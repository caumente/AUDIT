import warnings

import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore", category=RuntimeWarning)

from audit.app.util.commons.data_preprocessing import processing_data
from audit.app.util.constants.descriptions import SubjectsExplorationPage
from audit.app.util.pages.base_page import BasePage
from audit.utils.commons.strings import pretty_string
from audit.utils.internal._csv_helpers import read_datasets_from_dict


class SubjectsExploration(BasePage):
    def __init__(self, config):
        super().__init__(config)
        self.descriptions = SubjectsExplorationPage()

    def run(self):
        # Load configuration and data
        features = self.config.get("features")

        # Load configuration and data
        st.header(self.descriptions.header)
        st.markdown(self.descriptions.sub_header)

        # Load datasets
        df = read_datasets_from_dict(features)

        # Set up sidebar options
        selected_set, selected_subject = self.setup_sidebar(df)

        # Filter subject info and remove the subject from the dataset for further analysis
        subject_data = processing_data(df, sets=selected_set, subjects=selected_subject)
        rest_data = df[(df.set == selected_set) & (df.ID != selected_subject)]

        # show main information for the selected subject
        self.show_subject_information(subject_data)

        # check whether the subject is an outlier or not
        try:
            self.show_outlier_information(subject_data, rest_data)
        except TypeError:
            st.error(
                "Ups, something went wrong when searching for outliers. Please, make sure that all your metadata "
                "columns are numeric, otherwise it is not possible to run the algorithm",
                icon="🚨",
            )

    def setup_sidebar(self, data):
        with st.sidebar:
            st.header("Configuration")

            selected_set = self.sidebar.setup_sidebar_single_dataset(data)
            selected_subject = self.sidebar.setup_sidebar_single_subjects(data[data.set == selected_set])

        return selected_set, selected_subject

    def table_feature(self, data, feature):
        feat_dict = self.features.get_features(feature)
        df_feat = data[data["feature"].isin(feat_dict.values())]
        df_feat["feature"] = df_feat["feature"].map(dict(zip(feat_dict.values(), feat_dict.keys())))

        return df_feat

    def show_subject_information(self, data):
        st.subheader("Subject information")
        st.markdown("This section provides information of the chosen subject.")
        st.markdown(self.descriptions.features_explanation)

        # transposing features
        df = data.copy().transpose().reset_index()
        df.columns = ["feature", "value"]

        for f, c in zip(self.features.categories, st.columns(len(self.features.categories))):
            with c:
                st.markdown(f"#### {f} features")
                st.dataframe(self.table_feature(df, f).set_index("feature"), use_container_width=True)

    def iqr_outliers_detector(self, data, subject, deviation=1.5):
        outliers_iqr = {}
        for c in data.columns:
            if c in self.features.get_multiple_features(self.features.categories).values():
                q1 = data[c].quantile(0.25)
                q3 = data[c].quantile(0.75)
                iqr = q3 - q1
                outliers_iqr[c] = (subject[c].values[0] < (q1 - deviation * iqr)) or (
                    subject[c].values[0] > (q3 + deviation * iqr)
                )

        median = [f"{data[c].median():.2f}" for c in outliers_iqr.keys()]
        mean_std_combined = [f"{data[c].mean():.2f} ± {data[c].std():.2f}" for c in outliers_iqr.keys()]

        outliers_df = pd.DataFrame(
            {
                "Feature": list(outliers_iqr.keys()),
                "Is Outlier": list(outliers_iqr.values()),
                # 'Mean (Dataset)': [data[c].mean() for c in outliers_iqr.keys()],
                # 'Std Dev (Dataset)': [data[c].std() for c in outliers_iqr.keys()],
                "Median (Dataset)": median,
                "Mean ± Std (Dataset)": mean_std_combined,
                "Subject": [f"{subject[c].values[0]:.2f}" for c in outliers_iqr.keys()],
            }
        )

        outliers_df["Feature"] = outliers_df.Feature.map(pretty_string)
        outliers_df = outliers_df.set_index("Feature")

        return outliers_df

    def show_outlier_information(self, subject_data, data):
        st.subheader("IQR outlier detection")
        st.markdown(self.descriptions.iqr_explanation)
        extreme = st.checkbox("Extreme outlier", value=False, help="If enabled, it looks for extreme outlier values.")
        deviation = 3 if extreme else 1.5
        outliers = self.iqr_outliers_detector(data, subject_data, deviation=deviation)
        if any(outliers["Is Outlier"]) > 0:
            st.write(outliers[outliers["Is Outlier"] == True].drop(columns=["Is Outlier"]))
        else:
            st.write("The subject is not an outlier for any of the features")
