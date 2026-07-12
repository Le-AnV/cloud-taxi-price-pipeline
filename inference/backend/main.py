"""Command-line entrypoint for local development."""

from __future__ import annotations

import uvicorn

from backend.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
