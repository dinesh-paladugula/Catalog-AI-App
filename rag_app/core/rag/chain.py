# rag_app/core/rag/chain.py

from typing import Any, Dict, List, Optional

from groq import Groq

from rag_app.core.config import GROQ_API_KEY, GROQ_MODEL
from rag_app.core.rag.retriever import retrieve_chunks, retrieve_page_chunks
from rag_app.core.utils.links import pdf_page_file_url
from rag_app.core.rag.dimensions import is_dimension_question, best_dimension_from_retrieved

def answer_question(
    question: str,
    *,
    tenant_id: str,
    doc_id: Optional[str] = None,
    k: int = 5,
    index_name: str = "vector_index",
    page_num: Optional[int] = None,
) -> Dict[str, Any]:
    """
    If page_num is provided -> strict page-locked retrieval (Option A).
    Else -> normal retrieval.

    Returns:
      - answer
      - citations (page numbers + pdf_link + image_path)
      - image_paths (unique)
      - retrieved (raw chunks + scores)
      - primary_pdf_link
    """

    # 1) Retrieve
    if page_num is not None:
        if not doc_id:
            raise ValueError("doc_id is required when page_num is provided")

        retrieved = retrieve_page_chunks(
            question,
            tenant_id=tenant_id,
            doc_id=doc_id,
            page_num=page_num,
            k=k,
            index_name=index_name,
        )
    else:
        retrieved = retrieve_chunks(
            question,
            tenant_id=tenant_id,
            doc_id=doc_id,
            k=k,
            index_name=index_name,
        )

    # 2) Build context + citations + image list (+ pdf links)
    context_blocks: List[str] = []
    citations: List[Dict[str, Any]] = []
    image_paths: List[str] = []
    primary_pdf_link: Optional[str] = None

    for r in retrieved:
        page = r.get("page_num")
        img = r.get("image_path")
        txt = (r.get("text") or "").strip()
        source_pdf = r.get("source_pdf")

        context_blocks.append(f"[Page {page}] {txt}")

        pdf_link = None
        if source_pdf and page is not None:
            pdf_link = pdf_page_file_url(source_pdf, int(page))
            if primary_pdf_link is None:
                primary_pdf_link = pdf_link

        citations.append(
            {
                "page_num": page,
                "chunk_index": r.get("chunk_index"),
                "score": r.get("score"),
                "image_path": img,
                "pdf_link": pdf_link,
            }
        )

        if img and img not in image_paths:
            image_paths.append(img)

    # 3) DIMENSION MODE (deterministic): answer only if OCR contains it, else refer image
    if is_dimension_question(question):
        found = best_dimension_from_retrieved(retrieved, question)

        if found:
            dim, row = found
            page = row.get("page_num")
            pdf_link = None
            if row.get("source_pdf") and page is not None:
                pdf_link = pdf_page_file_url(row["source_pdf"], int(page))

            answer = f'{dim["room"]}: {dim["value"]} (Page {page})'
            return {
                "answer": answer,
                "citations": citations,
                "image_paths": image_paths,
                "primary_pdf_link": pdf_link or primary_pdf_link,
                "retrieved": retrieved,
            }

        # Not found in OCR -> refer image (no guessing)
        top = retrieved[0] if retrieved else {}
        page = top.get("page_num")
        pdf_link = None
        if top.get("source_pdf") and page is not None:
            pdf_link = pdf_page_file_url(top["source_pdf"], int(page))

        answer = (
            "Room dimensions are not available in extracted OCR text. "
            f"Please refer to the floor-plan image. (Page {page})"
        )
        return {
            "answer": answer,
            "citations": citations,
            "image_paths": image_paths,
            "primary_pdf_link": pdf_link or primary_pdf_link,
            "retrieved": retrieved,
        }

    # 4) Normal brochure extraction via LLM
    context = "\n\n".join(context_blocks)

    prompt = f"""
You are a brochure-aware assistant.

Your role:
- Help users explore flat options step by step.
- Speak ONLY using information present in the brochure OCR.
- Do NOT add marketing language, amenities, schools, or assumptions.
- Do NOT repeat greetings after the first message.

Conversation rules:
- If the user greets (e.g., "hi", "hello"), respond briefly and explain what you can help with.
- If the user expresses interest (e.g., "I want 3BHK"), ask clarifying questions BEFORE listing results.
- Only list flats when enough details are known (BHK, facing if relevant).
- Only include page numbers and PDF references when presenting factual matches.
- If no exact match is confirmed yet, do NOT show images or links.

When listing flats, use this format:
- FLAT NO <n> | <BHK> | <FACING> | <AREA> (Page X)

If information is not present in the brochure OCR, say so clearly.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")
    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL is not set in .env")

    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = resp.choices[0].message.content.strip()

    return {
        "answer": answer,
        "citations": citations,
        "image_paths": image_paths,
        "primary_pdf_link": primary_pdf_link,
        "retrieved": retrieved,
    }
