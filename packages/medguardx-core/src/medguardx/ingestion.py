"""Multi-format text extraction: plain text, PDF, image (OCR), HL7.

Optional heavy dependencies (pdfplumber, pytesseract/Pillow, hl7apy) are imported
lazily and degrade gracefully, so installing the core engine does not force an
OCR/PDF toolchain on integrators who only mask plain text.
"""
from __future__ import annotations

import io
import os
from typing import Tuple


def detect_file_type(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in (".hl7", ".adt"):
        return "hl7"
    if ext == ".pdf":
        return "pdf"
    if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return "image"
    preview = content[:200].decode("utf-8", errors="ignore")
    if "MSH|" in preview:
        return "hl7"
    return "text"


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except Exception as exc:  # pragma: no cover - depends on optional dep
        return f"[PDF extraction error: {exc}]"


def extract_text_from_image(content: bytes) -> str:
    try:
        import tempfile

        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(content))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
            img.save(fh.name)
            try:
                return pytesseract.image_to_string(fh.name).strip()
            finally:
                os.unlink(fh.name)
    except Exception as exc:  # pragma: no cover - depends on optional dep
        return f"[OCR error: {exc}]"


def parse_hl7(content: bytes) -> str:
    text = content.decode("utf-8", errors="ignore")
    try:
        from hl7apy.parser import parse_message

        msg = parse_message(text.replace("\n", "\r"))
        segments = []
        for seg in msg.children:
            fields = []
            for field in seg.children:
                try:
                    fields.append(f"{field.name}: {field.value}")
                except Exception:
                    pass
            if fields:
                segments.append(f"[{seg.name}] " + " | ".join(fields))
        return "\n".join(segments) if segments else text
    except Exception:  # pragma: no cover - depends on optional dep
        return text


def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    """Return ``(extracted_text, file_type)`` for an uploaded file."""
    file_type = detect_file_type(filename, content)
    if file_type == "pdf":
        return extract_text_from_pdf(content), file_type
    if file_type == "image":
        return extract_text_from_image(content), file_type
    if file_type == "hl7":
        return parse_hl7(content), file_type
    return content.decode("utf-8", errors="ignore"), file_type
