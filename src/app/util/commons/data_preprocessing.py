from typing import List
from typing import Union

import pandas as pd


def select_datasets(data, sets=None):
    if isinstance(sets, list):
        return data[data.set.isin(sets)]
    elif isinstance(sets, str):
        return data[data.set == sets]
    else:
        return data


def select_features(data, features=None):
    if isinstance(features, list):
        return data[features]
    elif isinstance(features, str):
        return data[[features]]
    else:
        return data


def select_regions(data, regions=None):
    if isinstance(regions, list):
        return data[data.region.isin(regions)]
    elif isinstance(regions, str):
        return data[data.region == regions]
    else:
        return data


def select_models(data, models=None):
    if isinstance(models, list):
        return data[data.model.isin(models)]
    elif isinstance(models, str):
        return data[data.model == models]
    else:
        return data


def select_subjects(data, subjects=None):
    if isinstance(subjects, list):
        return data[data.ID.isin(subjects)]
    elif isinstance(subjects, str):
        return data[data.ID == subjects]
    else:
        return data


def filter_outliers(
        data: pd.DataFrame,
        filtering_method: str = None,
        filtering_feature: str = None,
        remove_low: float = None,
        remove_up: float = None,
        clip_low: float = None,
        clip_up: float = None,
        num_std_devs: int = None
):
    if filtering_method:
        mean, std_dev = data[filtering_feature].mean(), data[filtering_feature].std()
        if filtering_method == "Removing outliers":
            data = data[data[filtering_feature].between(remove_low, remove_up)]
        elif filtering_method == "Clipping outliers":
            data[filtering_feature] = data[filtering_feature].clip(clip_low, clip_up)
        elif filtering_method == "Standard deviations":
            upper_bound = mean + int(num_std_devs) * std_dev
            lower_bound = mean - int(num_std_devs) * std_dev
            data = data[data[filtering_feature].between(lower_bound, upper_bound)]

    return data


def processing_data(
        data: pd.DataFrame,
        sets: Union[List[str], str] = None,
        models: Union[List[str], str] = None,
        features: Union[List[str], str] = None,
        regions: Union[List[str], str] = None,
        subjects: Union[List[str], str] = None,
        filtering_method: str = None,
        filtering_feature: str = None,
        remove_low: float = None,
        remove_up: float = None,
        clip_low: float = None,
        clip_up: float = None,
        num_std_devs: int = None
):
    data = select_datasets(data, sets=sets)
    data = select_models(data, models=models)
    data = select_features(data, features=features)
    data = select_regions(data, regions=regions)
    data = select_subjects(data, subjects=subjects)
    data = filter_outliers(data, filtering_method, filtering_feature, remove_low, remove_up, clip_low, clip_up, num_std_devs)

    return data
