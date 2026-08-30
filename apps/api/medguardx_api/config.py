"""Service configuration, loaded from environment variables.

Security-critical secrets must be provided explicitly in production. When
``ENVIRONMENT=production`` the service refuses to start with a generated key,
closing the old build's hole where a missing key silently fell back to a
hardcoded / throwaway value.
"""
from __future__ import annotations

import secrets
import warnings
from functools import lru_cache
from typing import List

from cryptography.fernet import Fernet
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MEDGUARDX_", env_file=".env", extra="ignore")

    environment: str = Field(default="development")

    # Auth / crypto secrets. Empty means "generate an ephemeral one" -- allowed
    # only outside production (see the validator below).
    jwt_secret: str = Field(default="")
    fernet_key: str = Field(default="")
    access_token_expire_hours: int = Field(default=12)
    jwt_algorithm: str = Field(default="HS256")

    # Storage. SQLite by default; set a postgresql+psycopg URL for production.
    database_url: str = Field(default="sqlite:///./medguardx.db")

    # NLP model used by the engine.
    model: str = Field(default="en_core_web_md")

    # Optional admin seed. When both are set, an admin account is created at
    # startup if it doesn't already exist. This is the ONLY way to mint an admin
    # -- the public /register endpoint refuses privileged roles.
    admin_username: str = Field(default="")
    admin_password: str = Field(default="")

    # CORS: comma-separated allowlist string. "*" is rejected in production.
    # Kept as a plain string so env parsing stays simple; use `cors_origins`.
    cors_origins_raw: str = Field(default="http://localhost:3000", alias="MEDGUARDX_CORS_ORIGINS")

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    def resolved_jwt_secret(self) -> str:
        if self.jwt_secret:
            return self.jwt_secret
        if self.is_production:
            raise RuntimeError("MEDGUARDX_JWT_SECRET must be set in production.")
        warnings.warn("No MEDGUARDX_JWT_SECRET set; using an ephemeral dev secret.", stacklevel=2)
        return secrets.token_urlsafe(48)

    def resolved_fernet_key(self) -> str:
        if self.fernet_key:
            return self.fernet_key
        if self.is_production:
            raise RuntimeError("MEDGUARDX_FERNET_KEY must be set in production (data is unrecoverable if it rotates).")
        warnings.warn("No MEDGUARDX_FERNET_KEY set; using an ephemeral dev key. Stored data will not survive a restart.", stacklevel=2)
        return Fernet.generate_key().decode()

    def validate_production(self) -> None:
        if self.is_production and "*" in self.cors_origins:
            raise RuntimeError("Wildcard CORS ('*') is not allowed in production. Set MEDGUARDX_CORS_ORIGINS.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
