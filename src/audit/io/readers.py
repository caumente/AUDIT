"""Format-specific image readers.

The reader layer is deliberately independent from imaging modality.  A NIfTI
file can contain MRI, CT, PET, or a segmentation; conversely an ultrasound
image can be stored as raster, DICOM, NRRD, or a NumPy array.
"""

from __future__ import annotations

import os
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Optional

import numpy as np
import SimpleITK as sitk
from PIL import Image


@dataclass(frozen=True)
class ImageData:
    """An image array together with the metadata required downstream."""

    array: np.ndarray
    spacing: np.ndarray
    path: str
    image: Optional[sitk.Image] = None


def _spacing_for_array(image: sitk.Image, ndim: int) -> np.ndarray:
    """Return SimpleITK spacing ordered like NumPy axes."""
    spacing = np.asarray(image.GetSpacing(), dtype=float)[::-1]
    if spacing.size < ndim:
        spacing = np.pad(spacing, (ndim - spacing.size, 0), constant_values=1.0)
    return spacing[-ndim:]


def _from_sitk(image: sitk.Image, path: str) -> ImageData:
    array = sitk.GetArrayFromImage(image)
    return ImageData(array=array, spacing=_spacing_for_array(image, array.ndim), path=str(path), image=image)


class ImageReader(ABC):
    """Base contract implemented by every storage-format reader."""

    extensions: tuple[str, ...] = ()

    @abstractmethod
    def read(self, path: str, **kwargs: Any) -> ImageData:
        """Read ``path`` and preserve all available metadata."""


class SimpleITKFileReader(ImageReader):
    """Reader for scalar image files handled natively by SimpleITK."""

    def read(self, path: str, **kwargs: Any) -> ImageData:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image file does not exist: {path}")
        return _from_sitk(sitk.ReadImage(str(path)), path)


class NiftiReader(SimpleITKFileReader):
    extensions = (".nii.gz", ".nii")


class NrrdReader(SimpleITKFileReader):
    extensions = (".nrrd",)


class MhaReader(SimpleITKFileReader):
    extensions = (".mha", ".mhd")


class RasterImageReader(ImageReader):
    extensions = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")

    def read(self, path: str, **kwargs: Any) -> ImageData:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image file does not exist: {path}")

        with Image.open(path) as source:
            # Preserve indexed masks. For true colour input, PIL's luminance
            # transform is preferable to silently selecting one RGB channel.
            if source.mode == "P":
                array = np.asarray(source)
            elif source.mode in {"1", "L", "I", "I;16", "F"}:
                array = np.asarray(source)
            elif kwargs.get("grayscale", True):
                array = np.asarray(source.convert("L"))
            else:
                array = np.asarray(source)

        spacing = np.asarray(kwargs.get("spacing", np.ones(array.ndim)), dtype=float)
        if spacing.size != array.ndim:
            raise ValueError(f"Configured spacing {spacing.tolist()} does not match {array.ndim}D raster {path}.")
        image = sitk.GetImageFromArray(array)
        image.SetSpacing(tuple(spacing[::-1]))
        return ImageData(array=array, spacing=spacing, path=str(path), image=image)


class ArrayReader(ImageReader):
    extensions = (".npy", ".npz")

    def read(self, path: str, **kwargs: Any) -> ImageData:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Array file does not exist: {path}")

        loaded = np.load(path, allow_pickle=False)
        if isinstance(loaded, np.lib.npyio.NpzFile):
            key = kwargs.get("array_key")
            if key is None:
                if len(loaded.files) != 1:
                    loaded.close()
                    raise ValueError(
                        f"NPZ file {path} contains {len(loaded.files)} arrays; configure 'array_key' explicitly."
                    )
                key = loaded.files[0]
            if key not in loaded.files:
                loaded.close()
                raise KeyError(f"Array key '{key}' not found in {path}. Available keys: {loaded.files}")
            array = np.asarray(loaded[key])
            loaded.close()
        else:
            array = np.asarray(loaded)

        spacing = np.asarray(kwargs.get("spacing", np.ones(array.ndim)), dtype=float)
        if spacing.size != array.ndim:
            raise ValueError(f"Configured spacing {spacing.tolist()} does not match {array.ndim}D array {path}.")
        image = sitk.GetImageFromArray(array)
        image.SetSpacing(tuple(spacing[::-1]))
        return ImageData(array=array, spacing=spacing, path=str(path), image=image)


class DicomSeriesReader(ImageReader):
    """Read a directory containing one DICOM image series."""

    extensions = ()

    def read(self, path: str, **kwargs: Any) -> ImageData:
        if not os.path.isdir(path):
            raise FileNotFoundError(f"DICOM series directory does not exist: {path}")

        series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(path)
        if not series_ids:
            raise ValueError(f"No DICOM series found in directory: {path}")

        requested_id = kwargs.get("series_id")
        if requested_id is None:
            if len(series_ids) != 1:
                raise ValueError(
                    f"Directory {path} contains {len(series_ids)} DICOM series; configure 'series_id' explicitly."
                )
            requested_id = series_ids[0]
        elif requested_id not in series_ids:
            raise KeyError(f"DICOM series '{requested_id}' not found in {path}. Available: {series_ids}")

        filenames = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(path, requested_id)
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(filenames)
        return _from_sitk(reader.Execute(), path)


class DicomSegReader(SimpleITKFileReader):
    """Read a DICOM SEG object through SimpleITK/GDCM."""

    extensions = (".dcm",)


