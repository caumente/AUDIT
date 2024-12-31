


def health_checks(selected_sets, select_feature_names: list = []):
    if len(selected_sets) == 0:
        return False, "Please, select a dataset from the left sidebar."
    elif any(k is None for k in select_feature_names):
        return False, f'Please, select an available category.'
    else:
        return True, ''


def dataset_sanity_check(selected_sets):
    if len(selected_sets) == 0:
        return False
    else:
        return True


def models_sanity_check(baseline_model, benchmark_model):
    if baseline_model == benchmark_model:
        return False
    else:
        return True
