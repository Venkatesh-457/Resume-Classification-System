"""
Document Ingestion & Text Extraction Module
Supports TXT, DOCX, Digital PDF, and Scanned PDF (with OCR fallback).
Handles validation, line normalization, and extraction quality diagnostics.
"""

from dataclasses import dataclass, field
import io
import logging
from pathlib import Path
import re
from typing import BinaryIO

import fitz  # PyMuPDF
import docx
from PIL import Image

from config.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from core.ingestion.ocr import ocr_engine

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Structured container holding extracted text and extraction metadata."""
    filename: str
    file_format: str
    file_size_bytes: int
    raw_text: str
    page_count: int = 1
    word_count: int = 0
    character_count: int = 0
    extraction_method: str = "Digital"
    ocr_used: bool = False
    is_scanned: bool = False
    warnings: list[str] = field(default_factory=list)
    success: bool = True
    error_message: str | None = None


class DocumentParsingError(Exception):
    """Raised when document ingestion or parsing fails."""
    pass


class DocumentParser:
    """Enterprise document parser for resumes with multi-format support and OCR fallback."""

    def __init__(self, ocr=ocr_engine):
        self.ocr = ocr

    def validate_file(self, filename: str, file_size: int) -> None:
        """Validate filename extension and file size constraints."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise DocumentParsingError(
                f"Unsupported format '{ext}'. Allowed file formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        if file_size <= 0:
            raise DocumentParsingError("Uploaded file is empty (0 bytes).")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise DocumentParsingError(
                f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_MB:.1f} MB."
            )

    def parse_file(self, file_obj: BinaryIO | bytes, filename: str) -> ExtractionResult:
        """
        Ingest and parse an uploaded resume file.
        Accepts binary stream or raw bytes along with the original filename.
        """
        if isinstance(file_obj, bytes):
            data = file_obj
        else:
            data = file_obj.read()

        file_size = len(data)
        self.validate_file(filename, file_size)

        ext = Path(filename).suffix.lower()
        result = ExtractionResult(
            filename=filename,
            file_format=ext.replace(".", "").upper(),
            file_size_bytes=file_size,
            raw_text="",
        )

        try:
            if ext == ".txt":
                self._parse_txt(data, result)
            elif ext == ".docx":
                self._parse_docx(data, result)
            elif ext == ".pdf":
                self._parse_pdf(data, result)
            else:
                raise DocumentParsingError(f"Handler not found for extension '{ext}'")

            # Post-extraction normalization & statistics
            result.raw_text = self._normalize_extracted_text(result.raw_text)
            result.character_count = len(result.raw_text)
            result.word_count = len(result.raw_text.split())

            # Quality and completeness checks
            if result.word_count < 25:
                result.warnings.append(
                    "Document text is unusually short (< 25 words). It may be incomplete, password protected, or an unreadable scan."
                )

        except DocumentParsingError:
            raise
        except Exception as exc:
            logger.exception("Failed to parse file %s: %s", filename, exc)
            result.success = False
            result.error_message = f"Failed to extract text: {str(exc)}"
            raise DocumentParsingError(result.error_message) from exc

        return result

    def _parse_txt(self, data: bytes, result: ExtractionResult) -> None:
        """Extract text from plain TXT file with encoding fallbacks."""
        result.extraction_method = "Direct Text"
        result.page_count = 1
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                result.raw_text = data.decode(enc)
                return
            except UnicodeDecodeError:
                continue
        # Fallback with replacement
        result.raw_text = data.decode("utf-8", errors="replace")
        result.warnings.append("Text contained non-standard characters decoded with lossy fallback.")

    def _parse_docx(self, data: bytes, result: ExtractionResult) -> None:
        """Extract text from DOCX file including paragraphs and table cells."""
        result.extraction_method = "DOCX XML Parser"
        try:
            doc = docx.Document(io.BytesIO(data))
        except Exception as e:
            raise DocumentParsingError(f"Corrupted or invalid DOCX document: {e}")

        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        # Extract text from tables as well (common in modern resumes)
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    table_texts.append(" | ".join(row_text))

        all_text = "\n".join(paragraphs)
        if table_texts:
            all_text += "\n\n" + "\n".join(table_texts)

        result.raw_text = all_text
        result.page_count = max(1, len(doc.paragraphs) // 30)

    def _parse_pdf(self, data: bytes, result: ExtractionResult) -> None:
        """
        Extract text from PDF using PyMuPDF.
        If pages contain insufficient digital text, falls back to OCR.
        """
        try:
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception as e:
            raise DocumentParsingError(f"Corrupted or invalid PDF document: {e}")

        result.page_count = len(doc)
        if result.page_count == 0:
            raise DocumentParsingError("PDF contains 0 pages.")

        page_texts = []
        scanned_pages = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text").strip()

            # Threshold for scanned page: < 35 characters of digital text
            if len(page_text) < 35:
                # Check for images or treat page as scanned
                if self.ocr.is_available:
                    logger.info("Page %d has insufficient text (%d chars). Running OCR...", page_idx + 1, len(page_text))
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = self.ocr.image_to_text(img)
                    if ocr_text:
                        page_texts.append(ocr_text)
                        scanned_pages.append(page_idx + 1)
                        result.ocr_used = True
                    else:
                        page_texts.append(page_text)
                else:
                    page_texts.append(page_text)
                    scanned_pages.append(page_idx + 1)
            else:
                page_texts.append(page_text)

        result.raw_text = "\n\n".join(page_texts)

        if scanned_pages:
            result.is_scanned = True
            if result.ocr_used:
                result.extraction_method = f"PyMuPDF + {self.ocr.version}"
                result.warnings.append(
                    f"OCR was applied on pages: {', '.join(map(str, scanned_pages))} due to sparse digital text."
                )
            else:
                result.extraction_method = "PyMuPDF (Digital Only)"
                result.warnings.append(
                    f"Pages {', '.join(map(str, scanned_pages))} appear to be scanned images. "
                    "Tesseract OCR is not installed, so text on image pages could not be extracted."
                )
        else:
            result.extraction_method = "PyMuPDF (Digital Vector)"

    def _normalize_extracted_text(self, text: str) -> str:
        """Normalize line endings, tabs, and excess whitespace."""
        if not text:
            return ""
        # Standardize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking spaces
        text = text.replace("\xa0", " ")
        # Remove null characters and non-printable control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # Collapse excessive newlines (more than 3 into 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip trailing/leading spaces on lines
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()


# Shared singleton parser instance
document_parser = DocumentParser()
