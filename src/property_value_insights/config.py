"""Environment-backed service configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime paths and operational limits for the inference service."""

    artifact_path: Path
    manifest_path: Path
    log_level: str = "INFO"
    max_batch_size: int = 100
    service_name: str = "property-value-insights"

    def __post_init__(self) -> None:
        if self.max_batch_size < 1 or self.max_batch_size > 1000:
            raise ValueError("max_batch_size must be between 1 and 1000")
        if self.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Unsupported log level")

    @classmethod
    def from_env(cls, project_root: str | Path | None = None) -> Settings:
        """Build settings from environment variables and relative repository paths."""

        root = Path(project_root or os.getenv("PROJECT_ROOT", ".")).resolve()

        def resolve_path(variable: str, default: str) -> Path:
            configured = Path(os.getenv(variable, default))
            return configured if configured.is_absolute() else root / configured

        return cls(
            artifact_path=resolve_path(
                "MODEL_ARTIFACT_PATH",
                "artifacts/property_value_model.joblib",
            ),
            manifest_path=resolve_path(
                "MODEL_MANIFEST_PATH",
                "artifacts/model_manifest.json",
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            max_batch_size=int(os.getenv("MAX_BATCH_SIZE", "100")),
        )
