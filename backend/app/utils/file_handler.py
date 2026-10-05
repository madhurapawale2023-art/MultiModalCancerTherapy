"""
File handling utilities for uploaded clinical and imaging files.

Supported use:
- Ultrasound images
- Clinical/report attachments
- General hospital document uploads

No DNA testing functionality is included.
"""

from pathlib import Path
from typing import Optional
from uuid import uuid4


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

UPLOAD_ROOT = PROJECT_ROOT / "uploads"

ULTRASOUND_UPLOAD_DIR = UPLOAD_ROOT / "ultrasound"
REPORT_UPLOAD_DIR = UPLOAD_ROOT / "reports"
GENERAL_UPLOAD_DIR = UPLOAD_ROOT / "general"


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".doc",
    ".docx",
}

ALLOWED_GENERAL_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS
    | ALLOWED_DOCUMENT_EXTENSIONS
)


# Maximum upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# DIRECTORY HELPERS
# ============================================================

def ensure_upload_directories() -> None:
    """
    Create upload directories when they do not exist.
    """

    ULTRASOUND_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    GENERAL_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# FILENAME HELPERS
# ============================================================

def get_file_extension(
    filename: str,
) -> str:
    """
    Return a normalized file extension.
    """

    return Path(filename).suffix.lower()


def is_allowed_image(
    filename: str,
) -> bool:
    """
    Check whether a file is a supported image.
    """

    return get_file_extension(filename) in (
        ALLOWED_IMAGE_EXTENSIONS
    )


def is_allowed_document(
    filename: str,
) -> bool:
    """
    Check whether a file is a supported document.
    """

    return get_file_extension(filename) in (
        ALLOWED_DOCUMENT_EXTENSIONS
    )


def is_allowed_file(
    filename: str,
) -> bool:
    """
    Check whether a file has a supported extension.
    """

    return get_file_extension(filename) in (
        ALLOWED_GENERAL_EXTENSIONS
    )


def create_safe_filename(
    original_filename: str,
    prefix: Optional[str] = None,
) -> str:
    """
    Create a unique filename without trusting the original
    client-supplied filename.
    """

    extension = get_file_extension(
        original_filename
    )

    if not extension:
        extension = ""

    unique_id = uuid4().hex

    if prefix:
        safe_prefix = "".join(
            character
            if character.isalnum() or character in (
                "_",
                "-",
            )
            else "_"
            for character in prefix.strip()
        )

        return f"{safe_prefix}_{unique_id}{extension}"

    return f"{unique_id}{extension}"


# ============================================================
# PATH HELPERS
# ============================================================

def get_ultrasound_upload_path(
    filename: str,
) -> Path:
    """
    Return destination path for an ultrasound image.
    """

    ensure_upload_directories()

    safe_name = create_safe_filename(
        filename,
        prefix="ultrasound",
    )

    return ULTRASOUND_UPLOAD_DIR / safe_name


def get_report_upload_path(
    filename: str,
) -> Path:
    """
    Return destination path for a report/document.
    """

    ensure_upload_directories()

    safe_name = create_safe_filename(
        filename,
        prefix="report",
    )

    return REPORT_UPLOAD_DIR / safe_name


def get_general_upload_path(
    filename: str,
) -> Path:
    """
    Return destination path for a general allowed file.
    """

    ensure_upload_directories()

    safe_name = create_safe_filename(
        filename,
        prefix="file",
    )

    return GENERAL_UPLOAD_DIR / safe_name


# ============================================================
# FILE SIZE VALIDATION
# ============================================================

def validate_file_size(
    file_size: int,
    max_size: int = MAX_FILE_SIZE,
) -> None:
    """
    Validate file size.

    Raises:
        ValueError: when size exceeds the configured limit.
    """

    if file_size < 0:
        raise ValueError(
            "File size cannot be negative."
        )

    if file_size > max_size:
        raise ValueError(
            f"File size exceeds the maximum allowed size "
            f"of {max_size // (1024 * 1024)} MB."
        )


# ============================================================
# FILE CONTENT VALIDATION
# ============================================================

def validate_filename(
    filename: str,
    allowed_extensions=None,
) -> None:
    """
    Validate filename extension.
    """

    if not filename or not filename.strip():
        raise ValueError(
            "Filename cannot be empty."
        )

    extension = get_file_extension(
        filename
    )

    if allowed_extensions is None:
        allowed_extensions = (
            ALLOWED_GENERAL_EXTENSIONS
        )

    if extension not in allowed_extensions:
        raise ValueError(
            f"Unsupported file type: {extension or 'unknown'}"
        )


# ============================================================
# SAVE FILE
# ============================================================

def save_file(
    content: bytes,
    original_filename: str,
    destination: str = "general",
    max_size: int = MAX_FILE_SIZE,
) -> Path:
    """
    Save uploaded file content to the configured upload folder.

    destination:
        ultrasound
        reports
        general
    """

    validate_filename(
        original_filename
    )

    validate_file_size(
        len(content),
        max_size=max_size,
    )

    destination = destination.lower().strip()

    if destination == "ultrasound":
        file_path = get_ultrasound_upload_path(
            original_filename
        )

        if not is_allowed_image(
            original_filename
        ):
            raise ValueError(
                "Only image files are allowed "
                "for ultrasound uploads."
            )

    elif destination == "reports":
        file_path = get_report_upload_path(
            original_filename
        )

    elif destination == "general":
        file_path = get_general_upload_path(
            original_filename
        )

    else:
        raise ValueError(
            "Invalid upload destination."
        )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_bytes(content)

    return file_path


# ============================================================
# DELETE FILE
# ============================================================

def delete_file(
    file_path: str | Path,
) -> bool:
    """
    Delete a file when it exists.
    """

    path = Path(file_path)

    if not path.exists():
        return False

    if not path.is_file():
        return False

    path.unlink()

    return True


# ============================================================
# FILE INFORMATION
# ============================================================

def get_file_info(
    file_path: str | Path,
) -> Optional[dict]:
    """
    Return basic information about a stored file.
    """

    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return None

    return {
        "name": path.name,
        "path": str(path),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "exists": True,
    }