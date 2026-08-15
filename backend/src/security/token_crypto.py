from __future__ import annotations

from cryptography.fernet import Fernet

from src.config import get_settings


def _fernet() -> Fernet:
    return Fernet(get_settings().token_encryption_key.encode())


def chiffrer(valeur_claire: str) -> bytes:
    """Chiffre une valeur sensible (token OAuth) avant stockage — Principe II, jamais en clair."""
    return _fernet().encrypt(valeur_claire.encode())


def dechiffrer(valeur_chiffree: bytes) -> str:
    return _fernet().decrypt(valeur_chiffree).decode()
