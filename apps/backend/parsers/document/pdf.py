import os
import logging
from typing import Any, Dict
from pypdf import PdfReader
from parsers.document.base import DocumentParser
from parsers.document.cleaner import clean_text, detect_lang
from parsers.document.ocr import OCRProvider

logger = logging.getLogger(__name__)


class PDFDocumentParser(DocumentParser):
    """Parses PDF (.pdf) files using the pypdf library, with page-by-page text extraction and metadata retrieval."""

    def __init__(self, ocr_provider: OCRProvider = OCRProvider()):
        self.ocr_provider = ocr_provider

    async def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        pages_text = []
        metadata: Dict[str, Any] = {
            "filename": os.path.basename(file_path),
            "mime_type": "application/pdf",
        }

        try:
            reader = PdfReader(file_path)
            metadata["page_count"] = len(reader.pages)

            # 1. Extract metadata from PDF document properties
            info = reader.metadata
            if info:
                if info.title:
                    metadata["title"] = info.title
                if info.author:
                    metadata["author"] = info.author
                if info.creator:
                    metadata["creator"] = info.creator
                if info.producer:
                    metadata["producer"] = info.producer

            # 2. Extract text page-by-page
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # Check for low text density (potential scanned image PDF page)
                if not text or len(text.strip()) < 20:
                    logger.info("Page %d has low text density, checking for image content to run OCR...", idx + 1)
                    ocr_page_texts = []
                    # Try extraction via OCR if images exist on the page
                    if hasattr(page, "images") and page.images:
                        for img in page.images:
                            ocr_text = self.ocr_provider.perform_ocr(img.data)
                            if ocr_text:
                                ocr_page_texts.append(ocr_text)
                    if ocr_page_texts:
                        text = "\n".join(ocr_page_texts)

                if text:
                    pages_text.append(text)
        except Exception as exc:
            raise ValueError(f"Failed to parse PDF file: {str(exc)}") from exc

        full_text = "\n\n".join(pages_text)
        cleaned = clean_text(full_text)
        language = detect_lang(cleaned)

        stat = os.stat(file_path)
        metadata.update({
            "file_size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
        })

        return {
            "text": cleaned,
            "metadata": metadata,
            "language": language,
        }
