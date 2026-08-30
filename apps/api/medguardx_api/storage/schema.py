"""Database schema (SQLAlchemy Core).

Using Core with a ``DATABASE_URL`` gives real pluggability: the same schema and
queries run on SQLite (dev/local) and PostgreSQL (production) with no code
changes -- fixing the old build's ephemeral-SQLite-only persistence.
"""
from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(150), unique=True, nullable=False, index=True),
    Column("password_hash", String(255), nullable=False),
    Column("role", String(50), nullable=False, default="patient"),
    Column("full_name", String(255)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

patients = Table(
    "patients",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("name_encrypted", Text),
    Column("owner_user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

records = Table(
    "records",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("patient_id", String(64), ForeignKey("patients.id"), nullable=False, index=True),
    Column("file_type", String(20), nullable=False),
    Column("original_filename", String(512)),
    Column("extracted_text_encrypted", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

access_logs = Table(
    "access_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("username", String(150)),
    Column("patient_id", String(64)),
    Column("record_id", Integer),
    Column("role", String(50), nullable=False),
    Column("purpose", String(50)),
    Column("consent", Boolean, default=False),
    Column("masking_strategy", String(50)),
    Column("policy_rule", Text),
    Column("accessed_at", DateTime(timezone=True), server_default=func.now()),
)

audit_logs = Table(
    "audit_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("action", String(50), nullable=False),
    Column("actor", String(150)),
    Column("actor_role", String(50)),
    Column("target", String(255)),
    Column("details", Text),
    Column("timestamp", DateTime(timezone=True), server_default=func.now()),
)
