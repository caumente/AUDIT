import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from audit.app.launcher import run_streamlit_app


def test_run_streamlit_app_uses_current_python_and_preserves_config_path():
    config_path = Path("configuration with spaces.yml")

    with patch("audit.app.launcher.subprocess.run") as run:
        run_streamlit_app(config_path)

    command = run.call_args.args[0]
    assert command[:4] == [sys.executable, "-m", "streamlit", "run"]
    assert command[-2:] == ["--config", str(config_path)]
    run.assert_called_once_with(command, check=True)


def test_run_streamlit_app_propagates_streamlit_failure():
    with patch(
        "audit.app.launcher.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, ["streamlit"]),
    ):
        with pytest.raises(subprocess.CalledProcessError):
            run_streamlit_app("config.yml")
