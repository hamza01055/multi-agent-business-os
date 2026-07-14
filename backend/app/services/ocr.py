"""OCR pipeline: PDF/image → text via Tesseract."""
from pathlib import Path
import pytesseract
from PIL import Image
from app.core.config import settings


def _pdf_to_images(path: str):
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(path)
    for page in pdf:
        yield page.render(scale=2.5).to_pil()


def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        pages = [
            pytesseract.image_to_string(img, lang=settings.OCR_LANGS)
            for img in _pdf_to_images(path)
        ]
        return "\n\n".join(pages)
    return pytesseract.image_to_string(Image.open(path), lang=settings.OCR_LANGS)
