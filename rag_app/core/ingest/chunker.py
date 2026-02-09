from dataclasses import dataclass
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_app.core.ingest.extractor import ExtractedPage


@dataclass
class TextChunk:
    page_num: int
    chunk_index: int
    text: str
    image_path: str


def chunk_pages(
    pages: List[ExtractedPage],
    chunk_size: int = 800, # Increased for better context
    overlap: int = 100,
) -> List[TextChunk]:
    """
    Split each page's text into chunks using RecursiveCharacterTextSplitter.
    Chunks never cross page boundaries to maintain image context.
    
    IMPROVEMENTS:
    - Uses RecursiveCharacterTextSplitter for smarter splitting.
    - Optimized separators to avoid cutting words or important layout markers.
    - Increased default chunk size for richer context.
    """
    chunks: List[TextChunk] = []
    
    # Initialize the splitter with meaningful separators
    # Order matters: split by double newline first, then single, then sentence markers
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )

    for page in pages:
        text = (page.text or "").strip()

        if not text:
            # For pages with no text (e.g., pure image pages like Site Plan),
            # we still want to keep them in the index so they can be retrieved by metadata
            # or if the retriever supports image-only chunks.
            # Adding a placeholder for the page.
            chunks.append(
                TextChunk(
                    page_num=page.page_num,
                    chunk_index=0,
                    text=f"Page {page.page_num} content (Image only or layout page)",
                    image_path=page.image_path,
                )
            )
            continue

        # Split the text into parts
        page_chunks = splitter.split_text(text)

        for index, chunk_text in enumerate(page_chunks):
            # Prepend page information to the chunk text to help the LLM and vector search
            # This makes the chunk "self-describing"
            enhanced_text = f"[Page {page.page_num}]\n{chunk_text}"
            
            chunks.append(
                TextChunk(
                    page_num=page.page_num,
                    chunk_index=index,
                    text=enhanced_text,
                    image_path=page.image_path,
                )
            )

    return chunks
