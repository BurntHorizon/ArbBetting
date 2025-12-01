"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator
from logger import get_logger
from config import config

logger = get_logger(__name__, config.LOG_LEVEL)


class DatabaseError(Exception):
    """Raised when there's a database connection or operation error."""
    pass


# Create database engine with connection pooling
try:
    engine = create_engine(
        config.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Maximum number of connections to keep
        max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=config.LOG_LEVEL == "DEBUG"  # Log SQL queries in debug mode
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise DatabaseError("Database initialization failed") from e

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for database operations.

    Yields:
        Database session

    Raises:
        DatabaseError: If there's an error with the database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
        logger.debug("Database transaction committed successfully")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error, rolling back transaction: {str(e)}")
        raise DatabaseError("Database operation failed") from e
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error, rolling back transaction: {str(e)}")
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def init_db():
    """
    Initialize the database by creating all tables.

    This should be called when setting up the application for the first time.

    Raises:
        DatabaseError: If table creation fails
    """
    try:
        from models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise DatabaseError("Database initialization failed") from e


def check_db_connection() -> bool:
    """
    Check if the database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False
