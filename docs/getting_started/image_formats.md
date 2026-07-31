# Image formats and readers

AUDIT configures the clinical modality and the storage format separately.
They answer different questions:

- `modality`: what kind of image is this? It selects domain behaviour such as
  preprocessing, default sequences, 2D/3D feature semantics, and viewers.
- `formats`: how is each input stored? It selects the reader and preserves
  available metadata such as physical spacing.

For example, an ultrasound image can be stored as PNG, NRRD, DICOM, or NIfTI.
Conversely, a NIfTI file is not necessarily an MRI.

## Supported readers

| Configuration value | Reader | Input |
| --- | --- | --- |
| `.nii`, `.nii.gz`, `nifti` | `NiftiReader` | NIfTI file |
| `.nrrd`, `nrrd` | `NrrdReader` | NRRD file |
| `.mha`, `.mhd`, `mha` | `MhaReader` | MetaImage file |
| `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `raster` | `RasterImageReader` | 2D raster image |
| `.npy`, `.npz`, `array` | `ArrayReader` | NumPy array |
| `dicom_series` | `DicomSeriesReader` | Directory containing one DICOM series |
| `dicom_seg`, `.dcm` | `DicomSegReader` | DICOM SEG file |
| `auto` | inferred from path | Supported file extension or DICOM directory |

## Configuration

The normal form is a mapping so that raw images, ground truth, and predictions
may use different storage formats:

```yaml
modality: US

formats:
  image: .png
  segmentation: .png
  prediction: .npz
```

For `.npz`, select the array explicitly when the archive contains more than
one:

```yaml
reader_options:
  prediction:
    array_key: segmentation
```

Array files do not contain spatial metadata. Physical spacing can be supplied
in NumPy axis order:

```yaml
reader_options:
  common:
    spacing: [0.2, 0.2]
```

If a DICOM directory contains multiple series, select one with
`reader_options.<kind>.series_id`.

Raster segmentations should be grayscale or palette-indexed masks whose pixel
values are the configured labels. RGB colour-coded masks are converted to
luminance; v0.2.0 does not include a colour-to-label mapping.

## Dataset layout

File readers use the existing AUDIT subject layout:

```text
images/
└── case_001/
    ├── case_001_t1.nii.gz
    └── case_001_seg.nii.gz
```

For a single-image US case with no configured sequences:

```text
images/
└── case_001/
    ├── case_001.png
    └── case_001_seg.png
```

A DICOM series can be placed in either
`case_001/case_001_<sequence>/` or the subject directory itself.


