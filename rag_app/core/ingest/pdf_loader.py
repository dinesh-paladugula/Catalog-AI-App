from dataclasses import dataclass
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from langchain_community.document_loaders import PyMuPDFLoader


@dataclass
class PdfPage:
    page_num: int           # 1-based page number
    native_text: str        # extracted text if available (may be empty)
    image_bytes: bytes      # rendered page as PNG bytes (for OCR)
    image_path: str         # where the page image is saved (for Streamlit preview)


def load_pdf_pages(pdf_path: str, doc_id: str, out_dir: str = "storage/images", dpi: int = 200) -> List[PdfPage]:
    pdf_path = Path(pdf_path)

    # 1) Native text using LangChain loader (per page)
    loader = PyMuPDFLoader(str(pdf_path))
    docs = loader.load()  # each doc = one page (usually)

    # Build list of native texts by page index (0-based)
    native_by_page = {}
    for d in docs:
        idx = d.metadata.get("page", 0)  # 0-based
        native_by_page[int(idx)] = (d.page_content or "").strip()

    # 2) Render pages as images using PyMuPDF
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    # Create folder: storage/images/<doc_id>/
    image_folder = Path(out_dir) / doc_id
    image_folder.mkdir(parents=True, exist_ok=True)

    pages: List[PdfPage] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for i in range(total_pages):
        page_num = i + 1

        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")

        img_path = image_folder / f"page_{page_num}.png"
        img_path.write_bytes(img_bytes)

        pages.append(
            PdfPage(
                page_num=page_num,
                native_text=native_by_page.get(i, ""),
                image_bytes=img_bytes,
                image_path=str(img_path),
            )
        )

    doc.close()
    return pages
