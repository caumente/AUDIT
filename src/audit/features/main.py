import os

import pandas as pd
from colorama import Fore
from loguru import logger
from multiprocessing import Pool, Manager, Lock

from audit.features.spatial import SpatialFeatures
from audit.features.statistical import StatisticalFeatures
from audit.features.texture import TextureFeatures
from audit.features.tumor import TumorFeatures
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_tqdm
from audit.utils.sequences.sequences import get_spacing
from audit.utils.sequences.sequences import load_nii_by_subject_id
from audit.utils.sequences.sequences import read_sequences_dict


@logger.catch
def check_multiprocessing(config_file):
    cpu_cores = config_file.get("cpu_cores")

    if cpu_cores is None or cpu_cores == "None":
        logger.info("cpu_cores not specified or invalid in feature_extraction.yml file, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()

    if not isinstance(cpu_cores, int) or cpu_cores <= 0:
        logger.info(f"Invalid cpu_cores value: {cpu_cores} in feature_extraction.yml file, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()

    logger.info(f"Using {cpu_cores} CPU cores for processing")
    return cpu_cores


def initializer(shared_df, lock):
    """Initialize shared variables for multiprocessing"""
    global shared_dataframe, dataframe_lock
    shared_dataframe = shared_df
    dataframe_lock = lock


def process_subject(data: pd.DataFrame, params: dict, cpu_cores: int) -> pd.DataFrame:
    """Process a single subject to extract features"""
    path_images = params.get('path_images')
    subject_id = params.get('subject_id')
    available_sequences = params.get('available_sequences')
    seq_reference = params.get('seq_reference')
    features_to_extract = params.get('features_to_extract')
    numeric_label = params.get('numeric_label')
    label_names = params.get('label_names')
    spatial_features, tumor_features, stats_features, texture_feats = {}, {}, {}, {}

    # read sequences and segmentation
    sequences = read_sequences_dict(root_dir=path_images, subject_id=subject_id, sequences=available_sequences)
    seg = load_nii_by_subject_id(root_dir=path_images, subject_id=subject_id, as_array=True)

    # calculating spacing
    sequences_spacing = get_spacing(img=load_nii_by_subject_id(path_images, subject_id, seq_reference))
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

    # calculate spatial features (dimensions and center mass)
    if 'spatial' in features_to_extract:
        sf = SpatialFeatures(sequence=sequences.get(seq_reference.replace("_", "")), spacing=sequences_spacing)
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

    if cpu_cores == 1:
        return subject_info_df

    with dataframe_lock:
        data[subject_id] = subject_info_df

    return data


@logger.catch
def extract_features(path_images: str, config_file: dict, dataset_name: str) -> pd.DataFrame:
    """
    Extracts features from all the MRIs located in the specified directory and compiles them into a DataFrame.

    Args:
        path_images (str): The path to the directory containing subject image data.
        config_file (str): Config file 'feature_extraction.yml'
        dataset_name (str): Name of dataset being processed

    Returns:
        pd.DataFrame: A DataFrame containing extracted features for each subject, including spatial, tumor, and
                      statistical features.
    """
    # get configuration
    label_names, numeric_label = list(config_file["labels"].keys()), list(config_file["labels"].values())
    features_to_extract = [key for key, value in config_file["features"].items() if value]
    available_sequences = config_file.get("sequences")
    seq_reference = available_sequences[0]
    subjects_list = list_dirs(path_images)
    cpu_cores = check_multiprocessing(config_file)

    if cpu_cores == 1:
        data = pd.DataFrame()

        with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
            for subject_id in subjects_list:
                logger.info(f"Processing subject: {subject_id}")

                # updating progress bar
                pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                pbar.update(1)

                params = {
                    'path_images': path_images,
                    'subject_id': subject_id,
                    'label_names': label_names,
                    'numeric_label': numeric_label,
                    'seq_reference': seq_reference,
                    'features_to_extract': features_to_extract,
                    'available_sequences': available_sequences
                }

                subject_info_df = process_subject(data, params, cpu_cores)
                data = pd.concat([data, subject_info_df], ignore_index=True)

        data = extract_longitudinal_info(config_file, data, dataset_name)

        return data.sort_values(by="ID")

    if cpu_cores > 1:

        manager = Manager()
        shared_data = manager.dict()
        lock = Lock()

        with Pool(processes=cpu_cores, initializer=initializer, initargs=(shared_data, lock)) as pool:
            with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                results = []

                for subject_id in subjects_list:
                    params = {
                        'path_images': path_images,
                        'subject_id': subject_id,
                        'label_names': label_names,
                        'numeric_label': numeric_label,
                        'seq_reference': seq_reference,
                        'features_to_extract': features_to_extract,
                        'available_sequences': available_sequences
                    }
                    results.append(pool.apply_async(process_subject, args=(shared_data, params, cpu_cores)))

                for result in results:
                    result.wait()
                    pbar.update(1)

        data = pd.DataFrame()
        for subject_id, subject_info_df in shared_data.items():
            data = pd.concat([data, subject_info_df], ignore_index=True)

        data = data.sort_values(by=data.columns[0]).reset_index(drop=True)
        data = extract_longitudinal_info(config_file, data, dataset_name)

        return data.sort_values(by="ID")


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
