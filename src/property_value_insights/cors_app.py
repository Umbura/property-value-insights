"""CORS-enabled ASGI entrypoint for the public stakeholder demo."""

from __future__ import annotations

import os
from collections.abc import Iterable

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from .api import create_app
from .config import Settings

CORS_ENV = "PVI_CORS_ORIGINS"


def parse_cors_origins(raw: str | None = None) -> tuple[str, ...]:
    """Parse a comma-separated allowlist of browser origins."""

    configured = os.getenv(CORS_ENV, "") if raw is None else raw
    origins: list[str] = []
    for value in configured.split(","):
        origin = value.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)
    return tuple(origins)


def create_cors_app(
    settings: Settings | None = None,
    *,
    origins: Iterable[str] | None = None,
) -> ASGIApp:
    """Wrap the inference API with a restrictive CORS policy for browser clients."""

    api: FastAPI = create_app(settings)
    allowed_origins = tuple(origins) if origins is not None else parse_cors_origins()
    if not allowed_origins:
        return api

    return CORSMiddleware(
        app=api,
        allow_origins=list(allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )


app = create_cors_app()


__all__ = ["app", "create_cors_app", "parse_cors_origins"]
