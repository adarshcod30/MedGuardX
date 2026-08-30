"""Fernet (AES-128-CBC + HMAC) encryption for data at rest.

The key comes from configuration. In production a missing key is a hard error
(see :mod:`medguardx_api.config`), so records can never be silently encrypted
with a throwaway key that rotates on the next deploy.
"""
from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet

from .config import get_settings


@lru_cache
def _fernet() -> Fernet:
    key = get_settings().resolved_fernet_key()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(data: str) -> str:
    return _fernet().encrypt(data.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
