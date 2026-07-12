import { useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import axios from "axios";
import {
  MapContainer,
  Marker,
  Polygon,
  Polyline,
  TileLayer,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";

type LatLng = [number, number];

type PredictResponse = {
  predicted_fare: number;
  trip_distance_miles: number;
  route_geometry: [number, number][];
};

const backendBaseUrl =
  import.meta.env.VITE_BACKEND_BASE_URL ?? "http://localhost:8000/api/v1";
const nycBoundary: LatLng[] = [
  [40.917577, -74.25909],
  [40.917577, -73.700272],
  [40.477399, -73.700272],
  [40.477399, -74.25909],
];
const defaultCenter: LatLng = [40.7128, -74.006];

const vendorOptions = ["Creative Mobile Technologies", "VeriFone Inc"];
const rateCodeOptions = [
  "Standard Rate",
  "JFK",
  "Newark",
  "Negotiated Fare",
  "Group Ride",
];

const createMarker = (color: string) =>
  L.divIcon({
    className: "",
    html: `<div style="width:16px;height:16px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 6px 18px rgba(0,0,0,0.25);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

function BoundaryClickHandler({
  onPick,
}: {
  onPick: (latlng: LatLng) => void;
}) {
  useMapEvents({
    click(event: { latlng: { lat: number; lng: number } }) {
      onPick([event.latlng.lat, event.latlng.lng]);
    },
  });
  return null;
}

function pointInPolygon(point: LatLng, polygon: LatLng[]): boolean {
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersect =
      yi > y !== yj > y &&
      x < ((xj - xi) * (y - yi)) / (yj - yi + 0.0000001) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

export default function App() {
  const [pickup, setPickup] = useState<LatLng | null>(null);
  const [dropoff, setDropoff] = useState<LatLng | null>(null);
  const [activePoint, setActivePoint] = useState<"pickup" | "dropoff">(
    "pickup",
  );
  const [vendorName, setVendorName] = useState(vendorOptions[0]);
  const [rateCodeName, setRateCodeName] = useState(rateCodeOptions[0]);
  const [route, setRoute] = useState<LatLng[]>([]);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canPredict = useMemo(
    () => Boolean(pickup && dropoff && vendorName && rateCodeName),
    [pickup, dropoff, vendorName, rateCodeName],
  );

  const handleMapClick = (latlng: LatLng) => {
    if (!pointInPolygon(latlng, nycBoundary)) {
      setError("Location must be inside New York City.");
      return;
    }

    setError("");
    if (activePoint === "pickup") {
      setPickup(latlng);
    } else {
      setDropoff(latlng);
    }
  };

  const handlePredict = async () => {
    if (!pickup || !dropoff) return;
    setLoading(true);
    setError("");

    try {
      const response = await axios.post<PredictResponse>(
        `${backendBaseUrl}/predict`,
        {
          pickup_latitude: pickup[0],
          pickup_longitude: pickup[1],
          dropoff_latitude: dropoff[0],
          dropoff_longitude: dropoff[1],
          vendor_name: vendorName,
          rate_code_name: rateCodeName,
        },
      );
      setPrediction(response.data);
      setRoute(
        response.data.route_geometry.map(([longitude, latitude]) => [
          latitude,
          longitude,
        ]),
      );
    } catch (requestError: unknown) {
      setError(
        axios.isAxiosError(requestError)
          ? (requestError.response?.data?.detail ?? "Prediction failed.")
          : "Prediction failed.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <main className="app-grid">
        <section className="hero-panel">
          <div className="eyebrow">NYC Taxi Fare Prediction</div>
          <h1>
            Estimate taxi fare with map-based pickup and dropoff selection.
          </h1>
          <p>
            Choose both locations inside New York City, select vendor and rate
            code, then let the backend handle routing, feature engineering, and
            inference.
          </p>

          <div className="controls">
            <label>
              Vendor
              <select
                value={vendorName}
                onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                  setVendorName(event.target.value)
                }
              >
                {vendorOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Rate Code
              <select
                value={rateCodeName}
                onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                  setRateCodeName(event.target.value)
                }
              >
                {rateCodeOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="action-row">
            <button
              className={activePoint === "pickup" ? "active" : ""}
              onClick={() => setActivePoint("pickup")}
            >
              Set Pickup
            </button>
            <button
              className={activePoint === "dropoff" ? "active" : ""}
              onClick={() => setActivePoint("dropoff")}
            >
              Set Dropoff
            </button>
            <button disabled={!canPredict || loading} onClick={handlePredict}>
              {loading ? "Predicting..." : "Predict Fare"}
            </button>
          </div>

          {error ? <div className="alert error">{error}</div> : null}

          <div className="cards">
            <article className="metric-card">
              <span>Fare</span>
              <strong>
                {prediction ? `$${prediction.predicted_fare.toFixed(2)}` : "--"}
              </strong>
            </article>
            <article className="metric-card">
              <span>Distance</span>
              <strong>
                {prediction
                  ? `${prediction.trip_distance_miles.toFixed(2)} mi`
                  : "--"}
              </strong>
            </article>
          </div>
        </section>

        <section className="map-panel">
          <MapContainer
            center={defaultCenter}
            zoom={11}
            scrollWheelZoom
            className="map-view"
          >
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Polygon
              positions={nycBoundary}
              pathOptions={{ color: "#ff7a18", weight: 2, fillOpacity: 0.08 }}
            />
            {pickup ? (
              <Marker position={pickup} icon={createMarker("#14b8a6")} />
            ) : null}
            {dropoff ? (
              <Marker position={dropoff} icon={createMarker("#f97316")} />
            ) : null}
            {route.length === 2 ? (
              <Polyline
                positions={route}
                pathOptions={{ color: "#111827", weight: 4 }}
              />
            ) : null}
            <BoundaryClickHandler onPick={handleMapClick} />
          </MapContainer>
        </section>
      </main>
    </div>
  );
}
