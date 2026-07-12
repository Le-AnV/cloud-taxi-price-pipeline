"""Request and response schemas for prediction endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, confloat


class PredictRequest(BaseModel):
    """Prediction request payload."""

    pickup_latitude: confloat(ge=-90, le=90)
    pickup_longitude: confloat(ge=-180, le=180)
    dropoff_latitude: confloat(ge=-90, le=90)
    dropoff_longitude: confloat(ge=-180, le=180)
    vendor_name: str = Field(min_length=1)
    rate_code_name: str = Field(min_length=1)


class PredictResponse(BaseModel):
    """Prediction response payload."""

    predicted_fare: float
    trip_distance_miles: float
    currency: Literal["USD"] = "USD"
    route_geometry: list[list[float]]
