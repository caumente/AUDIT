import numpy as np
import pytest
import SimpleITK as sitk
from PIL import Image

from audit.io.readers import ArrayReader
from audit.io.readers import DicomSegReader
from audit.io.readers import DicomSeriesReader
from audit.io.readers import MhaReader
from audit.io.readers import NiftiReader
from audit.io.readers import NrrdReader
from audit.io.readers import RasterImageReader
from audit.io.readers import get_reader
from audit.io.readers import normalize_format
from audit.io.readers import read_subject_image
from audit.io.readers import resolve_configured_format


@pytest.mark.parametrize(
    ("format_name", "reader_type"),
    [
        (".nii.gz", NiftiReader),
        (".nrrd", NrrdReader),
        (".mha", MhaReader),
        (".png", RasterImageReader),
        (".npz", ArrayReader),
        ("dicom_series", DicomSeriesReader),
        ("dicom_seg", DicomSegReader),
    ],
)
def test_reader_registry(format_name, reader_type):
    assert isinstance(get_reader(format_name), reader_type)


def test_nifti_reader_preserves_spacing_in_numpy_axis_order(tmp_path):
    subject_id = "case"
    subject_dir = tmp_path / subject_id
    subject_dir.mkdir()
    array = np.zeros((3, 4, 5), dtype=np.uint8)
    image = sitk.GetImageFromArray(array)
    image.SetSpacing((0.5, 0.75, 2.0))
    sitk.WriteImage(image, str(subject_dir / f"{subject_id}_seg.nii.gz"))

    result = read_subject_image(str(tmp_path), subject_id, "_seg", ".nii.gz")

    np.testing.assert_array_equal(result.array, array)
    np.testing.assert_allclose(result.spacing, [2.0, 0.75, 0.5])


@pytest.mark.parametrize("extension", [".nrrd", ".mha"])
def test_simpleitk_file_readers_preserve_data_and_spacing(tmp_path, extension):
    subject_id = "case"
    subject_dir = tmp_path / subject_id
    subject_dir.mkdir()
    array = np.arange(24, dtype=np.uint8).reshape(2, 3, 4)
    image = sitk.GetImageFromArray(array)
    image.SetSpacing((0.4, 0.7, 1.5))
    sitk.WriteImage(image, str(subject_dir / f"{subject_id}_seg{extension}"))

    result = read_subject_image(str(tmp_path), subject_id, "_seg", extension)

    np.testing.assert_array_equal(result.array, array)
    np.testing.assert_allclose(result.spacing, [1.5, 0.7, 0.4])


def test_raster_reader_converts_rgb_to_luminance(tmp_path):
    subject_id = "case"
    subject_dir = tmp_path / subject_id
    subject_dir.mkdir()
    rgb = np.zeros((4, 5, 3), dtype=np.uint8)
    rgb[..., 1] = 255
    Image.fromarray(rgb).save(subject_dir / f"{subject_id}.png")

    result = read_subject_image(str(tmp_path), subject_id, "", ".png")

    assert result.array.shape == (4, 5)
    assert np.all(result.array > 0)
    np.testing.assert_array_equal(result.spacing, [1.0, 1.0])


def test_auto_format_discovers_raster_file(tmp_path):
    subject_id = "case"
    subject_dir = tmp_path / subject_id
    subject_dir.mkdir()
    Image.fromarray(np.ones((3, 4), dtype=np.uint8)).save(subject_dir / f"{subject_id}.jpeg")

    result = read_subject_image(str(tmp_path), subject_id, "", "auto")

    assert result.array.shape == (3, 4)


def test_raster_reader_accepts_physical_spacing(tmp_path):
    path = tmp_path / "image.png"
    Image.fromarray(np.ones((4, 5), dtype=np.uint8)).save(path)

    result = get_reader(".png").read(str(path), spacing=[0.3, 0.2])

    np.testing.assert_allclose(result.spacing, [0.3, 0.2])
    np.testing.assert_allclose(result.image.GetSpacing(), [0.2, 0.3])


def test_raster_reader_preserves_palette_label_indices(tmp_path):
    path = tmp_path / "mask.png"
    palette_mask = Image.fromarray(np.array([[0, 2], [2, 0]], dtype=np.uint8), mode="P")
    palette = [0] * (256 * 3)
    palette[6:9] = [255, 0, 0]
    palette_mask.putpalette(palette)
    palette_mask.save(path, bits=8)

    result = get_reader(".png").read(str(path))

    np.testing.assert_array_equal(result.array, [[0, 2], [2, 0]])


def test_array_reader_requires_key_for_multi_array_npz(tmp_path):
    path = tmp_path / "arrays.npz"
    np.savez(path, first=np.ones((2, 2)), second=np.zeros((2, 2)))

    with pytest.raises(ValueError, match="array_key"):
        get_reader(".npz").read(str(path))

    result = get_reader(".npz").read(str(path), array_key="second")
    np.testing.assert_array_equal(result.array, np.zeros((2, 2)))


def test_format_configuration_is_independent_from_modality():
    config = {
        "modality": "US",
        "formats": {"image": ".nrrd", "segmentation": ".mha", "prediction": ".npz"},
    }

    assert normalize_format(resolve_configured_format(config, "image", "US")) == "nrrd"
    assert normalize_format(resolve_configured_format(config, "segmentation", "US")) == "mha"
    assert normalize_format(resolve_configured_format(config, "prediction", "US")) == "array"
