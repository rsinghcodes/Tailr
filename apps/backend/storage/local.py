import os
from pathlib import Path
from storage.base import StorageProvider
from storage.exceptions import FileNotFoundStorageError, InvalidPathError


class LocalStorageProvider(StorageProvider):
    """Local file system storage implementation with strict path sanitization."""

    def __init__(self, root_dir: str | Path | None = None):
        base_path = root_dir or os.getenv("STORAGE_DIR", "storage_data")
        self.root_dir = Path(base_path).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_path(self, relative_path: str) -> Path:
        """Resolves and validates relative path to prevent path traversal."""
        clean_rel = relative_path.lstrip("/\\")
        target_path = (self.root_dir / clean_rel).resolve()

        if not str(target_path).startswith(str(self.root_dir)):
            raise InvalidPathError(f"Path traversal detected for relative path: '{relative_path}'")

        return target_path

    async def save_file(self, relative_path: str, content: bytes | str) -> str:
        target_path = self._sanitize_path(relative_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, str):
            target_path.write_text(content, encoding="utf-8")
        else:
            target_path.write_bytes(content)

        return str(target_path)

    async def read_file(self, relative_path: str) -> bytes:
        target_path = self._sanitize_path(relative_path)

        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundStorageError(f"File not found: '{relative_path}'")

        return target_path.read_bytes()

    async def delete_file(self, relative_path: str) -> bool:
        try:
            target_path = self._sanitize_path(relative_path)
            if target_path.exists() and target_path.is_file():
                target_path.unlink()
                return True
        except (InvalidPathError, FileNotFoundStorageError):
            pass
        return False

    async def exists(self, relative_path: str) -> bool:
        try:
            target_path = self._sanitize_path(relative_path)
            return target_path.exists() and target_path.is_file()
        except InvalidPathError:
            return False
