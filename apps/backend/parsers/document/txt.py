import os
from typing import Any, Dict
from parsers.document.base import DocumentParser
from parsers.document.cleaner import clean_text, detect_lang


class TxtDocumentParser(DocumentParser):
    """Parses plain text (.txt) files."""

    async def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Text file not found at: {file_path}")

        raw_content = ""
        # Try UTF-8 first
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except UnicodeDecodeError:
            # Fallback to Windows-1252 with error ignore
            with open(file_path, "r", encoding="cp1252", errors="ignore") as f:
                raw_content = f.read()

        cleaned = clean_text(raw_content)
        language = detect_lang(cleaned)

        # Extract basic metadata
        stat = os.stat(file_path)
        metadata = {
            "filename": os.path.basename(file_path),
            "file_size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "mime_type": "text/plain",
        }

        return {
            "text": cleaned,
            "metadata": metadata,
            "language": language,
        }
