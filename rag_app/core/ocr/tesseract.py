import pytesseract
from PIL import Image
import io

from rag_app.core.config import TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def ocr_image_bytes(image_bytes: bytes, lang: str = "eng") -> str:
    img = Image.open(io.BytesIO(image_bytes))
    return (pytesseract.image_to_string(img, lang=lang) or "").strip()
