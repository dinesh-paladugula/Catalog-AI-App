# rag_app/core/utils/links.py

from pathlib import Path

STATIC_BASE_URL = "http://localhost:8501/static"

def pdf_page_file_url(pdf_path: str, page: int | None = None) -> str:
    """
    Convert local pdf path to HTTP URL with optional page anchor.
    """
    name = Path(pdf_path).name
    if page:
        return f"{STATIC_BASE_URL}/{name}#page={page}"
    return f"{STATIC_BASE_URL}/{name}"
