"""OSRM routing integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from backend.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteResult:
    """Structured route geometry returned by OSRM."""

    distance_meters: float
    geometry: list[list[float]]


class RoutingService:
    """Fetch route information from OSRM public API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_route(
        self,
        pickup_latitude: float,
        pickup_longitude: float,
        dropoff_latitude: float,
        dropoff_longitude: float,
    ) -> RouteResult:
        """Request route distance and geometry from OSRM."""

        url = (
            f"{self._settings.osrm_base_url}/route/v1/{self._settings.osrm_profile}/"
            f"{pickup_longitude},{pickup_latitude};{dropoff_longitude},{dropoff_latitude}"
        )
        params = {"overview": "full", "geometries": "geojson", "steps": "false"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload: dict[str, Any] = response.json()

        routes = payload.get("routes") or []
        if not routes:
            raise ValueError("Unable to calculate route.")

        route = routes[0]
        geometry = route.get("geometry", {}).get("coordinates", [])
        logger.info("OSRM route fetched successfully")
        return RouteResult(distance_meters=float(route["distance"]), geometry=geometry)
