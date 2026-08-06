"""Public request and response schemas for property value inference."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PropertyFeatures(BaseModel):
    """Features available for one property at inference time."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        json_schema_extra={
            "example": {
                "bedrooms": 4,
                "bathrooms": 1.0,
                "sqft_living": 1680,
                "sqft_lot": 5043,
                "floors": 1.5,
                "waterfront": 0,
                "view": 0,
                "condition": 4,
                "grade": 6,
                "sqft_above": 1680,
                "sqft_basement": 0,
                "yr_built": 1911,
                "yr_renovated": 0,
                "zipcode": "98118",
                "lat": 47.5354,
                "long": -122.273,
                "sqft_living15": 1560,
                "sqft_lot15": 5765,
            }
        },
    )

    bedrooms: int = Field(ge=0, description="Número de quartos.", examples=[4])
    bathrooms: float = Field(ge=0, description="Número de banheiros.", examples=[1.0])
    sqft_living: int = Field(
        ge=0, description="Área habitável interna, em square feet.", examples=[1680]
    )
    sqft_lot: int = Field(ge=0, description="Área do lote, em square feet.", examples=[5043])
    floors: float = Field(ge=0, description="Número de pavimentos.", examples=[1.5])
    waterfront: int = Field(
        ge=0, le=1, description="Indica frente para água: 0 não, 1 sim.", examples=[0]
    )
    view: int = Field(ge=0, le=4, description="Índice de vista, de 0 a 4.", examples=[0])
    condition: int = Field(ge=1, le=5, description="Índice de condição, de 1 a 5.", examples=[4])
    grade: int = Field(
        ge=1, le=13, description="Índice de qualidade construtiva, de 1 a 13.", examples=[6]
    )
    sqft_above: int = Field(
        ge=0, description="Área acima do solo, em square feet.", examples=[1680]
    )
    sqft_basement: int = Field(ge=0, description="Área do porão, em square feet.", examples=[0])
    yr_built: int = Field(ge=0, description="Ano de construção.", examples=[1911])
    yr_renovated: int = Field(
        ge=0, description="Ano de reforma; 0 significa que não há reforma registrada.", examples=[0]
    )
    zipcode: str = Field(
        pattern=r"^\d{5}$",
        description=(
            "CEP de cinco dígitos da localização; formalmente válido, sem garantia de "
            "cobertura do modelo para qualquer CEP."
        ),
        examples=["98118"],
    )
    lat: float = Field(
        ge=-90,
        le=90,
        description=(
            "Latitude da localização; formalmente válida, sem garantia de cobertura "
            "universal do modelo."
        ),
        examples=[47.5354],
    )
    long: float = Field(
        ge=-180,
        le=180,
        description=(
            "Longitude da localização; formalmente válida, sem garantia de cobertura "
            "universal do modelo."
        ),
        examples=[-122.273],
    )
    sqft_living15: int = Field(
        ge=0,
        description="Área habitável de referência da vizinhança, em square feet.",
        examples=[1560],
    )
    sqft_lot15: int = Field(
        ge=0,
        description="Área de lote de referência da vizinhança, em square feet.",
        examples=[5765],
    )


class BatchPredictionRequest(BaseModel):
    """A bounded collection of properties for one inference request."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "bedrooms": 4,
                        "bathrooms": 1.0,
                        "sqft_living": 1680,
                        "sqft_lot": 5043,
                        "floors": 1.5,
                        "waterfront": 0,
                        "view": 0,
                        "condition": 4,
                        "grade": 6,
                        "sqft_above": 1680,
                        "sqft_basement": 0,
                        "yr_built": 1911,
                        "yr_renovated": 0,
                        "zipcode": "98118",
                        "lat": 47.5354,
                        "long": -122.273,
                        "sqft_living15": 1560,
                        "sqft_lot15": 5765,
                    }
                ]
            }
        },
    )

    items: list[PropertyFeatures] = Field(
        min_length=1, description="Imóveis a prever; o lote requer ao menos um item."
    )


class PredictionResponse(BaseModel):
    """Prediction returned for one property."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predicted_price": 372953.43,
                "currency": "USD",
                "model_version": "0.4.0-rc1",
                "request_id": "b55ae80b6ad24ffb97a06e4963781637",
            }
        },
    )

    predicted_price: float = Field(description="Preço previsto em USD.", examples=[372953.43])
    currency: Literal["USD"] = "USD"
    model_version: str = Field(description="Versão do modelo servido.", examples=["0.4.0-rc1"])
    request_id: str = Field(
        description="Identificador de rastreabilidade da requisição.",
        examples=["b55ae80b6ad24ffb97a06e4963781637"],
    )


class BatchPredictionItem(BaseModel):
    """One ordered prediction inside a batch response."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"item_id": 1, "predicted_price": 372953.43}},
    )

    item_id: int = Field(description="Posição do item no lote, iniciada em 1.", examples=[1])
    predicted_price: float = Field(description="Preço previsto em USD.", examples=[372953.43])


class BatchPredictionResponse(BaseModel):
    """Predictions returned for a batch."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predictions": [{"item_id": 1, "predicted_price": 372953.43}],
                "currency": "USD",
                "model_version": "0.4.0-rc1",
                "request_id": "b55ae80b6ad24ffb97a06e4963781637",
            }
        },
    )

    predictions: list[BatchPredictionItem] = Field(
        description="Previsões na mesma ordem dos itens de entrada."
    )
    currency: Literal["USD"] = "USD"
    model_version: str = Field(description="Versão do modelo servido.", examples=["0.4.0-rc1"])
    request_id: str = Field(
        description="Identificador de rastreabilidade do lote.",
        examples=["b55ae80b6ad24ffb97a06e4963781637"],
    )


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
