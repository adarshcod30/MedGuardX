"""Test fixtures: hermetic env, temp SQLite, and a model-free stub engine."""
from __future__ import annotations

import os
import tempfile

import pytest

# Configure the service BEFORE importing it. Dev mode + fixed keys + temp DB.
_TMPDB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ.update(
    MEDGUARDX_ENVIRONMENT="development",
    MEDGUARDX_JWT_SECRET="test-jwt-secret",
    MEDGUARDX_FERNET_KEY="dGVzdC1mZXJuZXQta2V5LTMyLWJ5dGVzLWxvbmchISE=",
    MEDGUARDX_DATABASE_URL=f"sqlite:///{_TMPDB.name}",
    MEDGUARDX_CORS_ORIGINS="http://localhost:3000",
)


class StubEngine:
    """Real policy + masking, trivial detection -- no spaCy model needed."""

    def __init__(self):
        from medguardx import PolicyEngine

        self.policy = PolicyEngine()

    def warm_up(self):
        pass

    def detect(self, text):
        return []

    def evaluate_policy(self, role, purpose, consent):
        return self.policy.evaluate(role, purpose, consent)

    def process(self, text, role, purpose, consent=False, entities=None):
        from medguardx import mask_text
        from medguardx.engine import ProcessResult

        strategy, rule = self.policy.evaluate(role, purpose, consent)
        masked = mask_text(text, [], strategy)
        return ProcessResult(text, masked, [], strategy, rule)


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    import medguardx_api.routes.preview as preview_mod
    import medguardx_api.routes.retrieve as retrieve_mod
    import medguardx_api.routes.upload as upload_mod
    from medguardx_api.main import app

    stub = StubEngine()
    for mod in (upload_mod, retrieve_mod, preview_mod):
        mod.get_engine = lambda _stub=stub: _stub

    with TestClient(app) as c:
        yield c


def _register(client, username, role="doctor", password="password123"):
    return client.post(
        "/api/register",
        json={"username": username, "password": password, "role": role, "full_name": username},
    )
