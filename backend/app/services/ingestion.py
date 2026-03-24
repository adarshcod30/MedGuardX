"""Multi-format data ingestion: HL7, text, PDF, image."""
import os
import io
from typing import Tuple

def detect_file_type(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in ('.hl7', '.adt'):
        return 'hl7'
    if ext == '.pdf':
        return 'pdf'
    if ext in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp'):
        return 'image'
    # Check content for HL7 markers
    text_preview = content[:200].decode('utf-8', errors='ignore')
    if text_preview.startswith('MSH|') or 'MSH|' in text_preview:
        return 'hl7'
    return 'text'


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            texts = [page.extract_text() or '' for page in pdf.pages]
        return '\n'.join(texts).strip()
    except Exception as e:
        return f"[PDF extraction error: {str(e)}]"


def extract_text_from_image(content: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
        import tempfile
        import os
        img = Image.open(io.BytesIO(content))
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            try:
                # Pass filename instead of image object to avoid pytesseract's internal temp file bug
                return pytesseract.image_to_string(f.name).strip()
            finally:
                os.unlink(f.name)
    except Exception as e:
        return f"[OCR error: {str(e)}]"


def parse_hl7(content: bytes) -> str:
    try:
        text = content.decode('utf-8', errors='ignore')
        from hl7apy.parser import parse_message
        msg = parse_message(text.replace('\n', '\r'))
        segments = []
        for seg in msg.children:
            seg_name = seg.name
            fields = []
            for f in seg.children:
                try:
                    fields.append(f"{f.name}: {f.value}")
                except:
                    pass
            if fields:
                segments.append(f"[{seg_name}] " + " | ".join(fields))
        return '\n'.join(segments) if segments else text
    except Exception:
        # Fallback: return raw text with basic parsing
        text = content.decode('utf-8', errors='ignore')
        return text


def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    """Returns (extracted_text, file_type)."""
    file_type = detect_file_type(filename, content)
    if file_type == 'pdf':
        text = extract_text_from_pdf(content)
    elif file_type == 'image':
        text = extract_text_from_image(content)
    elif file_type == 'hl7':
        text = parse_hl7(content)
    else:
        text = content.decode('utf-8', errors='ignore')
    return text, file_type
