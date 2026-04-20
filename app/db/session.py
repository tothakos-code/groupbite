import logging
from contextlib import contextmanager
from pickle import GLOBAL
from typing import Generator, Optional

from flask import g, has_request_context
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

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
        # non scoped
        self.session_factory: sessionmaker = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        # scoped
        self.scoped_session_factory: scoped_session = scoped_session(
            self.session_factory
        )

    def _create_engine(self):
        """Create SQLAlchemy engine with proper configuration."""
        return create_engine(
            self.config.DATABASE_URL,
            pool_size=self.config.DB_POOL_SIZE,
            max_overflow=self.config.DB_MAX_OVERFLOW,
            pool_timeout=self.config.DB_POOL_TIMEOUT,
            pool_recycle=self.config.DB_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=False,
        )

    def get_scoped_session(self) -> Session:
        return self.scoped_session_factory()

    def get_nonscoped_session(self) -> Session:
        return self.session_factory()

    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        if has_request_context():
            # In-request: reuse one session on g
            if g is None:  # safety, should not happen if Flask is present
                raise RuntimeError(
                    "Flask request context present but flask.g unavailable."
                )

            session: Optional[Session] = getattr(g, "db_session", None)
            if session is None:
                session = self.get_scoped_session()
                g.db_session = session

            yield session
            return

        # Outside request: own the session lifecycle
        session = self.get_nonscoped_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("DB session error, rolling back")
            raise
        finally:
            session.close()

    def close_all_sessions(self):
        try:
            self.scoped_session_factory.remove()
        finally:
            self.engine.dispose()

    def init_flask(self, app):
        @app.teardown_request
        def request_end(exception):
            session = getattr(g, "db_session", None)
            if session is None:
                return

            try:
                if exception is None:
                    session.commit()
                else:
                    session.rollback()
            finally:
                self.scoped_session_factory.remove()
                g.db_session = None


# Global instance (initialized in app factory)
db_manager: DatabaseManager = None


def init_db(application, config: Config):
    global db_manager
    db_manager = DatabaseManager(config)
    db_manager.init_flask(application)
    return db_manager


@contextmanager
def get_session() -> Generator[Session, None, None]:
    global db_manager
    with db_manager.get_session_context() as db:
        yield db
