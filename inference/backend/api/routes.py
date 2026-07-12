"""API routes for taxi fare inference."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.config import Settings, get_settings
from backend.schemas.predict import PredictRequest, PredictResponse
from backend.services.feature_engineering_service import FeatureEngineeringService
from backend.services.prediction_service import PredictionService
from backend.services.routing_service import RoutingService

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    """Simple health endpoint."""

    return {"status": "ok"}


@router.post("/predict", response_model=PredictResponse)
async def predict(
    payload: PredictRequest, settings: Settings = Depends(get_settings)
) -> PredictResponse:
    """Run routing, feature engineering, and model inference."""

    routing_service = RoutingService(settings)
    feature_service = FeatureEngineeringService()
    prediction_service = PredictionService(settings)

    try:
        route_result = await routing_service.get_route(
            payload.pickup_latitude,
            payload.pickup_longitude,
            payload.dropoff_latitude,
            payload.dropoff_longitude,
        )
        features = feature_service.build_features(
            payload.pickup_latitude,
            payload.pickup_longitude,
            payload.dropoff_latitude,
            payload.dropoff_longitude,
            payload.vendor_name,
            payload.rate_code_name,
            route_result,
        )
        predicted_fare = prediction_service.predict(features)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return PredictResponse(
        predicted_fare=round(predicted_fare, 2),
        trip_distance_miles=round(features.trip_distance_miles, 2),
        route_geometry=route_result.geometry,
    )
