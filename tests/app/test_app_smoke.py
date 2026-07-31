import numpy as np
import pandas as pd
import pytest
import SimpleITK as sitk
from PIL import Image
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    "config_path",
    [
        "./configs/app.yml",
        "./configs/examples/curated_busi/app.yml",
    ],
)
def test_app_home_loads_for_mri_and_us(config_path, monkeypatch, tmp_path):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    script = (
        "from audit.app.APP import AUDIT\n"
        "from audit.utils.internal._config_helpers import load_config_file\n"
        f"AUDIT(load_config_file({config_path!r})).run()\n"
    )

    app = AppTest.from_string(script).run(timeout=30)

    assert not app.exception
    assert [title.value for title in app.title] == ["Welcome to AUDIT"]


@pytest.mark.parametrize(
    ("modality", "format_name", "label"),
    [
        ("MRI", ".nii.gz", 1),
        ("US", ".png", 255),
    ],
)
def test_segmentation_error_page_loads_format_aware_data(modality, format_name, label, tmp_path, monkeypatch):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    ground_truth = tmp_path / "ground_truth"
    prediction = tmp_path / "prediction"
    subject_id = "case"
    for root in (ground_truth, prediction):
        (root / subject_id).mkdir(parents=True)

    shape = (3, 4, 5) if modality == "MRI" else (6, 7)
    mask = np.zeros(shape, dtype=np.uint8)
    mask[(slice(1, -1),) * mask.ndim] = label
    if modality == "MRI":
        sitk.WriteImage(
            sitk.GetImageFromArray(mask),
            str(ground_truth / subject_id / f"{subject_id}_seg{format_name}"),
        )
        sitk.WriteImage(
            sitk.GetImageFromArray(mask),
            str(prediction / subject_id / f"{subject_id}_pred{format_name}"),
        )
        sequences = ["_t1"]
    else:
        Image.fromarray(mask).save(ground_truth / subject_id / f"{subject_id}_seg{format_name}")
        Image.fromarray(mask).save(prediction / subject_id / f"{subject_id}_pred{format_name}")
        sequences = []

    config = {
        "modality": modality,
        "formats": {
            "image": format_name,
            "segmentation": format_name,
            "prediction": format_name,
        },
        "sequences": sequences,
        "labels": {"BKG": 0, "TUMOR": label},
        "raw_datasets": {"dataset": str(ground_truth)},
        "predictions": {"dataset": {"model": str(prediction)}},
    }
    script = f"from audit.app.APP import AUDIT\nAUDIT({config!r}).run()\n"
    app = AppTest.from_string(script).run(timeout=30)

    app.sidebar.selectbox[0].select("Segmentation error matrix").run(timeout=30)

    assert not app.exception
    assert [subtitle.value for subtitle in app.subheader] == ["Segmentation Error Matrix"]


@pytest.mark.parametrize(
    ("modality", "labels", "sequences"),
    [
        ("MRI", {"BKG": 0, "TUMOR": 1}, ["_t1"]),
        ("US", {"BKG": 0, "TUMOR": 255}, []),
    ],
)
def test_multi_model_page_loads_for_mri_and_us(modality, labels, sequences, monkeypatch, tmp_path):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    metrics_path = tmp_path / "metrics.csv"
    pd.DataFrame(
        {
            "ID": ["case-1", "case-2", "case-1", "case-2"],
            "region": ["TUMOR"] * 4,
            "model": ["model-a", "model-a", "model-b", "model-b"],
            "dice": [0.8, 0.9, 0.7, 0.85],
        }
    ).to_csv(metrics_path, index=False)
    config = {
        "modality": modality,
        "formats": {"image": ".nii.gz" if modality == "MRI" else ".png"},
        "sequences": sequences,
        "labels": labels,
        "metrics": {"dataset": str(metrics_path)},
    }
    script = (
        "from unittest.mock import patch\n"
        "from audit.app.APP import AUDIT\n"
        f"config = {config!r}\n"
        "with patch('audit.app.util.pages.multi_model_performance.download_plot'):\n"
        "    AUDIT(config).run()\n"
    )

    app = AppTest.from_string(script).run(timeout=30)
    app.sidebar.selectbox[0].select("Multi-model performance").run(timeout=30)

    assert not app.exception
    assert [subtitle.value for subtitle in app.subheader] == ["Multi-model performance comparison"]
