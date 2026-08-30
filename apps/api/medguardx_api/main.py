"""MedGuardX API application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .routes import audit, auth, maintenance, preview, retrieve, upload
from .storage import store


def _seed_admin() -> None:
    """Create the configured admin account at startup if it doesn't exist.

    The only supported way to provision an admin -- signup can't grant the role.
    """
    settings = get_settings()
    if not (settings.admin_username and settings.admin_password):
        return
    if store.get_user_by_username(settings.admin_username):
        return
    from .security import hash_password

    store.create_user(
        username=settings.admin_username,
        password_hash=hash_password(settings.admin_password),
        role="admin",
        full_name="Administrator",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    _seed_admin()
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

    for module in (auth, upload, retrieve, preview, audit, maintenance):
        app.include_router(module.router)

    @app.get("/", tags=["health"])
    def root():
        return {"name": "MedGuardX", "version": __version__, "status": "running"}

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
