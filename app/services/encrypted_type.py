import base64
from os import getenv
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy.types import String, TypeDecorator

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

_cipher = None


def _get_cipher():
    """Build the Fernet cipher lazily so importing this module (and therefore
    `app`) doesn't require FERNET_KEY to already exist — `groupbite.py init`
    imports `app` before it has generated FERNET_KEY in the first place."""
    global _cipher
    if _cipher is None:
        fernet_key = getenv("FERNET_KEY")
        if not fernet_key:
            raise RuntimeError(
                "FERNET_KEY is not set. Run `python groupbite.py init` to generate it."
            )
        _cipher = Fernet(str.encode(fernet_key))
    return _cipher


class Encrypted(TypeDecorator):
    """Custom SQLAlchemy type that encrypts/decrypts string data."""

    impl = String  # The underlying database type

    def process_bind_param(self, value, dialect):
        """Encrypt the value before storing it in the database."""
        if value is not None:
            # Encrypt the value using Fernet cipher
            encrypted_value = _get_cipher().encrypt(value.encode())
            # Store it as a base64-encoded string
            return base64.b64encode(encrypted_value).decode()
        return value

    def process_result_value(self, value, dialect):
        """Decrypt the value when retrieving it from the database."""
        if value is not None:
            # Decode the base64-encoded value and decrypt it
            decrypted_value = _get_cipher().decrypt(base64.b64decode(value))
            return decrypted_value.decode()
        return value


def encrypt_value(value=None):
    if value is not None:
        encrypted_value = _get_cipher().encrypt(value.encode())
        return base64.b64encode(encrypted_value).decode()
    return value


def decrypt_value(value=None):
    if value is not None:
        decrypted_value = _get_cipher().decrypt(base64.b64decode(value))
        return decrypted_value.decode()
    return value
