import os
from multiprocessing import Lock
from multiprocessing import Manager
from multiprocessing import Pool

import pandas as pd
from colorama import Fore
from loguru import logger

from audit.features.pipelines.factory import get_feature_pipeline
from audit.utils.commons.file_manager import list_dirs
from audit.utils.commons.strings import fancy_tqdm
from audit.utils.modalities.factory import get_modality


@logger.catch
def check_multiprocessing(config_file):
    cpu_cores = config_file.get("cpu_cores")

    if cpu_cores is None or cpu_cores == "None":
        logger.info("cpu_cores not specified or invalid in feature_extraction.yml file, defaulting to os.cpu_count()")
        cpu_cores = os.cpu_count()

    if not isinstance(cpu_cores, int) or cpu_cores <= 0:
        logger.info(
            f"Invalid cpu_cores value: {cpu_cores} in feature_extraction.yml file, defaulting to os.cpu_count()"
        )
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
    path_images = params.get("path_images")
    subject_id = params.get("subject_id")
    available_sequences = params.get("available_sequences")
    seq_reference = params.get("seq_reference")
    features_to_extract = params.get("features_to_extract")
    numeric_label = params.get("numeric_label")
    label_names = params.get("label_names")
    modality_name = params.get("modality", "MRI")
    spatial_features, tumor_features, stats_features, texture_feats = {}, {}, {}, {}

    modality = get_modality(modality_name)

    # read sequences and segmentation
    sequences = modality.read_sequences_dict(root_dir=path_images, subject_id=subject_id, sequences=available_sequences)

    # Try loading segmentation using default modality logic, or fallback to sequences if None provided
    seg_dict = modality.read_sequences_dict(root_dir=path_images, subject_id=subject_id, sequences=["_seg"])
    seg = seg_dict.get("seg")

    # calculating spacing
    # Retrieve reference sequence image for spacing
    ref_dict = (
        modality.read_sequences_dict(root_dir=path_images, subject_id=subject_id, sequences=[seq_reference])
        if seq_reference
        else None
    )

    # SimpleITK image proxy isn't returned by read_sequences_dict (it returns arrays),
    # so we'll build an image proxy from the array just to extract spacing if not supported natively.
    # More correct: Since get_spacing takes SimpleITK.Image, and read_sequences_dict returns np.ndarray,
    # we need to adapt here by loading it directly, or building it.

    # Since Modality handles spacing we need a proxy image
    try:
        ref_arr = (
            ref_dict.get(seq_reference.replace("_", ""))
            if ref_dict
            else next(iter(sequences.values()))
            if sequences
            else None
        )
        ref_img = modality.build_image(ref_arr) if ref_arr is not None else None
        sequences_spacing = modality.get_spacing(img=ref_img)
    except Exception:
        sequences_spacing = modality.get_spacing(img=None)

    try:
        seg_img = modality.build_image(seg) if seg is not None else None
        seg_spacing = modality.get_spacing(img=seg_img)
    except Exception:
        seg_spacing = modality.get_spacing(img=None)

    pipeline_class = get_feature_pipeline(modality_name)
    pipeline = pipeline_class(features_to_extract=features_to_extract, modality_name=modality_name, cpu_cores=cpu_cores)

    subject_info_df = pipeline.extract(
        subject_id=subject_id,
        sequences=sequences,
        segmentation=seg,
        sequences_spacing=sequences_spacing,
        seg_spacing=seg_spacing,
        seq_reference=seq_reference,
        numeric_label=numeric_label,
        label_names=label_names,
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
    modality_name = config_file.get("modality", "MRI")

    modality = get_modality(modality_name)
    available_sequences = config_file.get("sequences")
    if available_sequences is None:
        available_sequences = modality.get_default_sequences()

    seq_reference = available_sequences[0] if available_sequences else None

    subjects_list = list_dirs(path_images)
    cpu_cores = check_multiprocessing(config_file)

    data = pd.DataFrame()
    if cpu_cores == 1:
        with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
            for subject_id in subjects_list:
                logger.info(f"Processing subject: {subject_id}")

                # updating progress bar
                pbar.set_postfix_str(f"{Fore.CYAN}Current subject: {Fore.LIGHTBLUE_EX}{subject_id}{Fore.CYAN}")
                pbar.update(1)

                params = {
                    "path_images": path_images,
                    "subject_id": subject_id,
                    "label_names": label_names,
                    "numeric_label": numeric_label,
                    "seq_reference": seq_reference,
                    "features_to_extract": features_to_extract,
                    "available_sequences": available_sequences,
                    "modality": modality_name,
                }

                subject_info_df = process_subject(data, params, cpu_cores)
                data = pd.concat([data, subject_info_df], ignore_index=True)

        data = extract_longitudinal_info(config_file, data, dataset_name)

    if cpu_cores > 1:
        manager = Manager()
        shared_data = manager.dict()
        lock = Lock()

        with Pool(processes=cpu_cores, initializer=initializer, initargs=(shared_data, lock)) as pool:
            with fancy_tqdm(total=len(subjects_list), desc=f"{Fore.CYAN}Progress", leave=True) as pbar:
                results = []

                for subject_id in subjects_list:
                    params = {
                        "path_images": path_images,
                        "subject_id": subject_id,
                        "label_names": label_names,
                        "numeric_label": numeric_label,
                        "seq_reference": seq_reference,
                        "features_to_extract": features_to_extract,
                        "available_sequences": available_sequences,
                        "modality": modality_name,
                    }
                    results.append(pool.apply_async(process_subject, args=(shared_data, params, cpu_cores)))

                for result in results:
                    result.wait()
                    pbar.update(1)

        for subject_id, subject_info_df in shared_data.items():
            data = pd.concat([data, subject_info_df], ignore_index=True)

        data = data.sort_values(by=data.columns[0]).reset_index(drop=True)
        data = extract_longitudinal_info(config_file, data, dataset_name)

    data = load_and_merge_metadata(data, config_file, dataset_name)

    return data.sort_values(by="ID")


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

    longitudinal_global = config.get("longitudinal")

    # Check if the key exists but is empty/malformed
    if not longitudinal_global or not isinstance(longitudinal_global, dict):
        if "longitudinal" in config:
            logger.warning(
                "The 'longitudinal' key exists in the configuration but contains no valid data. Skipping longitudinal extraction."
            )
        df["longitudinal_id"] = ""
        df["time_point"] = 0
        return df

    longitudinal = longitudinal_global.get(dataset_name)

    if longitudinal and isinstance(longitudinal, dict):
        pattern = longitudinal.get("pattern")
        longitudinal_id = longitudinal.get("longitudinal_id")
        time_point = longitudinal.get("time_point")

        if pattern is not None and longitudinal_id is not None and time_point is not None:
            try:
                df[["longitudinal_id", "time_point"]] = (
                    df["ID"].str.split(pattern, expand=True).iloc[:, [longitudinal_id, time_point]]
                )
                df["time_point"] = df["time_point"].astype(int)
            except Exception as e:
                logger.error(f"Error parsing longitudinal info for {dataset_name} using pattern '{pattern}': {e}")
                df["longitudinal_id"] = ""
                df["time_point"] = 0
        else:
            logger.warning(
                f"Incomplete longitudinal configuration for dataset '{dataset_name}'. Missing 'pattern', 'longitudinal_id', or 'time_point'."
            )
            df["longitudinal_id"] = ""
            df["time_point"] = 0
    else:
        df["longitudinal_id"] = ""
        df["time_point"] = 0

    return df


def load_and_merge_metadata(data: pd.DataFrame, config_file: dict, dataset_name: str) -> pd.DataFrame:
    """
    Loads and merges metadata files associated with a given dataset, if available,
    and merges them with the provided DataFrame.

    Args:
        data (pd.DataFrame): Main dataframe containing extracted features.
        config_file (dict): Configuration dictionary, potentially containing a 'metadata' section.
        dataset_name (str): Name of the dataset currently being processed.

    Returns:
        pd.DataFrame: DataFrame merged with all metadata files for the given dataset.
    """
    metadata_section = config_file.get("metadata", {})
    if not metadata_section:
        logger.info("No metadata section found in the config file. Skipping metadata merge.")
        return data

    dataset_metadata = metadata_section.get(dataset_name)
    if not dataset_metadata:
        logger.info(f"No metadata found for dataset '{dataset_name}'. Skipping metadata merge.")
        return data

    logger.info(f"Found {len(dataset_metadata)} metadata file(s) for dataset '{dataset_name}'.")

    for meta_name, filepath in dataset_metadata.items():
        # Handle undefined or empty paths gracefully
        if not filepath or not isinstance(filepath, str) or filepath.strip() == "":
            logger.warning(
                f"Metadata entry '{meta_name}' for dataset '{dataset_name}' has no valid file path, skipping."
            )
            continue

        if not os.path.exists(filepath):
            logger.warning(f"Metadata file '{meta_name}' not found at: {filepath}")
            continue

        logger.info(f"Loading metadata '{meta_name}' from: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext in [".csv", ".tsv"]:
                sep = "," if ext == ".csv" else "\t"
                meta_df = pd.read_csv(filepath, sep=sep)
            elif ext in [".xlsx", ".xls"]:
                meta_df = pd.read_excel(filepath)
            else:
                logger.warning(f"Unsupported metadata format for '{filepath}', skipping.")
                continue
        except Exception as e:
            logger.error(f"Error reading metadata file '{filepath}': {e}")
            continue

        if "ID" not in meta_df.columns:
            logger.warning(f"Metadata file '{meta_name}' does not contain an 'ID' column. Skipping merge.")
            continue

        data = pd.merge(data, meta_df, on="ID", how="left")
        logger.info(f"Merged metadata '{meta_name}'.")

    return data
