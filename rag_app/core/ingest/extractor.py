# rag_app/core/ingest/extractor.py
# Beginner version: ALWAYS OCR, no native text logic

from dataclasses import dataclass
from typing import List

from rag_app.core.ingest.pdf_loader import PdfPage
from rag_app.core.ocr.tesseract import ocr_image_bytes


@dataclass
class ExtractedPage:
    page_num: int
    text: str
    image_path: str


def extract_pages_with_ocr(
    pages: List[PdfPage],
    ocr_lang: str = "eng",
) -> List[ExtractedPage]:
    """
    Always runs OCR on every page image.
    """
    extracted: List[ExtractedPage] = []

    for page in pages:
        text = ocr_image_bytes(page.image_bytes, lang=ocr_lang)

        extracted.append(
            ExtractedPage(
                page_num=page.page_num,
                text=text,
                image_path=page.image_path,
            )
        )

    return extracted
