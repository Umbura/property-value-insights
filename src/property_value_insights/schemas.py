"""Public request and response schemas for property value inference."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PropertyFeatures(BaseModel):
    """Features available for one property at inference time."""

    model_config = ConfigDict(extra="forbid", strict=True)

    bedrooms: int = Field(ge=0)
    bathrooms: float = Field(ge=0)
    sqft_living: int = Field(ge=0)
    sqft_lot: int = Field(ge=0)
    floors: float = Field(ge=0)
    waterfront: int = Field(ge=0, le=1)
    view: int = Field(ge=0, le=4)
    condition: int = Field(ge=1, le=5)
    grade: int = Field(ge=1, le=13)
    sqft_above: int = Field(ge=0)
    sqft_basement: int = Field(ge=0)
    yr_built: int = Field(ge=0)
    yr_renovated: int = Field(ge=0)
    zipcode: str = Field(pattern=r"^\d{5}$")
    lat: float = Field(ge=-90, le=90)
    long: float = Field(ge=-180, le=180)
    sqft_living15: int = Field(ge=0)
    sqft_lot15: int = Field(ge=0)


class BatchPredictionRequest(BaseModel):
    """A bounded collection of properties for one inference request."""

    model_config = ConfigDict(extra="forbid", strict=True)

    items: list[PropertyFeatures] = Field(min_length=1)


class PredictionResponse(BaseModel):
    """Prediction returned for one property."""

    predicted_price: float
    currency: Literal["USD"] = "USD"
    model_version: str
    request_id: str


class BatchPredictionItem(BaseModel):
    """One ordered prediction inside a batch response."""

    item_id: int
    predicted_price: float


class BatchPredictionResponse(BaseModel):
    """Predictions returned for a batch."""

    predictions: list[BatchPredictionItem]
    currency: Literal["USD"] = "USD"
    model_version: str
    request_id: str


class HealthResponse(BaseModel):
    status: str
    api_version: str
    model_version: str


class ModelInfoResponse(BaseModel):
    name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    algorithm: str = Field(min_length=1)
    feature_set: str = Field(min_length=1)
    feature_columns: list[str] = Field(min_length=1)
    created_at_utc: datetime
    artifact_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    evaluation: dict[str, Any] = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)


class InternalErrorResponse(BaseModel):
    detail: Literal["Internal server error"] = "Internal server error"
    request_id: str
