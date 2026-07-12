# NYC Taxi Fare Inference

This folder contains a complete end-to-end inference application for NYC taxi fare prediction.

## Structure

- `backend/`: FastAPI inference API
- `frontend/`: React + Leaflet UI
- `models/`: persisted trained model artifacts
- `docs/`: project documentation

## Backend

Run the API with:

```bash
uvicorn backend.app:app --reload --port 8000
```

## Frontend

Install dependencies and run the dev server:

```bash
cd frontend
npm install
npm run dev
```

Open the UI at `http://localhost:3000`.

## Run The Full Website Locally

Use two terminals:

```bash
cd inference
uvicorn backend.app:app --reload --port 8000
```

```bash
cd inference/frontend
npm install
npm run dev
```

The frontend talks to the backend at `http://localhost:8000/api/v1` by default.

## Docker

Build the full app image from `inference/`:

```bash
docker build -t nyc-taxi-inference .
```

Run it:

```bash
docker run --rm -p 8000:8000 nyc-taxi-inference
```

Open `http://localhost:8000` in the browser. The React UI is served from the same container and the API is available under `http://localhost:8000/api/v1`.

## Notes

- Frontend only sends raw coordinates and categorical inputs.
- Backend performs OSRM routing, feature engineering, and inference.
- The backend loads `models/gradient_boosting_model_v3.pkl` first and falls back to `models/random_forest_model_v3.pkl` if needed.
- The UI shows fare and route readiness, while the backend keeps the model-only feature contract.
