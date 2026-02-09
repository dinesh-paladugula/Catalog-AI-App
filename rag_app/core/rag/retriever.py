from typing import Any, Dict, List, Optional
from rag_app.core.storage.mongo import get_collection
from rag_app.core.ingest.embeddings import embed_query


def retrieve_chunks(
    query: str,
    *,
    tenant_id: str,
    doc_id: Optional[str] = None,
    k: int = 5,
    index_name: str = "vector_index",
    num_candidates: int = 100,
) -> List[Dict[str, Any]]:
    col = get_collection()
    qvec = embed_query(query)

    flt: Dict[str, Any] = {"tenant_id": tenant_id}
    if doc_id:
        flt["doc_id"] = doc_id

    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": qvec,
                "numCandidates": num_candidates,
                "limit": k,
                "filter": flt,
            }
        },
        {
            "$project": {
                "_id": 0,
                "tenant_id": 1,
                "doc_id": 1,
                "page_num": 1,
                "chunk_index": 1,
                "text": 1,
                "image_path": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(col.aggregate(pipeline))


def retrieve_page_chunks(
    query: str,
    *,
    tenant_id: str,
    doc_id: str,
    page_num: int,
    k: int = 5,
    index_name: str = "vector_index",
    num_candidates: int = 100,
) -> List[Dict[str, Any]]:
    col = get_collection()
    qvec = embed_query(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": qvec,
                "numCandidates": num_candidates,
                "limit": k,
                "filter": {
                    "tenant_id": tenant_id,
                    "doc_id": doc_id,
                    "page_num": page_num,
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "tenant_id": 1,
                "doc_id": 1,
                "page_num": 1,
                "chunk_index": 1,
                "text": 1,
                "image_path": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(col.aggregate(pipeline))
