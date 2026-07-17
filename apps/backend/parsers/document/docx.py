import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict
from parsers.document.base import DocumentParser
from parsers.document.cleaner import clean_text, detect_lang


class DocxDocumentParser(DocumentParser):
    """Parses Microsoft Word (.docx) files using python standard library zipfile and XML parsing."""

    async def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DOCX file not found at: {file_path}")

        paragraphs = []
        metadata: Dict[str, Any] = {
            "filename": os.path.basename(file_path),
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        # Namespaces map
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcterms": "http://purl.org/dc/terms/",
        }

        try:
            with zipfile.ZipFile(file_path) as z:
                # 1. Parse text from word/document.xml
                if "word/document.xml" in z.namelist():
                    xml_content = z.read("word/document.xml")
                    root = ET.fromstring(xml_content)
                    
                    for p in root.findall(".//w:p", namespaces):
                        texts = [t.text for t in p.findall(".//w:t", namespaces) if t.text]
                        if texts:
                            paragraphs.append("".join(texts))
                else:
                    raise ValueError("Invalid DOCX archive: word/document.xml is missing.")

                # 2. Extract metadata from docProps/core.xml (optional)
                if "docProps/core.xml" in z.namelist():
                    core_xml = z.read("docProps/core.xml")
                    core_root = ET.fromstring(core_xml)
                    
                    creator_node = core_root.find(".//dc:creator", namespaces)
                    if creator_node is not None and creator_node.text:
                        metadata["author"] = creator_node.text

                    title_node = core_root.find(".//dc:title", namespaces)
                    if title_node is not None and title_node.text:
                        metadata["title"] = title_node.text

                    created_node = core_root.find(".//dcterms:created", namespaces)
                    if created_node is not None and created_node.text:
                        metadata["created"] = created_node.text

                    modified_node = core_root.find(".//dcterms:modified", namespaces)
                    if modified_node is not None and modified_node.text:
                        metadata["modified"] = modified_node.text
        except zipfile.BadZipFile as exc:
            raise ValueError(f"Corrupted DOCX file: {str(exc)}") from exc
        except Exception as exc:
            raise ValueError(f"Failed to parse DOCX file: {str(exc)}") from exc

        raw_text = "\n".join(paragraphs)
        cleaned = clean_text(raw_text)
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
