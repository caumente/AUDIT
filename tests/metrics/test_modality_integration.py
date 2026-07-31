import numpy as np
import pymia.evaluation.evaluator as eval_
import pytest
import SimpleITK as sitk
from PIL import Image

from audit.app.util.constants.features import Features
from audit.features.main import process_subject as process_feature_subject
from audit.metrics.backends.audit.audit import process_subject as process_metric_subject
from audit.metrics.backends.commons import load_subject_data
from audit.metrics.backends.metrics_reloaded.metrics_reloaded import process_subject_metricsreloaded
from audit.metrics.backends.pymia.pymia import aggregate_results
from audit.metrics.backends.pymia.pymia import instantiate_pymia_metrics
from audit.metrics.backends.pymia.pymia import perform_evaluation
from audit.metrics.error_matrix import errors_per_class


def _write_mri_case(root, subject_id, image, segmentation, spacing):
    subject_dir = root / subject_id
    subject_dir.mkdir(parents=True)
    for suffix, array in (("_t1", image), ("_seg", segmentation)):
        itk_image = sitk.GetImageFromArray(array)
        itk_image.SetSpacing(tuple(spacing[::-1]))
        sitk.WriteImage(itk_image, str(subject_dir / f"{subject_id}{suffix}.nii.gz"))


def _write_us_case(root, subject_id, image, segmentation):
    subject_dir = root / subject_id
    subject_dir.mkdir(parents=True)
    Image.fromarray(image).save(subject_dir / f"{subject_id}.png")
    Image.fromarray(segmentation).save(subject_dir / f"{subject_id}_seg.png")


@pytest.fixture
def modality_cases(tmp_path):
    image_mri = np.arange(1, 4 * 5 * 6 + 1, dtype=np.uint8).reshape(4, 5, 6)
    seg_mri = np.zeros_like(image_mri)
    seg_mri[1:3, 1:4, 2:5] = 2
    mri_gt = tmp_path / "mri_gt"
    mri_pred = tmp_path / "mri_pred"
    _write_mri_case(mri_gt, "mri_case", image_mri, seg_mri, np.array([2.0, 0.75, 0.5]))
    _write_mri_case(mri_pred, "mri_case", image_mri, seg_mri, np.array([2.0, 0.75, 0.5]))
    (mri_pred / "mri_case" / "mri_case_seg.nii.gz").rename(mri_pred / "mri_case" / "mri_case_pred.nii.gz")

    image_us = np.arange(1, 8 * 10 + 1, dtype=np.uint8).reshape(8, 10)
    seg_us = np.zeros_like(image_us)
    seg_us[2:6, 3:8] = 255
    us_gt = tmp_path / "us_gt"
    us_pred = tmp_path / "us_pred"
    _write_us_case(us_gt, "us_case", image_us, seg_us)
    _write_us_case(us_pred, "us_case", image_us, seg_us)
    (us_pred / "us_case" / "us_case_seg.png").rename(us_pred / "us_case" / "us_case_pred.png")

    return {
        "MRI": {
            "gt": str(mri_gt),
            "pred": str(mri_pred),
            "subject": "mri_case",
            "format": ".nii.gz",
            "sequences": ["_t1"],
            "labels": [0, 2],
            "label_names": ["BKG", "TUMOR"],
            "spacing": np.array([2.0, 0.75, 0.5]),
        },
        "US": {
            "gt": str(us_gt),
            "pred": str(us_pred),
            "subject": "us_case",
            "format": ".png",
            "sequences": [],
            "labels": [0, 255],
            "label_names": ["BKG", "TUMOR"],
            "spacing": np.array([1.0, 1.0]),
        },
    }


