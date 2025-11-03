from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database engine and session creation.

    Uses scoped_session for thread-safety with Flask and eventlet.
    """

    def __init__(self, config: Config):
        self.config = config
        self.engine = self._create_engine()
        self.SessionFactory = self._create_session_factory()

    def _create_engine(self):
        """Create SQLAlchemy engine with proper configuration."""
        return create_engine(
            self.config.DATABASE_URL,
            pool_size=self.config.DB_POOL_SIZE,
            max_overflow=self.config.DB_MAX_OVERFLOW,
            pool_timeout=self.config.DB_POOL_TIMEOUT,
            pool_recycle=self.config.DB_POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before using
            echo=False
        )

    def _create_session_factory(self):
        session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        return scoped_session(session_factory)

    def get_session(self) -> Session:
        return self.SessionFactory()

    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Session error, rolling back")
            raise
        finally:
            session.close()
            self.SessionFactory.remove()

    def close_all_sessions(self):
        self.SessionFactory.remove()
        self.engine.dispose()


# Global instance (initialized in app factory)
db_manager: DatabaseManager = None


def init_db(config: Config):
    global db_manager
    db_manager = DatabaseManager(config)
    return db_manager


def get_session() -> Session:
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db_manager.get_session()


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    with db_manager.get_session_context() as session:
        yield session
