from pathlib import Path
import mimetypes


def get_file_extension(file_path: str | Path) -> str:
    """
    Return the lowercase file extension.
    """

    path = Path(file_path)

    return path.suffix.lower()


def detect_mime_type(file_path: str | Path) -> str:
    """
    Detect MIME type using Python's standard mimetypes database.

    This is an initial Phase 8A detector.
    Deeper content/signature validation will be added later.
    """

    path = Path(file_path)

    mime_type, _ = mimetypes.guess_type(path.name)

    if mime_type:
        return mime_type

    return "application/octet-stream"


def detect_file_info(file_path: str | Path) -> dict:
    """
    Return basic file identification information.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return {
        "filename": path.name,
        "extension": get_file_extension(path),
        "mime_type": detect_mime_type(path),
        "size_bytes": path.stat().st_size,
    }