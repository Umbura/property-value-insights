import json
from pathlib import Path

from property_value_insights.notebook_hygiene import sanitize_notebook


def test_sanitizer_removes_only_execution_timing_metadata(tmp_path: Path) -> None:
    path = tmp_path / "analysis.ipynb"
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {"execution": {"iopub.status.busy": "timestamp"}, "tag": "keep"},
                "outputs": [{"output_type": "stream", "name": "stdout", "text": ["result\n"]}],
                "source": ["print('result')"],
            }
        ],
        "metadata": {"kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook), encoding="utf-8")

    assert sanitize_notebook(path) is True
    sanitized = json.loads(path.read_text(encoding="utf-8"))

    assert sanitized["cells"][0]["metadata"] == {"tag": "keep"}
    assert sanitized["cells"][0]["execution_count"] == 1
    assert sanitized["cells"][0]["outputs"] == notebook["cells"][0]["outputs"]
    assert sanitized["metadata"] == notebook["metadata"]
    assert sanitize_notebook(path) is False
