"""AES encryption/decryption for stored medical data."""
from cryptography.fernet import Fernet
import base64
import os

_KEY = os.environ.get("MEDGUARDX_KEY", "ZHVtbXkta2V5LWZvci1kZXYtb25seS0xMjM0NTY3OA==")

# Ensure valid Fernet key (32 url-safe base64-encoded bytes)
try:
    _fernet = Fernet(_KEY.encode() if isinstance(_KEY, str) else _KEY)
except Exception:
    _fernet = Fernet(Fernet.generate_key())


def encrypt(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    return _fernet.decrypt(data.encode()).decode()


def generate_key() -> str:
    return Fernet.generate_key().decode()
