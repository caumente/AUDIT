import warnings

import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore", category=RuntimeWarning)

from src.app.util.commons.data_preprocessing import processing_data
from src.app.util.commons.sidebars import setup_sidebar_single_dataset
from src.app.util.commons.sidebars import setup_sidebar_single_subjects
from src.app.util.constants.descriptions import SubjectsExplorationPage
from src.app.util.constants.features import Features
from src.utils.commons.file_manager import load_config_file
from src.utils.commons.file_manager import read_datasets_from_dict
from src.utils.commons.strings import pretty_string

# Load constants
const_descriptions = SubjectsExplorationPage()
const_features = Features()

# Load configuration and data
config = load_config_file("./src/configs/app.yml")
features = config.get("features")


def setup_sidebar(data):
    with st.sidebar:
        st.header("Configuration")

        selected_set = setup_sidebar_single_dataset(data)
        selected_subject = setup_sidebar_single_subjects(data[data.set == selected_set])

    return selected_set, selected_subject


def table_feature(data, feature):
    feat_dict = const_features.get_features(feature)
    df_feat = data[data["feature"].isin(feat_dict.values())]
    df_feat["feature"] = df_feat["feature"].map(dict(zip(feat_dict.values(), feat_dict.keys())))

    return df_feat


def show_subject_information(data):
    st.subheader("Subject information")
    st.markdown("This section provides information of the chosen subject.")
    st.markdown(const_descriptions.features_explanation)

    # transposing features
    df = data.copy().transpose().reset_index()
    df.columns = ["feature", "value"]

    for f, c in zip(const_features.categories, st.columns(len(const_features.categories))):
        with c:
            st.markdown(f"#### {f} features")
            st.dataframe(table_feature(df, f).set_index("feature"), use_container_width=True)


def iqr_outliers_detector(data, subject, deviation=1.5):
    outliers_iqr = {}
    for c in data.columns:
        if c in const_features.get_multiple_features(const_features.categories).values():
            q1 = data[c].quantile(0.25)
            q3 = data[c].quantile(0.75)
            iqr = q3 - q1
            outliers_iqr[c] = (subject[c].values[0] < (q1 - deviation * iqr)) or (subject[c].values[0] > (q3 + deviation * iqr))

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


def show_outlier_information(subject_data, data):
    st.subheader("IQR outlier detection")
    st.markdown(const_descriptions.iqr_explanation)
    extreme = st.checkbox("Extreme outlier", value=False, help="If enabled, it looks for extreme outlier values.")
    deviation = 3 if extreme else 1.5
    outliers = iqr_outliers_detector(data, subject_data, deviation=deviation)
    if any(outliers["Is Outlier"]) > 0:
        st.write(outliers[outliers["Is Outlier"] == True].drop(columns=["Is Outlier"]))
    else:
        st.write("The subject is not an outlier for any of the features")


def subjects():
    # Load configuration and data
    st.header(const_descriptions.header)
    st.markdown(const_descriptions.sub_header)

    # Load datasets
    df = read_datasets_from_dict(features)

    # Set up sidebar options
    selected_set, selected_subject = setup_sidebar(df)

    # Filter subject info and remove the subject from the dataset for further analysis
    subject_data = processing_data(df, sets=selected_set, subjects=selected_subject)
    rest_data = df[(df.set == selected_set) & (df.ID != selected_subject)]

    # show main information for the selected subject
    show_subject_information(subject_data)

    # check whether the subject is an outlier or not
    show_outlier_information(subject_data, rest_data)