from typing import Dict, Any, List

from rag_app.core.ingest.pdf_loader import load_pdf_pages
from rag_app.core.ingest.extractor import extract_pages_with_ocr
from rag_app.core.ingest.chunker import chunk_pages
from rag_app.core.ingest.embeddings import embed_texts
from rag_app.core.storage.mongo import get_collection

def ingest_pdf(
    pdf_path: str,
    tenant_id: str,
    doc_id: str,
    ocr_lang: str = "eng",
    chunk_size: int = 500,
    overlap: int = 50,
) -> Dict[str, Any]:
    """
    Ingest a PDF with OCR (mandatory).
    Stores chunks with vectors in MongoDB.
    """

    # 1) Load pages as images (+ saved page png paths)
    pages = load_pdf_pages(pdf_path=pdf_path, doc_id=doc_id)

    # 2) OCR every page (mandatory)
    extracted_pages = extract_pages_with_ocr(pages, ocr_lang=ocr_lang)

    # 3) Chunk per page
    chunks = chunk_pages(extracted_pages, chunk_size=chunk_size, overlap=overlap)

    # 4) Embeddings
    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)

    # 5) Store in MongoDB
    col = get_collection()

    docs_to_insert: List[Dict[str, Any]] = []
    for c, v in zip(chunks, vectors):
        docs_to_insert.append(
            {
                "tenant_id": tenant_id,
                "doc_id": doc_id,
                "page_num": c.page_num,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "embedding": v,
                "image_path": c.image_path,   # Streamlit can show this image
                "source_pdf": pdf_path,
            }
        )

    if docs_to_insert:
        col.insert_many(docs_to_insert)

    return {
        "pdf_path": pdf_path,
        "tenant_id": tenant_id,
        "doc_id": doc_id,
        "pages": len(pages),
        "chunks_inserted": len(docs_to_insert),
    }
