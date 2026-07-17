import os
from typing import Dict, Type
from parsers.document.base import DocumentParser
from parsers.document.pdf import PDFDocumentParser
from parsers.document.docx import DocxDocumentParser
from parsers.document.txt import TxtDocumentParser


class DocumentParserFactory:
    """Factory class to select the correct parser based on file extension or MIME type."""

    def __init__(self):
        self._parsers: Dict[str, Type[DocumentParser]] = {
            ".pdf": PDFDocumentParser,
            ".docx": DocxDocumentParser,
            ".txt": TxtDocumentParser,
        }

    def get_parser(self, file_path: str) -> DocumentParser:
        """Selects the correct parser instance for the given file path.

        Args:
            file_path: Absolute path to the file.

        Returns:
            An instance of DocumentParser.

        Raises:
            ValueError: If the file type is unsupported.
        """
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self._parsers:
            raise ValueError(f"Unsupported file type: '{ext}'. Supported types are: .pdf, .docx, .txt")

        parser_cls = self._parsers[ext]
        return parser_cls()
