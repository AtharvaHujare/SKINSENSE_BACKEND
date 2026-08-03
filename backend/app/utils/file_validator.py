"""
SkinSense AI - File Validation Utility Module.

Provides reusable image file validation for skin lesion uploads, checking file extension,
MIME type, file size limits, and non-empty file content.
"""

from typing import Set
from fastapi import UploadFile, HTTPException, status

# Configuration Constants
ALLOWED_EXTENSIONS: Set[str] = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES: Set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit


async def validate_image_file(
    file: UploadFile,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES
) -> UploadFile:
    """
    Validates uploaded image file against extension, content type, empty payload, and size boundaries.
    
    Raises:
        HTTPException(400): Empty file or invalid extension.
        HTTPException(415): Unsupported MIME type.
        HTTPException(413): Exceeds maximum size limit (10MB).
    """
    # 1. Validate filename and extension
    filename = file.filename or ""
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if not extension or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file extension '.{extension}'. "
                f"Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        )

    # 2. Validate MIME content-type header
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file content type '{content_type}'. "
                f"Allowed MIME types are: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            )
        )

    # 3. Read content to inspect file size and empty payload
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty. Please select a valid skin lesion image."
        )

    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of {max_mb:.0f} MB."
        )

    # Reset file pointer back to starting position for downstream processing
    await file.seek(0)
    return file
