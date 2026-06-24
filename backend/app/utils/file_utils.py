import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile

from app.config import settings


class FileTooLargeError(Exception):
    pass


class UnsupportedFormatError(Exception):
    pass


ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/octet-stream",  # FDX files
    "text/xml",                  # Some FDX variants
    "application/xml",
}

ALLOWED_EXTENSIONS = {".pdf", ".fdx"}


def validate_upload(file: UploadFile) -> None:
    """
    Validate an uploaded file for MIME type and size.
    Raises FileTooLargeError or UnsupportedFormatError on failure.
    """
    # Check extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Unsupported file type '{ext}'. "
            f"Please upload a PDF or FDX file."
        )


def get_tmp_path(filename: str) -> Path:
    """Generate a unique temp file path."""
    tmp_dir = Path(settings.tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    return tmp_dir / unique_name


async def write_tmp(file: UploadFile) -> Path:
    """
    Write an uploaded file to the temp directory.
    Returns the path to the written file.
    """
    path = get_tmp_path(file.filename or "upload.pdf")

    content = await file.read()

    # Check file size after reading
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise FileTooLargeError(
            f"File is too large ({len(content) // (1024*1024)}MB). "
            f"Maximum size is {settings.max_file_size_mb}MB."
        )

    async with aiofiles.open(path, 'wb') as f:
        await f.write(content)

    return path


def delete_tmp(path: Path) -> None:
    """Delete a temp file. Safe to call even if file doesn't exist."""
    try:
        if path and Path(path).exists():
            os.unlink(path)
    except Exception:
        pass


def detect_format(filename: str) -> str:
    """Detect file format from filename extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".fdx":
        return "fdx"
    return "pdf"