"""Storage layer — save/retrieve encrypted records."""
import uuid
import json
from ..database import get_db
from .encryption import encrypt, decrypt


def create_patient(name: str = None) -> str:
    patient_id = str(uuid.uuid4())
    db = get_db()
    db.execute(
        "INSERT INTO patients (id, name_encrypted) VALUES (?, ?)",
        (patient_id, encrypt(name) if name else None)
    )
    db.commit()
    db.close()
    return patient_id


def check_patient_exists(patient_id: str) -> bool:
    db = get_db()
    exists = db.execute("SELECT 1 FROM patients WHERE id = ?", (patient_id,)).fetchone() is not None
    db.close()
    return exists


def store_record(patient_id: str, file_type: str, filename: str,
                 raw_data: str, extracted_text: str, pii_metadata: list) -> int:
    db = get_db()
    cursor = db.execute(
        """INSERT INTO records (patient_id, file_type, original_filename,
           raw_data_encrypted, extracted_text_encrypted, pii_metadata)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (patient_id, file_type, filename,
         encrypt(raw_data), encrypt(extracted_text),
         json.dumps(pii_metadata))
    )
    record_id = cursor.lastrowid
    db.commit()
    db.close()
    return record_id


def get_records_by_patient(patient_id: str) -> list:
    db = get_db()
    rows = db.execute(
        "SELECT * FROM records WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,)
    ).fetchall()
    db.close()

    records = []
    for r in rows:
        records.append({
            "id": r["id"],
            "patient_id": r["patient_id"],
            "file_type": r["file_type"],
            "original_filename": r["original_filename"],
            "extracted_text": decrypt(r["extracted_text_encrypted"]),
            "pii_metadata": json.loads(r["pii_metadata"]) if r["pii_metadata"] else [],
            "created_at": r["created_at"],
        })
    return records


def log_access(user_id: int, patient_id: str, record_id: int,
               role: str, purpose: str, consent: bool,
               masking_strategy: str, policy_rule: str):
    db = get_db()
    db.execute(
        """INSERT INTO access_logs (user_id, patient_id, record_id, role,
           purpose, consent, masking_strategy, policy_rule) VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, patient_id, record_id, role, purpose,
         1 if consent else 0, masking_strategy, policy_rule)
    )
    db.commit()
    db.close()


def log_audit(action: str, actor: str, target: str, details: str):
    db = get_db()
    db.execute(
        "INSERT INTO audit_logs (action, actor, target, details) VALUES (?,?,?,?)",
        (action, actor, target, details)
    )
    db.commit()
    db.close()


def get_audit_logs(limit: int = 50, offset: int = 0) -> tuple:
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
    rows = db.execute(
        "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows], total


def get_stats() -> dict:
    db = get_db()
    stats = {
        "total_patients": db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
        "total_records": db.execute("SELECT COUNT(*) FROM records").fetchone()[0],
        "total_access_events": db.execute("SELECT COUNT(*) FROM access_logs").fetchone()[0],
        "total_audit_logs": db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0],
        "recent_uploads": db.execute(
            "SELECT COUNT(*) FROM records WHERE created_at > datetime('now', '-7 days')"
        ).fetchone()[0],
        "recent_accesses": db.execute(
            "SELECT COUNT(*) FROM access_logs WHERE accessed_at > datetime('now', '-7 days')"
        ).fetchone()[0],
    }
    db.close()
    return stats


def get_all_patients() -> list:
    db = get_db()
    rows = db.execute("SELECT id, created_at FROM patients ORDER BY created_at DESC").fetchall()
    db.close()
    return [dict(r) for r in rows]
