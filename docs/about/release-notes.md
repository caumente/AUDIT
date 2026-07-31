# Release notes

## AUDIT v0.2.0 — MRI/US and format-aware I/O

📅 **Release date**: July 31, 2026

`pyarrow` is pinned to 19.0.0 because the Streamlit 1.41.1 dataframe
serialization path can crash with newer incompatible releases in a fresh
installation.

This release separates two concepts that were previously coupled:

- `modality` identifies the clinical image type (`MRI` or `US`) and selects
  modality-specific preprocessing and feature extraction.
- `formats` identifies how images, segmentations, and predictions are stored
  and selects the corresponding reader.

### New functionality

- A reader registry supports NIfTI (`.nii`, `.nii.gz`), NRRD (`.nrrd`),
  MetaImage (`.mha`, `.mhd`), raster images (`.png`, `.jpg`, `.jpeg`, `.tif`,
  `.tiff`, `.bmp`), NumPy arrays (`.npy`, `.npz`), DICOM series directories,
  and DICOM SEG files.
- Image arrays and physical spacing now travel together through the feature
  and metric pipelines. SimpleITK spacing is converted to NumPy axis order.
- MRI and US can independently use any compatible reader. A run still has one
  global modality, label map, and format configuration.
- Feature extraction can pass an optional `preprocessing` mapping to the
  selected modality; US supports min-max normalization in this release.
- US now computes the configured 2D spatial features instead of silently
  ignoring `spatial: true`.
- The app's feature catalogue and segmentation error matrix are
  modality-aware; the error matrix no longer assumes NIfTI input.
- AUDIT's native metric names are now explicit and community-readable:
  `dice`, `jaccard`, `accuracy`, `precision`, `sensitivity`, `specificity`,
  `hausdorff_distance`, and `predicted_size`.
- pymia and Metrics Reloaded retain their backend-specific configuration keys
  and expose their segmentation-oriented catalogs: 30 metrics each,
  respectively.

### Corrections

- The custom Hausdorff metric now calculates the standard symmetric distance
  and applies physical spacing.
- Empty-prediction sensitivity, precision, and predicted-size metrics use consistent zero
  semantics; undefined Hausdorff values are represented as `NaN` rather than
  backend-dependent infinity.
- Metrics Reloaded now supports every binary-mask metric documented by AUDIT,
  including `wck` and `youden_ind`; its `avdr` calculation no longer suffers
  unsigned-integer underflow.
- pymia 0.3.2 distance metrics work with empty masks under NumPy 2.x, and
  undefined non-finite results are exported as `NaN`.
- Raster RGB input is converted to luminance rather than silently selecting
  the red channel.
- Missing or shape-incompatible masks now raise explicit errors instead of
  producing an all-zero error matrix.
- US tumor location is calculated from the 2D image centre and is no longer
  left undefined when spatial features are enabled.

### Compatibility and known boundaries

- Legacy YAML files without `formats` continue to load with a warning:
  MRI defaults to `.nii.gz` and US uses extension discovery.
- Metric aliases used by earlier AUDIT configurations (`jacc`, `accu`, `prec`,
  `sens`, `spec`, `haus`, and `size`) remain readable for migration purposes.
  New AUDIT CSV files use the explicit canonical names; third-party backend
  CSV files retain their native keys.
- DICOM series and DICOM SEG readers are available through SimpleITK/GDCM,
  but this release has no anonymized real DICOM fixtures. They require
  dataset-level validation before being considered production-verified.
- Raster label masks must be grayscale or palette-indexed. Colour-to-label
  mapping for RGB masks is not included.
- Ground truth and predictions must already be registered on the same grid.
  Shape and spacing are validated; automatic origin/direction validation and
  resampling are not included.
- Mixed MRI and US datasets in the same run, dataset-specific label maps, and
  dataset-specific modalities remain intentionally out of scope.

## AUDIT v0.1.2 — Multiple metric backends

📅 **Release date**: March 14, 2026

This release refactored metric extraction so the computation engine could be
selected without changing the rest of the AUDIT workflow.

### New functionality

- Added `audit`, `pymia`, and `metricsreloaded` metric backends.
- Added backend selection to `metric_extraction.yml`.
- Extended the supported overlap, distance, classification, and volume
  metrics through pymia and Metrics Reloaded.
- Added model-volume support to longitudinal and performance analyses.

### Architecture and documentation

- Replaced the previous monolithic metric pipeline with backend-specific
  modules and shared loading/processing utilities.
- Added API documentation for the metric pipeline, pymia, and Metrics
  Reloaded.
- Added the expanded getting-started workflow and updated documentation
  navigation.
- Applied project-wide Black and isort formatting before tagging the release.


## AUDIT v0.1.0

📅 **Release date**: July 10, 2025

---

We’re excited to announce the first public release of **AUDIT**, a lightweight and interactive Python tool for 
evaluating **medical image segmentation models**, especially on **MRI datasets**.  
This version focuses on enabling fast exploration and quality control with minimal setup, bridging model developers 
and researchers.

---

## 📬 Get Involved

- Try it: [auditapp.streamlit.app](https://auditapp.streamlit.app)  
- Read the docs: [caumente.github.io](https://caumente.github.io)  
- Contribute or report bugs: [github.com/caumente/audit](https://github.com/caumente/audit)

Thank you for trying AUDIT — let’s improve medical segmentation evaluation together!

---

## 🙌 Acknowledgements

Built on top of an amazing open-source ecosystem:

- [Streamlit](https://streamlit.io) – rapid UIs  
- [Plotly](https://plotly.com) – interactive graphs  
- [NiBabel](https://nipy.org/nibabel) – neuroimaging I/O  
- [ITK-SNAP](http://www.itksnap.org) – image inspection
