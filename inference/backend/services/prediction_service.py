"""Model loading and prediction service."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from backend.config import Settings
from backend.services.feature_engineering_service import EngineeredFeatures

logger = logging.getLogger(__name__)

FEATURE_NUMERIC_COLS = [
    "trip_distance_miles",
    "pickup_latitude",
    "pickup_longitude",
    "dropoff_latitude",
    "dropoff_longitude",
    "manhattan_dist",
    "haversine_dist",
]

FEATURE_CATEGORICAL_COLS = [
    "vendor_name",
    "rate_code_name",
    "weekday",
]

FEATURE_COLUMNS = FEATURE_NUMERIC_COLS + FEATURE_CATEGORICAL_COLS


class PredictionService:
    """Load the persisted pipeline and generate fare predictions."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pipeline = self._load_pipeline()

    def _resolve_model_path(self) -> Path:
        if self._settings.model_path.exists():
            return self._settings.model_path
        if self._settings.fallback_model_path.exists():
            logger.warning(
                "Primary model not found, using fallback model at %s",
                self._settings.fallback_model_path,
            )
            return self._settings.fallback_model_path
        raise FileNotFoundError("No trained model file was found in models/.")

    def _load_pipeline(self) -> Any:
        model_path = self._resolve_model_path()
        logger.info("Loading model from %s", model_path)
        return joblib.load(model_path)

    def predict(self, features: EngineeredFeatures) -> float:
        """Predict fare amount from engineered features."""

        frame = pd.DataFrame([features.__dict__], columns=FEATURE_COLUMNS)
        prediction = self._pipeline.predict(frame)
        return float(prediction[0])
