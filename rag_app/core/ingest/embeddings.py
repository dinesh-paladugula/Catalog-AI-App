# rag_app/core/ingest/embeddings.py

import time
from typing import List
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from rag_app.core.config import HUGGINGFACE_API_KEY, HUGGINGFACE_EMBED_MODEL


def get_embedder() -> HuggingFaceEndpointEmbeddings:
    if not HUGGINGFACE_API_KEY:
        raise ValueError("HUGGINGFACE_API_KEY is not set")

    return HuggingFaceEndpointEmbeddings(
        model=HUGGINGFACE_EMBED_MODEL,
        task="feature-extraction",
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
    )


def embed_texts(texts: List[str], batch_size: int = 8, retries: int = 5) -> List[List[float]]:
    """
    Embed texts using HF Inference API in small batches to avoid 504 timeouts.
    """
    embedder = get_embedder()
    all_vectors: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]

        for attempt in range(retries):
            try:
                vecs = embedder.embed_documents(batch)
                all_vectors.extend(vecs)
                break
            except Exception as e:
                # simple backoff: 1s, 2s, 4s, 8s...
                sleep_s = 2 ** attempt
                print(f"HF embed failed (batch {i//batch_size}, attempt {attempt+1}/{retries}): {e}")
                time.sleep(sleep_s)
        else:
            raise RuntimeError("HuggingFace embeddings failed after retries")

    return all_vectors


def embed_query(query: str, retries: int = 5) -> List[float]:
    embedder = get_embedder()

    for attempt in range(retries):
        try:
            return embedder.embed_query(query)
        except Exception as e:
            time.sleep(2 ** attempt)
            print(f"HF query embed failed attempt {attempt+1}/{retries}: {e}")

    raise RuntimeError("HuggingFace query embedding failed after retries")
