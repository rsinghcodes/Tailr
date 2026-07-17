import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try optional imports
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract  # type: ignore
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


class OCRProvider:
    """Handles Optical Character Recognition (OCR) for scanned documents/images."""

    def __init__(self):
        self.is_available = HAS_PIL and HAS_TESSERACT
        if self.is_available:
            try:
                # Test Tesseract execution
                pytesseract.get_tesseract_version()
            except Exception:
                logger.info("pytesseract is installed but Tesseract-OCR binary was not found on path.")
                self.is_available = False

    def perform_ocr(self, image_data: bytes) -> Optional[str]:
        """Performs OCR on an image byte stream.

        Args:
            image_data: Bytes representing the image file.

        Returns:
            The extracted text string, or None if OCR is unavailable or fails.
        """
        if not self.is_available:
            logger.info("OCR is not available (either pillow/pytesseract missing or Tesseract not on path).")
            return None

        try:
            import io
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as exc:
            logger.warning("OCR processing failed: %s", str(exc))
            return None