@pytest.mark.parametrize("modality_name", ["MRI", "US"])
def test_feature_pipeline_and_app_catalog_agree(modality_cases, modality_name):
    case = modality_cases[modality_name]
    params = {
        "path_images": case["gt"],
        "subject_id": case["subject"],
        "available_sequences": case["sequences"],
        "seq_reference": case["sequences"][0] if case["sequences"] else None,
        "numeric_label": case["labels"],
        "label_names": case["label_names"],
        "features_to_extract": ["statistical", "texture", "spatial", "tumor"],
        "modality": modality_name,
        "image_format": case["format"],
        "segmentation_format": case["format"],
    }

    result = process_feature_subject(None, params, 1)
    config = {
        "modality": modality_name,
        "sequences": case["sequences"],
        "labels": dict(zip(case["label_names"], case["labels"])),
    }
    expected = set(Features(config).get_multiple_features(["Statistical", "Texture", "Spatial", "Tumor"]).values())

    assert expected == set(result.columns) - {"ID"}
    assert result.loc[0, "lesion_size_tumor"] > 0


def test_us_preprocessing_options_are_applied(modality_cases):
    case = modality_cases["US"]
    params = {
        "path_images": case["gt"],
        "subject_id": case["subject"],
        "available_sequences": [],
        "seq_reference": None,
        "numeric_label": case["labels"],
        "label_names": case["label_names"],
        "features_to_extract": ["statistical"],
        "modality": "US",
        "image_format": ".png",
        "segmentation_format": ".png",
        "preprocessing_options": {"normalize": True},
    }

    result = process_feature_subject(None, params, 1)

    assert result.loc[0, "min_intensity"] < 0.1
    assert result.loc[0, "max_intensity"] == pytest.approx(1.0)


@pytest.mark.parametrize("modality_name", ["MRI", "US"])
def test_canonical_metrics_are_perfect_for_both_modalities(modality_cases, modality_name):
    case = modality_cases[modality_name]
    params = {
        "path_ground_truth_dataset": case["gt"],
        "path_predictions": case["pred"],
        "numeric_label": case["labels"],
        "subject_id": case["subject"],
        "label_names": case["label_names"],
        "metrics_to_extract": [
            "dice",
            "jaccard",
            "accuracy",
            "precision",
            "sensitivity",
            "specificity",
            "hausdorff_distance",
            "predicted_size",
        ],
        "model_name": "perfect",
        "modality": modality_name,
        "ground_truth_format": case["format"],
        "prediction_format": case["format"],
    }

    audit_result = process_metric_subject(None, params, 1).iloc[0]
    reloaded_params = {
        **params,
        "metrics_to_extract": [
            "dsc",
            "iou",
            "accuracy",
            "ppv",
            "sensitivity",
            "specificity",
            "hd",
            "numb_pred",
        ],
    }
    reloaded_result = process_subject_metricsreloaded(None, reloaded_params, 1).set_index("metric")["value"]
    pymia_metrics = [
        "dice",
        "jacc",
        "accu",
        "prec",
        "sens",
        "spec",
        "haus",
        "pred_vol",
    ]
    evaluator = eval_.SegmentationEvaluator(
        instantiate_pymia_metrics(pymia_metrics),
        {case["labels"][1]: case["label_names"][1]},
    )
    perform_evaluation(
        evaluator,
        case["gt"],
        case["pred"],
        case["subject"],
        modality_name,
        case["format"],
        case["format"],
    )
    pymia_result = {item["metric"]: item["value"] for item in aggregate_results(evaluator, params["model_name"])}

    equivalent_metrics = {
        "dice": ("dice", "dsc"),
        "jaccard": ("jacc", "iou"),
        "accuracy": ("accu", "accuracy"),
        "precision": ("prec", "ppv"),
        "sensitivity": ("sens", "sensitivity"),
        "specificity": ("spec", "specificity"),
    }
    for audit_name, (pymia_name, reloaded_name) in equivalent_metrics.items():
        assert audit_result[audit_name] == pytest.approx(1.0)
        assert reloaded_result[reloaded_name] == pytest.approx(1.0)
        assert pymia_result[pymia_name] == pytest.approx(1.0)
    assert audit_result["hausdorff_distance"] == pytest.approx(0.0)
    assert reloaded_result["hd"] == pytest.approx(0.0)
    assert pymia_result["haus"] == pytest.approx(0.0)
    assert audit_result["predicted_size"] == pytest.approx(pymia_result["pred_vol"])
    assert audit_result["predicted_size"] == pytest.approx(reloaded_result["numb_pred"] * case["spacing"].prod())


