"""Storage access layer.

Encapsulates every DB query behind a small API. Encryption of record text happens
here, so callers never handle ciphertext. Works identically on SQLite and Postgres
via the configured ``DATABASE_URL``.
"""
from __future__ import annotations

import uuid
from functools import lru_cache
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine

from ..config import get_settings
from ..encryption import decrypt, encrypt
from . import schema


def _normalize_url(url: str) -> str:
    """Coerce managed-Postgres URLs to the psycopg v3 driver.

    Render/Heroku expose ``postgres://`` or ``postgresql://``; SQLAlchemy would
    otherwise pick psycopg2. We ship psycopg v3, so pin the driver explicitly.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@lru_cache
def _engine() -> Engine:
    url = _normalize_url(get_settings().database_url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True, future=True)
    if url.startswith("sqlite"):
        # WAL improves concurrency for the file-backed dev database.
        with engine.begin() as conn:
            conn.exec_driver_sql("PRAGMA journal_mode=WAL")
    return engine


def init_db() -> None:
    schema.metadata.create_all(_engine())


# --- users ----------------------------------------------------------------------
def create_user(username: str, password_hash: str, role: str, full_name: Optional[str]) -> int:
    with _engine().begin() as conn:
        result = conn.execute(
            schema.users.insert().values(
                username=username, password_hash=password_hash, role=role, full_name=full_name
            )
        )
        return int(result.inserted_primary_key[0])


def get_user_by_username(username: str) -> Optional[dict]:
    with _engine().connect() as conn:
        row = conn.execute(
            select(schema.users).where(schema.users.c.username == username)
        ).mappings().first()
        return dict(row) if row else None


# --- patients & records ---------------------------------------------------------
def create_patient(owner_user_id: Optional[int] = None, name: Optional[str] = None) -> str:
    patient_id = str(uuid.uuid4())
    with _engine().begin() as conn:
        conn.execute(
            schema.patients.insert().values(
                id=patient_id,
                name_encrypted=encrypt(name) if name else None,
                owner_user_id=owner_user_id,
            )
        )
    return patient_id


def patient_exists(patient_id: str) -> bool:
    with _engine().connect() as conn:
        return conn.execute(
            select(schema.patients.c.id).where(schema.patients.c.id == patient_id)
        ).first() is not None


def store_record(patient_id: str, file_type: str, filename: str, extracted_text: str) -> int:
    with _engine().begin() as conn:
        result = conn.execute(
            schema.records.insert().values(
                patient_id=patient_id,
                file_type=file_type,
                original_filename=filename,
                extracted_text_encrypted=encrypt(extracted_text),
            )
        )
        return int(result.inserted_primary_key[0])


def get_records_by_patient(patient_id: str) -> List[dict]:
    with _engine().connect() as conn:
        rows = conn.execute(
            select(schema.records)
            .where(schema.records.c.patient_id == patient_id)
            .order_by(schema.records.c.created_at.desc())
        ).mappings().all()
    return [
        {
            "id": r["id"],
            "patient_id": r["patient_id"],
            "file_type": r["file_type"],
            "original_filename": r["original_filename"],
            "extracted_text": decrypt(r["extracted_text_encrypted"]),
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]


# --- logging --------------------------------------------------------------------
def log_access(*, user_id, username, patient_id, record_id, role, purpose, consent, masking_strategy, policy_rule) -> None:
    with _engine().begin() as conn:
        conn.execute(
            schema.access_logs.insert().values(
                user_id=user_id, username=username, patient_id=patient_id, record_id=record_id,
                role=role, purpose=purpose, consent=bool(consent),
                masking_strategy=masking_strategy, policy_rule=policy_rule,
            )
        )


def log_audit(*, action, actor, actor_role, target, details) -> None:
    with _engine().begin() as conn:
        conn.execute(
            schema.audit_logs.insert().values(
                action=action, actor=actor, actor_role=actor_role, target=target, details=details
            )
        )


def get_audit_logs(limit: int = 50, offset: int = 0) -> Tuple[List[dict], int]:
    with _engine().connect() as conn:
        total = conn.execute(select(func.count()).select_from(schema.audit_logs)).scalar_one()
        rows = conn.execute(
            select(schema.audit_logs)
            .order_by(schema.audit_logs.c.timestamp.desc())
            .limit(limit).offset(offset)
        ).mappings().all()
    logs = [
        {
            "id": r["id"], "action": r["action"], "actor": r["actor"],
            "actor_role": r["actor_role"], "target": r["target"],
            "details": r["details"], "timestamp": str(r["timestamp"]),
        }
        for r in rows
    ]
    return logs, int(total)


def get_stats() -> dict:
    e = _engine()
    with e.connect() as conn:
        def count(table, where=None):
            q = select(func.count()).select_from(table)
            if where is not None:
                q = q.where(where)
            return int(conn.execute(q).scalar_one())

        return {
            "total_patients": count(schema.patients),
            "total_records": count(schema.records),
            "total_access_events": count(schema.access_logs),
            "total_audit_logs": count(schema.audit_logs),
            "recent_uploads": count(schema.records),
            "recent_accesses": count(schema.access_logs),
        }
