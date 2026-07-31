import os

import numpy as np
import streamlit as st
from stqdm import stqdm
from streamlit_theme import st_theme

from audit.app.util.commons.checks import none_check
from audit.app.util.constants.descriptions import SegmentationErrorMatrixPage
from audit.app.util.pages.base_page import BasePage
from audit.io.readers import resolve_configured_format
from audit.io.readers import resolve_reader_options
from audit.metrics.backends.commons import load_subject_data
from audit.metrics.error_matrix import errors_per_class
from audit.metrics.error_matrix import normalize_matrix_per_row
from audit.utils.modalities.factory import get_modality
from audit.visualization.commons import update_segmentation_matrix_plot
from audit.visualization.confusion_matrices import plt_confusion_matrix


class SegmentationErrorMatrix(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = SegmentationErrorMatrixPage()

    def run(self):
        theme = st_theme(key="matrix_theme")
        if theme is not None:
            self.template = theme.get("base")

        # Load configuration
        labels_dict = self.config.get("labels")
        predictions = self.config.get("predictions", {})
        raw_datasets = self.config.get("raw_datasets", {})
        modality_name = self.config.get("modality", "MRI")
        segmentation_format = resolve_configured_format(self.config, "segmentation", modality_name)
        prediction_format = resolve_configured_format(self.config, "prediction", modality_name)
        segmentation_reader_options = resolve_reader_options(self.config, "segmentation")
        prediction_reader_options = resolve_reader_options(self.config, "prediction")

        # Define page layout
        st.subheader(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)
        st.markdown(self.descriptions.description)

        proceed = none_check(labels=labels_dict, predictions=predictions, raw_datasets=raw_datasets)
        if proceed[0]:
            # Setup sidebar
            selected_dataset, selected_model, selected_id, gt_path, pred_path, subjects_in_path = self.setup_sidebar(
                predictions, raw_datasets
            )

            col1, col2 = st.columns([2, 2], gap="small")
            with col1:
                # Main visualization logic
                normalized = st.checkbox(
                    "Normalized per ground truth label",
                    value=True,
                    help="It normalizes the errors per class, if enabled.",
                )

                if selected_id == "All":
                    averaged = st.checkbox(
                        "Averaged per number of subjects",
                        value=True,
                        help="It averages the errors per number of subjects within the corresponding dataset, if enabled.",
                    )
            with col2:
                customization_matrix = st.selectbox(
                    label="Customize visualization",
                    options=["Standard visualization", "Custom visualization"],
                    index=0,
                    key="matrix",
                )

            if customization_matrix == "Custom visualization":
                col1, col2 = st.columns([4, 1], gap="small")
                with col1:
                    if selected_id == "All":
                        fig = self.visualize_aggregated(
                            gt_path,
                            pred_path,
                            subjects_in_path,
                            labels_dict,
                            averaged,
                            normalized,
                            modality_name,
                            segmentation_format,
                            prediction_format,
                            segmentation_reader_options,
                            prediction_reader_options,
                        )
                    else:
                        fig = self.visualize_subject_level(
                            gt_path,
                            pred_path,
                            selected_id,
                            labels_dict,
                            normalized,
                            modality_name,
                            segmentation_format,
                            prediction_format,
                            segmentation_reader_options,
                            prediction_reader_options,
                        )
                with col2:
                    update_segmentation_matrix_plot(fig, list(labels_dict.keys()), key="matrix")
                with col1:
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            else:
                if selected_id == "All":
                    fig = self.visualize_aggregated(
                        gt_path,
                        pred_path,
                        subjects_in_path,
                        labels_dict,
                        averaged,
                        normalized,
                        modality_name,
                        segmentation_format,
                        prediction_format,
                        segmentation_reader_options,
                        prediction_reader_options,
                    )
                else:
                    fig = self.visualize_subject_level(
                        gt_path,
                        pred_path,
                        selected_id,
                        labels_dict,
                        normalized,
                        modality_name,
                        segmentation_format,
                        prediction_format,
                        segmentation_reader_options,
                        prediction_reader_options,
                    )

                st.plotly_chart(fig, theme="streamlit", use_container_width=True)

            if selected_id != "All":
                # run itk-snap
                viewer_name = "ITK-SNAP" if modality_name.upper() == "MRI" else "modality viewer"
                visualize_itk = st.button(f"Visualize it in {viewer_name}")
                if visualize_itk:
                    try:
                        opened = get_modality(modality_name).run_comparison_segmentation_viewer(
                            gt_path, pred_path, selected_id, labels_dict
                        )
                        if not opened:
                            st.info(f"No external comparison viewer is configured for {modality_name}.")
                    except Exception:
                        st.error("Ups, something went wrong when opening the file in ITK-SNAP", icon="🚨")

    @staticmethod
    def setup_sidebar(predictions, raw_datasets):
        with st.sidebar:
            st.header("Configuration")

            # Dataset selection
            available_datasets = list(predictions.keys())
            selected_dataset = st.selectbox("Select the dataset to analyze", available_datasets, index=0)
            ground_truth_path = raw_datasets.get(selected_dataset)

            # Model selection
            available_models = list(predictions.get(selected_dataset).keys())
            selected_model = st.selectbox("Select the model to analyze", available_models, index=0)
            predictions_path = predictions.get(selected_dataset).get(selected_model)

            # Subject selection
            subjects_in_path = sorted([f.path.split("/")[-1] for f in os.scandir(ground_truth_path) if f.is_dir()])
            selected_id = st.selectbox("Select the subject ID to visualize", ["All"] + subjects_in_path, index=0)

        return selected_dataset, selected_model, selected_id, ground_truth_path, predictions_path, subjects_in_path

    @staticmethod
    def compute_confusion_matrix(seg, pred, labels, normalized):
        """
        Compute the confusion matrix for a single subject.

        Args:
            seg (np.array): Ground truth segmentation.
            pred (np.array): Predicted segmentation.
            labels (list): List of label values.
            normalized (bool): Whether to normalize the confusion matrix.

        Returns:
            np.array: Confusion matrix.
        """
        cm = errors_per_class(seg, pred, list(labels))
        if normalized:
            cm = normalize_matrix_per_row(cm)
        return cm

    @staticmethod
    def compute_accumulated_confusion_matrix(
        gt_path,
        predictions_path,
        subjects_in_path,
        labels,
        modality_name="MRI",
        segmentation_format=None,
        prediction_format=None,
        segmentation_reader_options=None,
        prediction_reader_options=None,
    ):
        """
        Compute the accumulated confusion matrix for all subjects.

        Args:
            gt_path (str): Path to ground truth data.
            predictions_path (str): Path to predictions data.
            subjects_in_path (list): List of subject IDs.
            labels (list): List of label values.

        Returns:
            np.array: Accumulated confusion matrix.
        """
        accumulated = None
        for subject_id in stqdm(
            subjects_in_path, desc=f"Calculating confusion matrix for {len(subjects_in_path)} subjects"
        ):
            seg, pred, _ = load_subject_data(
                gt_path,
                predictions_path,
                subject_id,
                modality_name=modality_name,
                ground_truth_format=segmentation_format,
                prediction_format=prediction_format,
                ground_truth_reader_options=segmentation_reader_options,
                prediction_reader_options=prediction_reader_options,
            )
            cm = errors_per_class(seg, pred, list(labels))
            if accumulated is None:
                accumulated = np.zeros_like(cm)
            accumulated += cm
        return accumulated

    def visualize_subject_level(
        self,
        gt_path,
        predictions_path,
        selected_id,
        labels_dict,
        normalized,
        modality_name="MRI",
        segmentation_format=None,
        prediction_format=None,
        segmentation_reader_options=None,
        prediction_reader_options=None,
    ):
        """
        Visualize the confusion matrix for a specific subject.

        Args:
            gt_path (str): Path to ground truth data.
            predictions_path (str): Path to predictions data.
            selected_id (str): Selected subject ID.
            labels_dict (dict): Dictionary mapping class names to label values.
            normalized (bool): Whether to normalize the confusion matrix.
        """
        classes, labels = list(labels_dict.keys()), list(labels_dict.values())
        seg, pred, _ = load_subject_data(
            gt_path,
            predictions_path,
            selected_id,
            modality_name=modality_name,
            ground_truth_format=segmentation_format,
            prediction_format=prediction_format,
            ground_truth_reader_options=segmentation_reader_options,
            prediction_reader_options=prediction_reader_options,
        )

        cm = self.compute_confusion_matrix(seg, pred, labels, normalized)
        fig = plt_confusion_matrix(cm, classes, theme=self.template, normalized=normalized)

        return fig

    def visualize_aggregated(
        self,
        gt_path,
        predictions_path,
        subjects_in_path,
        labels_dict,
        averaged,
        normalized,
        modality_name="MRI",
        segmentation_format=None,
        prediction_format=None,
        segmentation_reader_options=None,
        prediction_reader_options=None,
    ):
        """
        Visualize the accumulated confusion matrix for all subjects.

        Args:
            gt_path (str): Path to ground truth data.
            predictions_path (str): Path to predictions data.
            subjects_in_path (list): List of subject IDs.
            labels_dict (dict): Dictionary mapping class names to label values.
            averaged (bool): Whether to average the confusion matrix.
            normalized (bool): Whether to normalize the confusion matrix.
        """
        classes, labels = list(labels_dict.keys()), list(labels_dict.values())

        accumulated = self.compute_accumulated_confusion_matrix(
            gt_path,
            predictions_path,
            subjects_in_path,
            labels,
            modality_name,
            segmentation_format,
            prediction_format,
            segmentation_reader_options,
            prediction_reader_options,
        )

        if averaged:
            accumulated = (accumulated / len(subjects_in_path)).astype(int)
        if normalized:
            accumulated = normalize_matrix_per_row(accumulated)

        fig = plt_confusion_matrix(accumulated, classes, theme=self.template, normalized=normalized)

        return fig
