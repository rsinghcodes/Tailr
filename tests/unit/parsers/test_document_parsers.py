import pytest
import zipfile
from unittest.mock import MagicMock, patch
from parsers.document.cleaner import clean_text, detect_lang
from parsers.document.txt import TxtDocumentParser
from parsers.document.docx import DocxDocumentParser
from parsers.document.pdf import PDFDocumentParser
from parsers.document.factory import DocumentParserFactory


def test_clean_text():
    raw = "\x00Hello   world!\n\n\nNew Paragraph. \t"
    cleaned = clean_text(raw)
    assert cleaned == "Hello world!\n\nNew Paragraph."


def test_detect_lang():
    # English text
    assert detect_lang("The quick brown fox jumps over the lazy dog.") == "en"
    # Spanish text
    assert detect_lang("El zorro marrón rápido salta sobre el perro perezoso.") == "es"


@pytest.mark.asyncio
async def test_txt_parser(tmp_path):
    txt_path = tmp_path / "test.txt"
    content = "Hello, this is plain text.\n"
    txt_path.write_text(content, encoding="utf-8")

    parser = TxtDocumentParser()
    result = await parser.parse(str(txt_path))

    assert result["text"] == "Hello, this is plain text."
    assert result["metadata"]["filename"] == "test.txt"
    assert result["metadata"]["mime_type"] == "text/plain"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_docx_parser(tmp_path):
    docx_path = tmp_path / "test.docx"
    
    # Create mock DOCX zip archive
    with zipfile.ZipFile(docx_path, "w") as z:
        z.writestr("word/document.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                <w:p>
                    <w:r>
                        <w:t>Hello world from DOCX</w:t>
                    </w:r>
                </w:p>
            </w:body>
        </w:document>""")
        z.writestr("docProps/core.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                           xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:creator>Test Author</dc:creator>
            <dc:title>Test Title</dc:title>
        </cp:coreProperties>""")

    parser = DocxDocumentParser()
    result = await parser.parse(str(docx_path))

    assert result["text"] == "Hello world from DOCX"
    assert result["metadata"]["filename"] == "test.docx"
    assert result["metadata"]["author"] == "Test Author"
    assert result["metadata"]["title"] == "Test Title"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_docx_parser_corrupted(tmp_path):
    docx_path = tmp_path / "corrupt.docx"
    docx_path.write_bytes(b"invalid zip file bytes")

    parser = DocxDocumentParser()
    with pytest.raises(ValueError, match="Corrupted DOCX"):
        await parser.parse(str(docx_path))


@pytest.mark.asyncio
async def test_pdf_parser(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy bytes")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Extracted PDF text content."
    
    mock_metadata = MagicMock()
    mock_metadata.title = "PDF Title"
    mock_metadata.author = "PDF Author"
    mock_metadata.creator = None
    mock_metadata.producer = None

    with patch("parsers.document.pdf.PdfReader") as mock_reader_cls:
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader.metadata = mock_metadata
        mock_reader_cls.return_value = mock_reader

        parser = PDFDocumentParser()
        result = await parser.parse(str(pdf_path))

        assert result["text"] == "Extracted PDF text content."
        assert result["metadata"]["filename"] == "test.pdf"
        assert result["metadata"]["title"] == "PDF Title"
        assert result["metadata"]["author"] == "PDF Author"
        assert result["metadata"]["page_count"] == 1


def test_parser_factory():
    factory = DocumentParserFactory()

    assert isinstance(factory.get_parser("test.txt"), TxtDocumentParser)
    assert isinstance(factory.get_parser("test.docx"), DocxDocumentParser)
    assert isinstance(factory.get_parser("test.pdf"), PDFDocumentParser)

    with pytest.raises(ValueError, match="Unsupported file type"):
        factory.get_parser("test.png")
