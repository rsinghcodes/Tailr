from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Abstract Base Class for File Storage Providers."""

    @abstractmethod
    async def save_file(self, relative_path: str, content: bytes | str) -> str:
        """Saves file content under specified relative path."""
        pass

    @abstractmethod
    async def read_file(self, relative_path: str) -> bytes:
        """Reads file content from specified relative path."""
        pass

    @abstractmethod
    async def delete_file(self, relative_path: str) -> bool:
        """Deletes file at specified relative path."""
        pass

    @abstractmethod
    async def exists(self, relative_path: str) -> bool:
        """Checks if file exists at specified relative path."""
        pass
