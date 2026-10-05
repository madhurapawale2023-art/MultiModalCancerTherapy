# ============================================================
# MultiModalCancerTherapy
# backend/app/db/database.py
# PostgreSQL + SQLAlchemy Database Configuration
# ============================================================

import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ============================================================
# Load Environment Variables
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()


# ============================================================
# Database Configuration
# ============================================================

DB_HOST = os.getenv(
    "DB_HOST",
    "localhost"
)

DB_PORT = int(
    os.getenv(
        "DB_PORT",
        "5432"
    )
)

DB_NAME = os.getenv(
    "DB_NAME",
    "postgres"
)

DB_USER = os.getenv(
    "DB_USER",
    "postgres"
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    ""
)


# ============================================================
# SQLAlchemy Database URL
# URL.create safely handles special characters in password
# ============================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)


# ============================================================
# SQLAlchemy Engine
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    future=True
)


# ============================================================
# Session Factory
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session
)


# ============================================================
# Base Model
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# Database Dependency
# ============================================================

def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# Test Database Connection
# ============================================================

def check_database_connection() -> bool:

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as error:

        print(
            "Database connection failed:",
            error
        )

        return False


# ============================================================
# Initialize Database
# ============================================================

def init_database() -> None:

    try:

        with engine.connect() as connection:

            connection.execute(
                text(
                    "CREATE SCHEMA IF NOT EXISTS multimodal"
                )
            )

            connection.commit()

        print(
            "PostgreSQL database connection initialized."
        )

    except Exception as error:

        print(
            "Database initialization failed:",
            error
        )

        raise


# ============================================================
# Database Information
# ============================================================

def get_database_info() -> dict:

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT
                        current_database(),
                        current_user
                    """
                )
            ).fetchone()

            return {
                "database": result[0],
                "user": result[1],
                "connected": True
            }

    except Exception as error:

        return {
            "database": None,
            "user": None,
            "connected": False,
            "error": str(error)
        }