from uuid import uuid4
from dataclasses import dataclass

import filetype
from fastapi import UploadFile

from app.utils.logger import logger
from app.integrations.files import UploadResponse


@dataclass
class _CustomKind:
    mime: str

    def __init__(self, mime: str) -> None:
        self.mime = mime


class FolderService:
    """Folder Service."""

    @staticmethod
    def profile_folder(user_id: str) -> str:
        """Construct profile folder path for a user."""
        return f"users/{user_id}/profile"


class FileService:
    """File Service."""

    @staticmethod
    async def upload_file(file: UploadFile, folder: str) -> UploadResponse:
        """Upload a file to a cloud storage."""
        kind = filetype.guess(file.file)  # type: ignore

        if kind is None:
            logger.warning("File type could not be determined", file=file.filename)
            if not file.filename:
                return {
                    "success": False,
                    "filename": "",
                    "url": "",
                    "message": "File type could not be determined",
                }

            extension = file.filename.split(".")[-1]
            if extension == "txt":
                kind = _CustomKind("text/plain")
            elif extension == "md":
                kind = _CustomKind("text/markdown")
            else:
                logger.warning(
                    "File extension not supported",
                    file=file.filename,
                    extension=extension,
                )
                return {
                    "success": False,
                    "filename": "",
                    "url": "",
                    "message": "File type could not be determined",
                }

        match kind.mime:
            case "text/plain":
                filename = (
                    file.filename
                    if file.filename and file.filename.endswith(".txt")
                    else f"{(file.filename or uuid4().hex).split('.')[0]}.txt"
                )
            case "application/pdf":
                filename = (
                    file.filename
                    if file.filename and file.filename.endswith(".pdf")
                    else f"{(file.filename or uuid4().hex).split('.')[0]}.pdf"
                )
            case _:  # type: ignore
                logger.warning(
                    "File type not supported",
                    file=file.filename,
                    mime=kind.mime,  # type: ignore
                )
                return {
                    "success": False,
                    "filename": "",
                    "url": "",
                    "message": "File type not supported",
                }

        return {
            "success": True,
            "filename": filename,
            "url": f"https://example.com/{folder}/{filename}",
            "message": "File uploaded successfully",
        }

    @staticmethod
    def delete_file(filename: str) -> bool:
        """Delete a file from cloud storage."""
        # Implement the logic to delete the file from cloud storage
        # For now, we will just log the action and return True
        logger.info("Deleting file", filename=filename)
        return True
