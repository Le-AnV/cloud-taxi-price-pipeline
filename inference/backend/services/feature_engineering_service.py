"""Feature engineering utilities for taxi fare inference."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from backend.services.routing_service import RouteResult

MILES_PER_METER = 0.000621371


@dataclass(frozen=True)
class EngineeredFeatures:
    """All model features required for inference."""

    trip_distance_miles: float
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    manhattan_dist: float
    haversine_dist: float
    vendor_name: str
    rate_code_name: str
    weekday: str


class FeatureEngineeringService:
    """Derive model-ready features from raw request data and routing output."""

    @staticmethod
    def _haversine_miles(
        pickup_latitude: float,
        pickup_longitude: float,
        dropoff_latitude: float,
        dropoff_longitude: float,
    ) -> float:
        earth_radius_miles = 3958.7613
        lat1 = math.radians(pickup_latitude)
        lon1 = math.radians(pickup_longitude)
        lat2 = math.radians(dropoff_latitude)
        lon2 = math.radians(dropoff_longitude)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        )
        return 2 * earth_radius_miles * math.asin(math.sqrt(a))

    @staticmethod
    def _manhattan_miles(
        pickup_latitude: float,
        pickup_longitude: float,
        dropoff_latitude: float,
        dropoff_longitude: float,
    ) -> float:
        north_south_miles = abs(dropoff_latitude - pickup_latitude) * 69.0
        east_west_miles = (
            abs(dropoff_longitude - pickup_longitude)
            * 53.0
            * math.cos(math.radians((pickup_latitude + dropoff_latitude) / 2))
        )
        return north_south_miles + abs(east_west_miles)

    def build_features(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        dropoff_latitude: float,
        dropoff_longitude: float,
        vendor_name: str,
        rate_code_name: str,
        route_result: RouteResult,
        current_time: datetime | None = None,
    ) -> EngineeredFeatures:
        """Create model input features from raw coordinates and metadata."""

        trip_distance_miles = route_result.distance_meters * MILES_PER_METER
        haversine_dist = self._haversine_miles(
            pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude
        )
        manhattan_dist = self._manhattan_miles(
            pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude
        )
        weekday = (current_time or datetime.now()).strftime("%A")

        return EngineeredFeatures(
            trip_distance_miles=trip_distance_miles,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropoff_latitude=dropoff_latitude,
            dropoff_longitude=dropoff_longitude,
            manhattan_dist=manhattan_dist,
            haversine_dist=haversine_dist,
            vendor_name=vendor_name,
            rate_code_name=rate_code_name,
            weekday=weekday,
        )
