from pathlib import Path

from property_value_insights.release_readiness import collect_release_checks

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_integrated_release_candidate_passes_repository_checks() -> None:
    checks = collect_release_checks(PROJECT_ROOT)

    assert checks
    assert all(check.passed for check in checks), {
        check.name: check.detail for check in checks if not check.passed
    }
