"""
Basic project health tests.

These tests verify:
- Application configuration loads correctly.
- PostgreSQL database connection is available.
- Core backend modules can be imported.
"""

from backend.app.core.config import settings
from backend.app.db.database import check_database_connection


def test_application_configuration():
    """
    Verify basic application configuration.
    """

    assert settings.APP_NAME == "MultiModalCancerTherapy"

    assert settings.DB_HOST == "localhost"

    assert int(settings.DB_PORT) == 5432


def test_database_connection():
    """
    Verify PostgreSQL database connection.
    """

    assert check_database_connection() is True


def test_core_modules_import():
    """
    Verify important backend modules can be imported.
    """

    from backend.app.core import config
    from backend.app.core import dependencies
    from backend.app.core import security
    from backend.app.db import database
    from backend.app.db import models

    assert config is not None
    assert dependencies is not None
    assert security is not None
    assert database is not None
    assert models is not None