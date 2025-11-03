from os import getenv
from dotenv import load_dotenv
from pathlib import Path

# Load environment once at app startup
dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)


class Config:
    """Application configuration."""
    
    # Database configuration
    DB_USER = getenv("POSTGRES_USER")
    DB_PASSWORD = getenv("POSTGRES_PASSWORD")
    DB_HOST = getenv("POSTGRES_HOST")
    DB_PORT = getenv("POSTGRES_PORT")
    DB_NAME = getenv("POSTGRES_DB_NAME")

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Connection pool settings
    DB_POOL_SIZE = int(getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW = int(getenv("DB_MAX_OVERFLOW", 20))
    DB_POOL_TIMEOUT = int(getenv("DB_POOL_TIMEOUT", 30))
    DB_POOL_RECYCLE = int(getenv("DB_POOL_RECYCLE", 3600))
