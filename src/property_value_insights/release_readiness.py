"""Automated checks for the integrated release candidate."""

from __future__ import annotations

import argparse
import csv
import json
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from . import __version__
from .artifact import sha256_file, sha256_normalized_text_file

EXPECTED_ENV_KEYS = {
    "LOG_LEVEL",
    "MAX_BATCH_SIZE",
    "MODEL_ARTIFACT_PATH",
    "MODEL_MANIFEST_PATH",
}
EXPECTED_PREDICTION_ROWS = 100
REQUIRED_PATHS = (
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    ".python-version",
    "uv.lock",
    "artifacts/model_manifest.json",
    "artifacts/property_value_model.joblib",
    "docs/API_CONTRACT.md",
    "docs/MODEL_CARD.md",
    "docs/RELEASE_READINESS.md",
    "docs/reviews/phase-7.md",
    "notebooks/01_eda.ipynb",
    "notebooks/02_modeling.ipynb",
    "reports/future_predictions.csv",
)
PROCESS_LANGUAGE = re.compile(
    r"\bFase\s+\d+(?:\.\d+)?\b|revis[aã]o supervisionada|crit[eé]rios? de aceite",
    re.IGNORECASE,
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SECRET_PATTERN = re.compile(
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"
)
PUBLIC_TEXT_SUFFIXES = {
    ".csv",
    ".example",
    ".ipynb",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class ReleaseCheck:
    name: str
    passed: bool
    detail: str


def _check(name: str, operation: Callable[[], str]) -> ReleaseCheck:
    try:
        detail = operation()
    except (AssertionError, KeyError, OSError, TypeError, ValueError) as error:
        return ReleaseCheck(name=name, passed=False, detail=str(error))
    return ReleaseCheck(name=name, passed=True, detail=detail)


def _validate_required_paths(root: Path) -> str:
    missing = [relative for relative in REQUIRED_PATHS if not (root / relative).exists()]
    if missing:
        raise ValueError(f"Missing required paths: {', '.join(missing)}")
    return f"{len(REQUIRED_PATHS)} required paths are present"


def _validate_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as source:
        project_version = tomllib.load(source)["project"]["version"]
    if project_version != __version__:
        raise ValueError(
            f"Package version mismatch: pyproject={project_version}, source={__version__}"
        )
    if ".dev" in project_version:
        raise ValueError("Integrated candidate still uses a development version")
    return f"package version {project_version} is consistent"


def _validate_environment_example(root: Path) -> str:
    keys = {
        line.split("=", 1)[0]
        for line in (root / ".env.example").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    if keys != EXPECTED_ENV_KEYS:
        unexpected = sorted(keys - EXPECTED_ENV_KEYS)
        missing = sorted(EXPECTED_ENV_KEYS - keys)
        raise ValueError(
            f"Environment contract differs: unexpected={unexpected}, missing={missing}"
        )
    return "environment example contains only supported runtime settings"


def _validate_artifact_and_predictions(root: Path) -> str:
    manifest = json.loads(
        (root / "artifacts" / "model_manifest.json").read_text(encoding="utf-8")
    )
    artifact_path = root / manifest["artifact"]["path"]
    predictions_path = root / manifest["prediction_output"]["path"]
    future_path = root / manifest["prediction_output"]["source_path"]

    if sha256_file(artifact_path) != manifest["artifact"]["sha256"]:
        raise ValueError("Model artifact hash differs from the manifest")
    if (
        sha256_normalized_text_file(predictions_path)
        != manifest["prediction_output"]["sha256"]
    ):
        raise ValueError("Prediction file hash differs from the manifest")
    if (
        sha256_normalized_text_file(future_path)
        != manifest["prediction_output"]["source_sha256"]
    ):
        raise ValueError("Future input hash differs from the manifest")

    with predictions_path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != EXPECTED_PREDICTION_ROWS:
        raise ValueError(f"Expected 100 predictions, found {len(rows)}")
    row_ids = [int(row["row_id"]) for row in rows]
    if row_ids != list(range(1, EXPECTED_PREDICTION_ROWS + 1)):
        raise ValueError("Prediction row identifiers are not the ordered range 1..100")
    model_versions = {row["model_version"] for row in rows}
    if model_versions != {manifest["model"]["version"]}:
        raise ValueError("Prediction model version differs from the manifest")
    if any(float(row["predicted_price"]) <= 0 for row in rows):
        raise ValueError("Prediction file contains a non-positive price")
    return "artifact hashes and 100 ordered predictions match the manifest"


def _validate_notebooks(root: Path) -> str:
    notebook_paths = sorted((root / "notebooks").glob("*.ipynb"))
    if not notebook_paths:
        raise ValueError("No notebooks were found")
    for path in notebook_paths:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(notebook["cells"], start=1):
            source = "".join(cell.get("source", []))
            if PROCESS_LANGUAGE.search(source):
                raise ValueError(f"{path.name} cell {index} contains internal process language")
            if "execution" in cell.get("metadata", {}):
                raise ValueError(f"{path.name} cell {index} contains transient timing metadata")
            if cell.get("cell_type") != "code":
                continue
            if cell.get("execution_count") is None:
                raise ValueError(f"{path.name} cell {index} has not been executed")
            if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):
                raise ValueError(f"{path.name} cell {index} contains an execution error")
    return f"{len(notebook_paths)} notebooks are executed and free of error outputs"


def _markdown_paths(root: Path) -> list[Path]:
    paths = list(root.glob("*.md"))
    for directory in ("diagrams", "docs", "reports"):
        paths.extend((root / directory).rglob("*.md"))
    return sorted(set(paths))


def _validate_markdown_links(root: Path) -> str:
    markdown_paths = _markdown_paths(root)
    broken: list[str] = []
    for path in markdown_paths:
        for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                broken.append(f"{path.relative_to(root)} -> {target}")
    if broken:
        raise ValueError(f"Broken relative links: {', '.join(broken)}")
    return f"relative links are valid across {len(markdown_paths)} Markdown files"


def _validate_publication_hygiene(root: Path) -> str:
    forbidden_local = [root / ".env", *root.glob("*.pem"), *root.glob("*.key")]
    present = [path.name for path in forbidden_local if path.exists()]
    if present:
        raise ValueError(f"Local sensitive files must be removed before publication: {present}")

    scanned = 0
    for path in root.rglob("*"):
        if not path.is_file() or any(
            part in {".git", ".pytest_cache", ".ruff_cache", ".venv"} for part in path.parts
        ):
            continue
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES and path.name not in {
            "Dockerfile",
            ".env.example",
        }:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET_PATTERN.search(content):
            raise ValueError(f"Potential credential pattern found in {path.relative_to(root)}")
        scanned += 1
    return f"no credential patterns found across {scanned} public text files"


def collect_release_checks(project_root: str | Path) -> list[ReleaseCheck]:
    root = Path(project_root).resolve()
    return [
        _check("required_paths", lambda: _validate_required_paths(root)),
        _check("package_version", lambda: _validate_version(root)),
        _check("environment_contract", lambda: _validate_environment_example(root)),
        _check("artifact_and_predictions", lambda: _validate_artifact_and_predictions(root)),
        _check("notebooks", lambda: _validate_notebooks(root)),
        _check("markdown_links", lambda: _validate_markdown_links(root)),
        _check("publication_hygiene", lambda: _validate_publication_hygiene(root)),
    ]


def verify_release(project_root: str | Path) -> list[ReleaseCheck]:
    checks = collect_release_checks(project_root)
    failures = [check for check in checks if not check.passed]
    if failures:
        summary = "; ".join(f"{check.name}: {check.detail}" for check in failures)
        raise ValueError(f"Release readiness failed: {summary}")
    return checks


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser


def main() -> int:
    args = _parser().parse_args()
    checks = collect_release_checks(args.project_root)
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"[{status}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
