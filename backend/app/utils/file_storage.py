"""
SkinSense AI - Asynchronous File Storage Utility.

Manages secure, asynchronous image file storage for skin lesion uploads, creating
directory trees under uploads/patients/{patient_id}/ with UUID filenames.
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile, HTTPException, status
from app.config import settings


def _save_file_sync(destination_path: Path, content: bytes) -> None:
    """
    Synchronous helper executed via thread pool to perform non-blocking disk writes.
    """
    with open(destination_path, "wb") as f:
        f.write(content)


async def save_uploaded_image(
    file: UploadFile,
    patient_id: str
) -> Dict[str, Any]:
    """
    Saves an uploaded image asynchronously into uploads/patients/{patient_id}/.
    
    Generates a unique UUID filename while preserving the original extension.
    Guarantees directories are created and existing files are never overwritten.
    
    Returns:
        Dict containing saved_filename, relative_path, and absolute_path.
    """
    try:
        # 1. Determine base uploads path and construct patient directory
        base_uploads_dir = Path(settings.UPLOADS_DIR)
        patient_dir = base_uploads_dir / "patients" / str(patient_id)

        # 2. Ensure patient directory exists
        patient_dir.mkdir(parents=True, exist_ok=True)

        # 3. Extract and sanitize file extension
        filename = file.filename or "image.jpg"
        extension = filename.split(".")[-1].lower() if "." in filename else "jpg"

        # 4. Generate unique UUID filename
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        destination_path = patient_dir / unique_filename

        # Ensure collision safety
        while destination_path.exists():
            unique_filename = f"{uuid.uuid4().hex}.{extension}"
            destination_path = patient_dir / unique_filename

        # 5. Read uploaded file bytes and write asynchronously via threadpool
        content = await file.read()
        await asyncio.to_thread(_save_file_sync, destination_path, content)

        # Reset pointer after reading
        await file.seek(0)

        # 6. Construct path outputs
        relative_path = str(destination_path.as_posix())
        absolute_path = str(destination_path.resolve())

        return {
            "saved_filename": unique_filename,
            "relative_path": relative_path,
            "absolute_path": absolute_path,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded image to storage: {str(exc)}"
        )
