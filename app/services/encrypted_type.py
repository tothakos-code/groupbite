from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
import base64
from cryptography.fernet import Fernet

from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

FERNET_KEY = getenv('FERNET_KEY')
cipher = Fernet(str.encode(FERNET_KEY))

class Encrypted(TypeDecorator):
    """Custom SQLAlchemy type that encrypts/decrypts string data."""

    impl = String  # The underlying database type

    def process_bind_param(self, value, dialect):
        """Encrypt the value before storing it in the database."""
        if value is not None:
            # Encrypt the value using Fernet cipher
            encrypted_value = cipher.encrypt(value.encode())
            # Store it as a base64-encoded string
            return base64.b64encode(encrypted_value).decode()
        return value

    def process_result_value(self, value, dialect):
        """Decrypt the value when retrieving it from the database."""
        if value is not None:
            # Decode the base64-encoded value and decrypt it
            decrypted_value = cipher.decrypt(base64.b64decode(value))
            return decrypted_value.decode()
        return value
