from io import BytesIO
from typing import BinaryIO
from hashlib import sha256
from pathlib import Path

from b2sdk.v3 import B2Api, AuthInfoCache, InMemoryAccountInfo

from app.env import BASE_DIR, settings
from app.utils.logger import logger

from .typing import UploadResponse

info = InMemoryAccountInfo()
cache = AuthInfoCache(info)
b2_api = B2Api(info, cache)

b2_api.authorize_account(settings.B2_APP_KEY_ID, settings.B2_APP_KEY, "production")  # type: ignore


def upload_file(file: BinaryIO, filename: str) -> UploadResponse:
    """Upload a file to Backblaze B2."""
    try:
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        file_data = file.read()
        file_info = bucket.upload_bytes(file_data, filename)  # type: ignore
        url = bucket.get_download_url(file_info.file_name)  # type: ignore

    except Exception as e:
        logger.error("File upload failed", filename=filename, error=str(e))
        return {
            "success": False,
            "filename": filename,
            "url": "",
            "message": "File upload failed",
        }

    return {"success": True, "filename": filename, "url": url}


def delete_file(filename: str) -> bool:
    """Delete a file from Backblaze B2."""
    try:
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        downloaded_file = bucket.download_file_by_name(filename)
        downloaded_file.download_version.delete()

    except Exception as e:
        logger.error("File deletion failed", filename=filename, error=str(e))
        return False

    return True


def download_file_to_memory(filename: str) -> BinaryIO | None:
    """Download a file from Backblaze B2."""
    try:
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        downloaded_file = bucket.download_file_by_name(filename)

        file_io = BytesIO()
        downloaded_file.save(file_io)
        file_io.seek(0)  # Reset cursor to the beginning of the file

        return file_io

    except Exception as e:
        logger.error("File download failed", filename=filename, error=str(e))
        return None


def download_file_to_disk(filename: str) -> str | None:
    """Download a file from Backblaze B2 to disk."""
    try:
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        downloaded_file = bucket.download_file_by_name(filename)

        file_path = (
            BASE_DIR
            / "temp"
            / (sha256(filename.encode()).hexdigest() + "." + filename.split(".")[-1])
        )  # Hash filename for unique storage
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            downloaded_file.save(f)

        return str(file_path)

    except Exception as e:
        logger.error("File download failed", filename=filename, error=str(e))
        return None


def delete_file_from_disk(file_path: str) -> bool:
    """Delete a file from disk."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True

        else:
            logger.warning("File not found for deletion", file_path=file_path)
            return False

    except Exception as e:
        logger.error(
            "File deletion from disk failed", file_path=file_path, error=str(e)
        )
        return False
