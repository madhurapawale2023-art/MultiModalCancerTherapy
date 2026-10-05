# ============================================================
# MultiModalCancerTherapy
# backend/app/core/config.py
# Application Configuration
# ============================================================

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"


# ============================================================
# Load .env
# ============================================================

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


# ============================================================
# Application Settings
# ============================================================

class Settings(BaseSettings):

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    APP_NAME: str = "MultiModalCancerTherapy"

    APP_VERSION: str = "1.0.0"

    APP_ENV: str = "development"

    DEBUG: bool = True


    # --------------------------------------------------------
    # Server
    # --------------------------------------------------------

    HOST: str = "127.0.0.1"

    PORT: int = 8000


    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------

    DB_HOST: str = "localhost"

    DB_PORT: int = 5432

    DB_NAME: str = "postgres"

    DB_USER: str = "postgres"

    DB_PASSWORD: str = ""


    # --------------------------------------------------------
    # JWT Authentication
    # --------------------------------------------------------

    JWT_SECRET_KEY: str = (
        "change-this-secret-key-before-production"
    )

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # --------------------------------------------------------
    # Uploads
    # --------------------------------------------------------

    UPLOAD_DIR: str = "uploads"

    MAX_UPLOAD_SIZE_MB: int = 10


    # --------------------------------------------------------
    # ML Model Paths
    # --------------------------------------------------------

    CLINICAL_MODEL_PATH: str = (
        "models/clinical/clinical_model.joblib"
    )

    CLINICAL_PREPROCESSOR_PATH: str = (
        "models/clinical/clinical_preprocessor.joblib"
    )

    CLINICAL_ENCODER_PATH: str = (
        "models/clinical/target_encoder.joblib"
    )

    ULTRASOUND_MODEL_PATH: str = (
        "models/image/ultrasound_unet_clean.pth"
    )

    ULTRASOUND_METADATA_PATH: str = (
        "models/image/ultrasound_unet_clean_info.json"
    )

    MULTIMODAL_CONFIG_PATH: str = (
        "models/multimodal_fusion_config.json"
    )


    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    CORS_ORIGINS: str = (
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:5500,http://127.0.0.1:5500,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8000,http://127.0.0.1:8000"
    )


    # --------------------------------------------------------
    # Pydantic configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# ============================================================
# Settings Instance
# ============================================================

settings = Settings()


# ============================================================
# Helper Functions
# ============================================================

def get_project_path(relative_path: str) -> Path:
    """
    Convert project-relative path into absolute path.
    """
    return PROJECT_ROOT / relative_path


def get_upload_directory() -> Path:
    """
    Return absolute upload directory and create it.
    """

    upload_dir = get_project_path(
        settings.UPLOAD_DIR
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return upload_dir


def get_cors_origins() -> list[str]:
    """
    Convert comma-separated CORS origins into a list.
    """

    return [
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ]