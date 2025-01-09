import os

import numpy as np
import streamlit as st
from numpy.ma.extras import average
from stqdm import stqdm

from audit.app.util.constants.descriptions import SegmentationErrorMatrixPage
from audit.metrics.error_matrix import errors_per_class, normalize_matrix_per_row
from audit.utils.external_tools.itk_snap import run_comparison_segmentation_itk_snap
from audit.utils.sequences.sequences import load_nii_by_subject_id
from audit.visualization.confusion_matrices import plt_confusion_matrix_plotly

# Load constants
const_descriptions = SegmentationErrorMatrixPage()


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


def visualize_confusion_matrix(cm, classes, normalized):
    """
    Visualize the confusion matrix using Plotly.

    Args:
        cm (np.array): Confusion matrix.
        classes (list): List of class labels.
        normalized (bool): Whether the confusion matrix is normalized.
    """
    fig = plt_confusion_matrix_plotly(cm, classes, normalized)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


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


def compute_accumulated_confusion_matrix(gt_path, predictions_path, subjects_in_path, labels):
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
    for subject_id in stqdm(subjects_in_path, desc=f"Calculating confusion matrix for {len(subjects_in_path)} subjects"):
        seg = load_nii_by_subject_id(root=gt_path, subject_id=subject_id, seq="_seg", as_array=True)
        pred = load_nii_by_subject_id(root=predictions_path, subject_id=subject_id, seq="_pred", as_array=True)
        cm = errors_per_class(seg, pred, list(labels))
        if accumulated is None:
            accumulated = np.zeros_like(cm)
        accumulated += cm
    return accumulated


def visualize_subject_level(gt_path, predictions_path, selected_id, labels_dict, normalized):
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
    seg = load_nii_by_subject_id(root=gt_path, subject_id=selected_id, seq="_seg", as_array=True)
    pred = load_nii_by_subject_id(root=predictions_path, subject_id=selected_id, seq="_pred", as_array=True)

    cm = compute_confusion_matrix(seg, pred, labels, normalized)
    visualize_confusion_matrix(cm, classes, normalized)

    # run itk-snap
    visualize_itk = st.button("Visualize it in ITK-SNAP")
    if visualize_itk:
        run_comparison_segmentation_itk_snap(gt_path, predictions_path, selected_id, labels_dict)


def visualize_aggregated(gt_path, predictions_path, subjects_in_path, labels_dict, averaged, normalized):
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

    accumulated = compute_accumulated_confusion_matrix(gt_path, predictions_path, subjects_in_path, labels)

    if averaged:
        accumulated = (accumulated / len(subjects_in_path)).astype(int)
    if normalized:
        accumulated = normalize_matrix_per_row(accumulated)

    visualize_confusion_matrix(accumulated, classes, normalized)


def matrix(config):
    """
    Main function for the Segmentation Error Matrix page.

    Args:
        config (dict): Configuration dictionary with labels, predictions, and raw dataset paths.
    """
    # Load configuration
    labels_dict = config.get("labels")
    predictions = config.get("predictions", {})
    raw_datasets = config.get("raw_datasets", {})

    # Define page layout
    st.subheader(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)
    st.markdown(const_descriptions.description)

    # Setup sidebar
    selected_dataset, selected_model, selected_id, gt_path, pred_path, subjects_in_path = setup_sidebar(predictions, raw_datasets)

    # Main visualization logic
    normalized = st.checkbox(
        "Normalized per ground truth label",
        value=True,
        help="It normalizes the errors per class, if enabled."
    )

    if selected_id == "All":
        averaged = st.checkbox(
            "Averaged per number of subjects",
            value=True,
            help="It averages the errors per number of subjects within the corresponding dataset, if enabled.",
        )
        visualize_aggregated(gt_path, pred_path, subjects_in_path, labels_dict, averaged, normalized)
    else:
        visualize_subject_level(gt_path, pred_path, selected_id, labels_dict, normalized)

