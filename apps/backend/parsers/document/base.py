from abc import ABC, abstractmethod
from typing import Any, Dict


class DocumentParser(ABC):
    """Abstract base class representing a document parser."""

    @abstractmethod
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parses a document file and returns extracted text, metadata, and language details.

        Args:
            file_path: The absolute filesystem path to the file.

        Returns:
            A dictionary containing:
                - "text": Cleaned and normalized text content (str).
                - "metadata": Extracted document metadata (dict).
                - "language": Detected language code (str).
        """
        pass
