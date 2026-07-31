from pathlib import Path

import pytest

from audit.utils.internal._config_helpers import load_config_file


def test_load_config_file_resolves_relative_path_from_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    config_path = tmp_path / "config.yml"
    config_path.write_text("modality: US\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert load_config_file("config.yml") == {"modality": "US"}


def test_load_config_file_keeps_packaged_config_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)

    config = load_config_file("configs/app.yml")

    assert config["modality"] == "MRI"


def test_load_config_file_reports_user_and_packaged_candidates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="Checked user path"):
        load_config_file("missing.yml")