FORMAT_ALIASES = {
    "nifti": "nifti",
    ".nii": "nifti",
    ".nii.gz": "nifti",
    "nrrd": "nrrd",
    ".nrrd": "nrrd",
    "mha": "mha",
    "metaimage": "mha",
    ".mha": "mha",
    ".mhd": "mha",
    "raster": "raster",
    ".png": "raster",
    ".jpg": "raster",
    ".jpeg": "raster",
    ".tif": "raster",
    ".tiff": "raster",
    ".bmp": "raster",
    "array": "array",
    ".npy": "array",
    ".npz": "array",
    "dicom_series": "dicom_series",
    "dicom": "dicom_series",
    "dicom_seg": "dicom_seg",
    ".dcm": "dicom_seg",
    "auto": "auto",
}

READERS = {
    "nifti": NiftiReader,
    "nrrd": NrrdReader,
    "mha": MhaReader,
    "raster": RasterImageReader,
    "array": ArrayReader,
    "dicom_series": DicomSeriesReader,
    "dicom_seg": DicomSegReader,
}


def normalize_format(format_name: Optional[str]) -> str:
    if format_name is None:
        return "auto"
    normalized = str(format_name).strip().lower()
    if normalized not in FORMAT_ALIASES:
        supported = ", ".join(sorted(FORMAT_ALIASES))
        raise ValueError(f"Unsupported image format '{format_name}'. Supported values: {supported}")
    return FORMAT_ALIASES[normalized]


def get_reader(format_name: str) -> ImageReader:
    normalized = normalize_format(format_name)
    if normalized == "auto":
        raise ValueError("'auto' must be resolved from a path before selecting a reader.")
    return READERS[normalized]()


def _configured_extensions(format_name: Optional[str]) -> tuple[str, ...]:
    raw = str(format_name).strip().lower() if format_name is not None else "auto"
    normalized = normalize_format(format_name)
    if raw.startswith(".") and raw in FORMAT_ALIASES:
        return (raw,)
    if normalized == "auto":
        return tuple(
            ext for key in ("nifti", "nrrd", "mha", "raster", "array", "dicom_seg") for ext in READERS[key].extensions
        )
    return READERS[normalized].extensions


def infer_format(path: str) -> str:
    """Infer the registered reader name from a file or directory path."""
    lower = str(path).lower()
    for format_name, reader_class in READERS.items():
        if format_name in {"dicom_series", "dicom_seg"}:
            continue
        if any(lower.endswith(ext) for ext in reader_class.extensions):
            return format_name
    if os.path.isdir(path):
        return "dicom_series"
    if lower.endswith(".dcm"):
        return "dicom_seg"
    raise ValueError(f"Cannot infer an image reader from path: {path}")


def resolve_configured_format(config: dict, kind: str, modality_name: str = "MRI") -> str:
    """Resolve ``image``, ``segmentation`` or ``prediction`` format.

    ``formats`` may be a single value or a mapping. Legacy configurations are
    supported by falling back to NIfTI for MRI and automatic raster discovery
    for US.
    """
    formats = config.get("formats")
    if isinstance(formats, str):
        return formats
    if isinstance(formats, dict):
        value = formats.get(kind)
        if value is None and kind == "prediction":
            value = formats.get("segmentation")
        if value is not None:
            return value

    legacy = config.get(f"{kind}_format") or config.get("format")
    if legacy is not None:
        return legacy
    return ".nii.gz" if modality_name.upper() == "MRI" else "auto"


def resolve_reader_options(config: dict, kind: str) -> dict:
    """Return optional reader arguments for one input kind."""
    options = config.get("reader_options", {})
    if not isinstance(options, dict):
        raise ValueError("'reader_options' must be a mapping.")
    common = options.get("common", {})
    specific = options.get(kind, {})
    if not isinstance(common, dict) or not isinstance(specific, dict):
        raise ValueError(f"reader_options.common and reader_options.{kind} must be mappings.")
    return {**common, **specific}


def read_subject_image(
    root_dir: str,
    subject_id: str,
    sequence: str,
    format_name: Optional[str],
    **reader_options: Any,
) -> ImageData:
    """Read a subject image following AUDIT's subject-directory convention."""
    if not root_dir or not subject_id:
        raise ValueError("Both root_dir and subject_id must be non-empty strings.")

    subject_dir = Path(root_dir) / subject_id
    base_name = f"{subject_id}{sequence}"
    normalized = normalize_format(format_name)

    if normalized == "dicom_series":
        candidates = [subject_dir / base_name, subject_dir]
        for candidate in candidates:
            if candidate.is_dir():
                return get_reader(normalized).read(str(candidate), **reader_options)
        raise FileNotFoundError(f"DICOM series for '{base_name}' not found below {subject_dir}.")

    if normalized == "dicom_seg":
        candidates = [subject_dir / f"{base_name}.dcm", subject_dir / base_name]
    else:
        candidates = [subject_dir / f"{base_name}{ext}" for ext in _configured_extensions(format_name)]

    for candidate in candidates:
        if candidate.is_file():
            resolved_format = normalized if normalized != "auto" else infer_format(str(candidate))
            return get_reader(resolved_format).read(str(candidate), **reader_options)

    if normalized == "auto":
        dicom_candidates = [subject_dir / base_name, subject_dir]
        for candidate in dicom_candidates:
            if candidate.is_dir() and sitk.ImageSeriesReader.GetGDCMSeriesIDs(str(candidate)):
                return get_reader("dicom_series").read(str(candidate), **reader_options)
        candidates.extend(dicom_candidates)

    expected = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Image for subject '{subject_id}' and sequence '{sequence}' not found. Tried: {expected}")
