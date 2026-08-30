"""MedGuardX API application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .routes import audit, auth, preview, retrieve, upload
from .storage import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    # Warm the model so the first request isn't slow. Best-effort: a missing model
    # should surface clearly rather than crash startup.
    try:
        from .engine import get_engine

        get_engine().warm_up()
    except Exception as exc:  # pragma: no cover
        app.state.engine_warm_error = str(exc)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MedGuardX API",
        description="Hardened healthcare PII/PHI masking service with enforced RBAC.",
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    for module in (auth, upload, retrieve, preview, audit):
        app.include_router(module.router)

    @app.get("/", tags=["health"])
    def root():
        return {"name": "MedGuardX", "version": __version__, "status": "running"}

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
