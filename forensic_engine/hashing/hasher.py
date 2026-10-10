from pathlib import Path
import hashlib


DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MB


def calculate_sha256(
    file_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read in chunks so large forensic evidence files
    do not need to be loaded completely into memory.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()