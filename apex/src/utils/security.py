import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from src.config import get_settings


ENCRYPTED_PREFIX = "enc:v1:"


def mask_secret(value, visible_chars=4):
    if not value:
        return "Nao cadastrada"

    text = str(value)
    if len(text) <= visible_chars:
        return "*" * len(text)

    return f"{'*' * 8}{text[-visible_chars:]}"


def _credential_secret():
    settings = get_settings()
    return settings.credentials_secret_key or settings.secret_session


def _fernet():
    digest = hashlib.sha256(_credential_secret().encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def is_encrypted_secret(value):
    return bool(value and str(value).startswith(ENCRYPTED_PREFIX))


def encrypt_secret(value):
    if value in {None, ""}:
        return None

    text = str(value)
    if is_encrypted_secret(text):
        return text

    token = _fernet().encrypt(text.encode("utf-8")).decode("utf-8")
    return f"{ENCRYPTED_PREFIX}{token}"


def decrypt_secret(value):
    if value in {None, ""}:
        return None

    text = str(value)
    if not is_encrypted_secret(text):
        return text

    token = text[len(ENCRYPTED_PREFIX):]
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Nao foi possivel descriptografar uma credencial sensivel. Verifique CREDENTIALS_SECRET_KEY.") from exc
