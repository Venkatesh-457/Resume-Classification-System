"""
OCR Module
Provides optical character recognition support for scanned documents.
Uses RapidOCR (pure ONNX Runtime, fast, zero-dependency) with fallback to Tesseract OCR.
"""

import io
import logging
from pathlib import Path
from PIL import Image

from config.settings import TESSERACT_CMD

logger = logging.getLogger(__name__)


class OCREngine:
    """Enterprise OCR engine using RapidOCR (ONNX) with Tesseract fallback."""

    def __init__(self, tesseract_cmd: str | None = None):
        self.cmd_path = tesseract_cmd or TESSERACT_CMD
        self._rapid_ocr = None
        self._is_available = False
        self._engine_type = "None"
        self._version = "1.0"
        self._init_engine()

    def _init_engine(self) -> None:
        """Initialize RapidOCR (ONNX) or pytesseract."""
        # 1. Try RapidOCR (ONNX Runtime)
        try:
            from rapidocr_onnxruntime import RapidOCR
            self._rapid_ocr = RapidOCR()
            self._is_available = True
            self._engine_type = "RapidOCR (ONNX Runtime)"
            self._version = "RapidOCR 1.4"
            logger.info("Initialized RapidOCR engine (ONNX Runtime).")
            return
        except Exception as exc:
            logger.warning("RapidOCR unavailable (%s). Falling back to Tesseract.", exc)

        # 2. Try Tesseract OCR
        if self.cmd_path and Path(self.cmd_path).is_file():
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = str(self.cmd_path)
                version = pytesseract.get_tesseract_version()
                self._is_available = True
                self._engine_type = "Tesseract OCR"
                self._version = str(version)
                logger.info("Tesseract OCR available. Version: %s", self._version)
                return
            except Exception as exc:
                logger.warning("Tesseract binary test failed: %s", exc)

        self._is_available = False
        self._engine_type = "None"

    @property
    def is_available(self) -> bool:
        """Returns True if any OCR engine is active and functional."""
        return self._is_available

    @property
    def version(self) -> str | None:
        """Returns active OCR engine type and version."""
        return self._engine_type

    def get_status_info(self) -> dict:
        """Diagnostic dictionary explaining OCR status and setup steps."""
        return {
            "available": self._is_available,
            "engine": self._engine_type,
            "version": self._version,
            "setup_guide": (
                "OCR Engine is active and ready to process scanned image resumes."
                if self._is_available else
                "No OCR engine is currently detected. Install rapidocr-onnxruntime or Tesseract OCR."
            )
        }

    def image_to_text(self, image: Image.Image | bytes) -> str:
        """
        Extract text from a PIL Image or image bytes.
        """
        if not self._is_available:
            logger.warning("OCR requested but no OCR engine is available.")
            return ""

        # Use RapidOCR if available
        if self._rapid_ocr is not None:
            try:
                if isinstance(image, Image.Image):
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    img_bytes = buf.getvalue()
                else:
                    img_bytes = image

                result, _ = self._rapid_ocr(img_bytes)
                if result:
                    lines = [line[1] for line in result]
                    return "\n".join(lines).strip()
                return ""
            except Exception as exc:
                logger.error("RapidOCR extraction failed: %s", exc)

        # Fallback to pytesseract
        try:
            import pytesseract
            if isinstance(image, bytes):
                pil_img = Image.open(io.BytesIO(image))
            else:
                pil_img = image
            return pytesseract.image_to_string(pil_img, lang="eng").strip()
        except Exception as exc:
            logger.error("Tesseract OCR extraction failed: %s", exc)
            return ""


# Shared singleton instance
ocr_engine = OCREngine()
