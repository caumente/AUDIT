import pandas as pd
from colorama import Fore
from loguru import logger

from src.features.spatial import SpatialFeatures
from src.features.statistical import StatisticalFeatures
from src.features.texture import TextureFeatures
from src.features.tumor import TumorFeatures
from src.utils.commons.file_manager import list_dirs
from src.utils.commons.strings import fancy_tqdm
from src.utils.sequences.sequences import get_spacing
from src.utils.sequences.sequences import load_nii_by_subject_id
from src.utils.sequences.sequences import read_sequences_dict


@logger.catch
def extract_features(path_images: str, config_file: dict, dataset_name: str) -> pd.DataFrame:
    """
    Extracts features from all the MRIs located in the specified directory and compiles them into a DataFrame.

    Args:
        path_images (str): The path to the directory containing subject image data.
        config_file (str): Config file 'feature_extractor.yml'
        dataset_name (str): Name of dataset being processed

    Returns:
        pd.DataFrame: A DataFrame containing extracted features for each subject, including spatial, tumor, and
                      statistical features.
    """
    # get configuration
    label_names, numeric_label = list(config_file["labels"].keys()), list(config_file["labels"].values())
    features_to_extract = [key for key, value in config_file["features"].items() if value]
    spatial_features, tumor_features, stats_features, texture_feats = {}, {}, {}, {}
    subjects_list = list_dirs(path_images)

    # loop over all the elements in the root folder
    data = pd.DataFrame()

    with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
        for n, subject_id in enumerate(subjects_list):
            logger.info(f"Processing subject: {subject_id}")

            # updating progress bar
            pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
            pbar.update(1)

            # read sequences and segmentation
            sequences = read_sequences_dict(root=path_images, subject_id=subject_id)
            seg = load_nii_by_subject_id(root=path_images, subject_id=subject_id, as_array=True)

            # calculating spacing
            sequences_spacing = get_spacing(img=load_nii_by_subject_id(path_images, subject_id, "_t1ce"))
            seg_spacing = get_spacing(img=load_nii_by_subject_id(path_images, subject_id, "_seg"))

            # extract first order (statistical) information from sequences
            if 'statistical' in features_to_extract:
                stats_features = {
                    key: StatisticalFeatures(seq[seq > 0]).extract_features()
                    for key, seq in sequences.items()
                    if seq is not None
                }

            # extract second order (texture) information from sequences
            if 'texture' in features_to_extract:
                texture_feats = {
                    key: TextureFeatures(seq, remove_empty_planes=True).extract_features()
                    for key, seq in sequences.items()
                    if seq is not None
                }

            # calculate spatial features (dimensions and brain center mass)
            if 'spatial' in features_to_extract:
                sf = SpatialFeatures(sequence=sequences.get("t1ce"), spacing=sequences_spacing)
                spatial_features = sf.extract_features()

            # calculate tumor features
            if 'tumor' in features_to_extract:
                tf = TumorFeatures(
                    segmentation=seg, spacing=seg_spacing, mapping_names=dict(zip(numeric_label, label_names))
                )
                tumor_features = tf.extract_features(sf.center_mass.values() if 'spatial' in features_to_extract else {})

            # Add info to the main df
            subject_info_df = store_subject_information(
                subject_id,
                spatial_features,
                tumor_features,
                stats_features,
                texture_feats
            )
            data = pd.concat([data, subject_info_df], ignore_index=True)

        data = extract_longitudinal_info(config_file, data, dataset_name)

        return data


def store_subject_information(
    subject_id: str,
    spatial_features: dict,
    tumor_features: dict,
    stats_features: dict,
    texture_feats: dict
) -> pd.DataFrame:
    """
    Stores the extracted features for a single subject in a DataFrame.

    Args:
        subject_id (str): The ID of the subject.
        spatial_features (dict): A dictionary containing spatial features extracted from the subject's images.
        tumor_features (dict): A dictionary containing tumor features extracted from the subject's segmentation.
        stats_features (dict): A dictionary containing statistical features extracted from the subject's images.
        texture_feats (dict): A dictionary containing texture features extracted from the subject's images.

    Returns:
        pd.DataFrame: A DataFrame with the subject's ID and all extracted features, structured as a single row.
    """

    # storing information about subject
    subject_info = {"ID": subject_id}

    # including spatial information
    subject_info.update(spatial_features)

    # including tumor information
    subject_info.update(tumor_features)

    # including stats information
    for seq, dict_stats in stats_features.items():
        prefixed_stats = {f"{seq}_{k}": v for k, v in dict_stats.items()}
        subject_info.update(prefixed_stats)

    # including texture information
    for seq, dict_stats in texture_feats.items():
        prefixed_textures = {f"{seq}_{k}": v for k, v in dict_stats.items()}
        subject_info.update(prefixed_textures)

    # from dict to dataframe
    subject_info_df = pd.DataFrame(subject_info, index=[0])

    return subject_info_df


def extract_longitudinal_info(config: dict, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """
    Extracts longitudinal information from the dataset based on the provided configuration.

    This function parses the subject IDs in the DataFrame (`df`) to extract longitudinal identifiers
    and time points. It uses a regular expression pattern defined in the `config` to split the subject
    ID and populate the DataFrame with `longitudinal_id` and `time_point` columns. If no longitudinal
    configuration is found for the specified `dataset_name`, it defaults the `longitudinal_id` to an
    empty string and `time_point` to 0.

    Args:
        config (dict): Configuration dictionary containing longitudinal extraction parameters.
                       It should contain a `longitudinal` field with patterns and column indices.
        df (pd.DataFrame): The DataFrame containing subject IDs under the "ID" column.
        dataset_name (str): The name of the dataset, used to lookup longitudinal configuration.

    Returns:
        pd.DataFrame: The updated DataFrame with new columns `longitudinal_id` and `time_point`.
    """

    longitudinal = config.get("longitudinal", {}).get(dataset_name, None)
    if longitudinal:
        pattern = longitudinal.get("pattern")
        longitudinal_id = longitudinal.get("longitudinal_id")
        time_point = longitudinal.get("time_point")
        df[["longitudinal_id", "time_point"]] = (
            df["ID"].str.split(pattern, expand=True).iloc[:, [longitudinal_id, time_point]]
        )
        df["time_point"] = df["time_point"].astype(int)
    else:
        df["longitudinal_id"] = ""
        df["time_point"] = 0

    return df
