from dataclasses import dataclass
from typing import List

from rag_app.core.ingest.extractor import ExtractedPage


@dataclass
class TextChunk:
    page_num: int
    chunk_index: int
    text: str
    image_path: str


def chunk_pages(
    pages: List[ExtractedPage],
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[TextChunk]:
    """
    Split each page's text into chunks.
    Chunks never cross page boundaries.
    """
    chunks: List[TextChunk] = []

    for page in pages:
        text = (page.text or "").strip()

        if not text:
            continue

        start = 0
        index = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append(
                TextChunk(
                    page_num=page.page_num,
                    chunk_index=index,
                    text=chunk_text,
                    image_path=page.image_path,
                )
            )

            start = end - overlap
            index += 1

    return chunks
