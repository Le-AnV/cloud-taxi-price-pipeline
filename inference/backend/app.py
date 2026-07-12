"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.config import get_settings
from backend.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_v1_prefix)

frontend_dist_path = Path(__file__).resolve().parent / "frontend_dist"
frontend_index_path = frontend_dist_path / "index.html"

if frontend_dist_path.exists():
    app.mount(
        "/assets", StaticFiles(directory=frontend_dist_path / "assets"), name="assets"
    )


@app.get("/", include_in_schema=False, response_model=None)
async def root() -> Response:
    """Serve the built frontend when available."""

    if frontend_index_path.exists():
        return FileResponse(frontend_index_path)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Frontend not built into this image. Build the React app and copy dist/ into backend/frontend_dist.",
        },
    )
