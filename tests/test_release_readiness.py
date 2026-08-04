import shutil
from pathlib import Path

import pytest

from property_value_insights.release_readiness import (
    _validate_artifact_and_predictions,
    _validate_publication_hygiene,
    collect_release_checks,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_integrated_release_candidate_passes_repository_checks() -> None:
    checks = collect_release_checks(PROJECT_ROOT)

    assert checks
    assert all(check.passed for check in checks), {
        check.name: check.detail for check in checks if not check.passed
    }


def test_release_check_rejects_modified_historical_input(tmp_path: Path) -> None:
    required_files = (
        "artifacts/model_manifest.json",
        "artifacts/property_value_model.joblib",
        "data/raw/future_unseen_examples.csv",
        "data/raw/kc_house_data.csv",
        "reports/future_predictions.csv",
    )
    for relative in required_files:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / relative, destination)

    historical_path = tmp_path / "data/raw/kc_house_data.csv"
    with historical_path.open("a", encoding="utf-8") as historical:
        historical.write("\n")

    with pytest.raises(ValueError, match="Historical input hash differs"):
        _validate_artifact_and_predictions(tmp_path)


@pytest.mark.parametrize(
    "relative_path",
    (
        "deploy/.env",
        "deploy/.ENV.production",
        "deploy/service-account.pem",
        "secrets/signing.key",
    ),
)
def test_release_check_rejects_nested_sensitive_files(
    tmp_path: Path, relative_path: str
) -> None:
    sensitive_path = tmp_path / relative_path
    sensitive_path.parent.mkdir(parents=True, exist_ok=True)
    sensitive_path.write_text("private material", encoding="utf-8")

    with pytest.raises(ValueError, match="Local sensitive file"):
        _validate_publication_hygiene(tmp_path)


def test_release_check_allows_environment_example(tmp_path: Path) -> None:
    example_path = tmp_path / "config/.env.example"
    example_path.parent.mkdir(parents=True)
    example_path.write_text("LOG_LEVEL=INFO\n", encoding="utf-8")

    assert "1 public text files" in _validate_publication_hygiene(tmp_path)