@pytest.mark.parametrize("modality_name", ["MRI", "US"])
def test_error_matrix_uses_common_format_aware_loader(modality_cases, modality_name):
    case = modality_cases[modality_name]
    ground_truth, prediction, spacing = load_subject_data(
        case["gt"],
        case["pred"],
        case["subject"],
        modality_name,
        case["format"],
        case["format"],
    )

    matrix = errors_per_class(ground_truth, prediction, case["labels"])

    assert matrix.shape == (2, 2)
    assert matrix.sum() == 0
    np.testing.assert_allclose(spacing, case["spacing"])


def test_error_matrix_rejects_missing_images():
    with pytest.raises(ValueError, match="required"):
        errors_per_class(None, None, [0, 1])


def test_metric_loader_rejects_spacing_mismatch(tmp_path):
    ground_truth = tmp_path / "gt"
    prediction = tmp_path / "pred"
    array = np.ones((2, 3, 4), dtype=np.uint8)
    _write_mri_case(ground_truth, "case", array, array, np.array([1.0, 1.0, 1.0]))
    _write_mri_case(prediction, "case", array, array, np.array([2.0, 1.0, 1.0]))
    (prediction / "case" / "case_seg.nii.gz").rename(prediction / "case" / "case_pred.nii.gz")

    with pytest.raises(ValueError, match="Spacing mismatch"):
        load_subject_data(str(ground_truth), str(prediction), "case", "MRI", ".nii.gz", ".nii.gz")


def test_empty_label_semantics_agree_between_backends(modality_cases):
    case = modality_cases["US"]
    metrics = [
        "dice",
        "jaccard",
        "accuracy",
        "precision",
        "sensitivity",
        "specificity",
        "hausdorff_distance",
        "predicted_size",
    ]
    params = {
        "path_ground_truth_dataset": case["gt"],
        "path_predictions": case["pred"],
        "numeric_label": [0, 255, 128],
        "subject_id": case["subject"],
        "label_names": ["BKG", "TUMOR", "ABSENT"],
        "metrics_to_extract": metrics,
        "model_name": "perfect",
        "modality": "US",
        "ground_truth_format": ".png",
        "prediction_format": ".png",
    }

    audit = process_metric_subject(None, params, 1).set_index("region").loc["ABSENT", metrics]
    reloaded_params = {
        **params,
        "metrics_to_extract": [
            "dsc",
            "iou",
            "accuracy",
            "ppv",
            "sensitivity",
            "specificity",
            "hd",
            "numb_pred",
        ],
    }
    reloaded_rows = process_subject_metricsreloaded(None, reloaded_params, 1)
    reloaded = reloaded_rows[reloaded_rows["region"] == "ABSENT"].set_index("metric")["value"]
    pymia_metrics = [
        "dice",
        "jacc",
        "accu",
        "prec",
        "sens",
        "spec",
        "haus",
        "pred_vol",
    ]
    evaluator = eval_.SegmentationEvaluator(instantiate_pymia_metrics(pymia_metrics), {128: "ABSENT"})
    perform_evaluation(evaluator, case["gt"], case["pred"], case["subject"], "US", ".png", ".png")
    pymia = {item["metric"]: item["value"] for item in aggregate_results(evaluator, "perfect")}

    expected = {
        "dice": 1.0,
        "jaccard": 1.0,
        "accuracy": 1.0,
        "precision": 0.0,
        "specificity": 1.0,
        "hausdorff_distance": 0.0,
        "predicted_size": 0.0,
    }
    equivalents = {
        "dice": ("dice", "dsc"),
        "jaccard": ("jacc", "iou"),
        "accuracy": ("accu", "accuracy"),
        "precision": ("prec", "ppv"),
        "specificity": ("spec", "specificity"),
        "hausdorff_distance": ("haus", "hd"),
        "predicted_size": ("pred_vol", "numb_pred"),
    }
    for audit_name, value in expected.items():
        pymia_name, reloaded_name = equivalents[audit_name]
        assert audit[audit_name] == pytest.approx(value)
        assert reloaded[reloaded_name] == pytest.approx(value)
        assert pymia[pymia_name] == pytest.approx(value)
    assert np.isnan(audit["sensitivity"])
    assert np.isnan(reloaded["sensitivity"])
    assert np.isnan(pymia["sens"])
