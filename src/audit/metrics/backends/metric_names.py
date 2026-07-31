"""Public metric keys supported by each metric backend."""

from __future__ import annotations

AUDIT_METRICS = (
    "dice",
    "jaccard",
    "accuracy",
    "precision",
    "sensitivity",
    "specificity",
    "hausdorff_distance",
    "predicted_size",
)

PYMIA_METRICS = (
    "ari",
    "auc",
    "ckc",
    "dice",
    "ic",
    "jacc",
    "mi",
    "rand",
    "so",
    "sdo",
    "vs",
    "haus",
    "avd",
    "mahal",
    "vi",
    "gce",
    "prob",
    "sens",
    "spec",
    "prec",
    "fmeas",
    "accu",
    "fallout",
    "fnr",
    "tp",
    "fp",
    "tn",
    "fn",
    "ref_vol",
    "pred_vol",
)

METRICS_RELOADED_METRICS = (
    "numb_ref",
    "numb_pred",
    "numb_tp",
    "numb_fp",
    "numb_fn",
    "accuracy",
    "nb",
    "ec",
    "ba",
    "cohens_kappa",
    "wck",
    "lr+",
    "iou",
    "fbeta",
    "dsc",
    "youden_ind",
    "ppv",
    "npv",
    "ior",
    "sensitivity",
    "specificity",
    "mcc",
    "cldice",
    "assd",
    "boundary_iou",
    "hd",
    "hd_perc",
    "masd",
    "nsd",
    "avdr",
)

BACKEND_METRICS = {
    "audit": AUDIT_METRICS,
    "pymia": PYMIA_METRICS,
    "metricsreloaded": METRICS_RELOADED_METRICS,
}

# Only the historical AUDIT abbreviations are renamed. Third-party backend
# keys intentionally remain native so users retain access to their full APIs.
AUDIT_LEGACY_ALIASES = {
    "jacc": "jaccard",
    "accu": "accuracy",
    "prec": "precision",
    "sens": "sensitivity",
    "spec": "specificity",
    "haus": "hausdorff_distance",
    "size": "predicted_size",
}


def get_backend_metrics(backend: str) -> tuple[str, ...]:
    """Return the public configuration keys accepted by ``backend``."""
    backend = backend.lower()
    if backend not in BACKEND_METRICS:
        supported = ", ".join(BACKEND_METRICS)
        raise ValueError(f"Unknown metrics backend '{backend}'. Supported backends: {supported}")
    return BACKEND_METRICS[backend]


def normalize_metric_names(metric_names: list[str], backend: str = "audit") -> list[str]:
    """Normalize AUDIT legacy aliases and validate backend-specific keys."""
    backend = backend.lower()
    supported = get_backend_metrics(backend)
    aliases = AUDIT_LEGACY_ALIASES if backend == "audit" else {}
    normalized = [aliases.get(name, name) for name in metric_names]
    duplicates = sorted({name for name in normalized if normalized.count(name) > 1})
    if duplicates:
        raise ValueError("Metrics configured more than once through canonical/legacy aliases: " + ", ".join(duplicates))
    unknown = [name for name in normalized if name not in supported]
    if unknown:
        raise ValueError(
            f"Unsupported metric(s) for backend '{backend}': {', '.join(unknown)}. "
            f"Available metrics: {', '.join(supported)}"
        )
    return normalized


def normalize_metric_config(metrics: dict[str, bool], backend: str = "audit") -> dict[str, bool]:
    """Normalize and validate the keys of a YAML ``metrics`` mapping."""
    names = list(metrics)
    normalized_names = normalize_metric_names(names, backend)
    return {canonical: metrics[source] for source, canonical in zip(names, normalized_names)}


def backend_metric_name(metric_name: str, backend: str) -> str:
    """Validate and return the exact implementation key for a backend."""
    return normalize_metric_names([metric_name], backend)[0]


def backend_metric_pairs(metric_names: list[str], backend: str) -> list[tuple[str, str]]:
    """Return output/backend key pairs, preserving third-party native names."""
    names = normalize_metric_names(metric_names, backend)
    return [(name, name) for name in names]


def validate_metric_names(metric_names: list[str], backend: str = "audit") -> None:
    """Validate metric keys against the selected backend."""
    normalize_metric_names(metric_names, backend)


# Compatibility for code importing the previous constant name.
LEGACY_METRIC_ALIASES = AUDIT_LEGACY_ALIASES
CANONICAL_METRICS = AUDIT_METRICS
