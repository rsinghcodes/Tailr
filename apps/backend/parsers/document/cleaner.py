import re
from langdetect import detect  # type: ignore


def clean_text(text: str) -> str:
    """Cleans and normalizes extracted text content.

    - Strips leading/trailing whitespaces.
    - Normalizes consecutive spaces to a single space.
    - Limits consecutive newlines to a maximum of two.
    - Removes non-printable/control characters except newlines and tabs.
    """
    if not text:
        return ""

    # Remove non-printable control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize consecutive horizontal spaces to a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize consecutive newlines/vertical spaces to maximum 2 newlines (preserves paragraphs)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def detect_lang(text: str) -> str:
    """Detects the primary language of the text. Falls back to 'en' on failure."""
    if not text or len(text.strip()) < 10:
        return "en"

    try:
        lang = detect(text)
        return lang if lang else "en"
    except Exception:
        return "en"
