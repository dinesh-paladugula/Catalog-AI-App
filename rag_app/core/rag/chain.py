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
    k: int = 15,  # High k for better coverage
    index_name: str = "vector_index",
    page_num: Optional[int] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Main RAG chain to answer user questions with strict formatting rules.
    """

    # -------------------------
    # 1) Retrieve
    # -------------------------
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

    # -------------------------
    # 2) Build context + citations
    # -------------------------
    context_blocks: List[str] = []
    citations: List[Dict[str, Any]] = []
    image_paths: List[str] = []
    primary_pdf_link: Optional[str] = None

    def build_pdf_link(page: Optional[int]) -> Optional[str]:
        if page is None or not doc_id:
            return None
        return pdf_page_file_url(doc_id, int(page))

    for r in retrieved:
        page = r.get("page_num")
        img = r.get("image_path")
        txt = (r.get("text") or "").strip()

        context_blocks.append(f"[SOURCE: Page {page}]\n{txt}\n[END SOURCE]")

        pdf_link = build_pdf_link(page)

        if pdf_link and primary_pdf_link is None:
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

    # -------------------------
    # 3) DIMENSION MODE (Specialized extraction)
    # -------------------------
    if is_dimension_question(question):
        found = best_dimension_from_retrieved(retrieved, question)

        if found:
            dim, row = found
            page = row.get("page_num")
            pdf_link = build_pdf_link(page)
            img = row.get("image_path")

            answer = f'The {dim["room"]} dimension is {dim["value"]} (Page {page}).'

            return {
                "answer": answer,
                "citations": citations,
                "image_paths": [img] if img else image_paths,
                "primary_pdf_link": pdf_link or primary_pdf_link,
                "retrieved": retrieved,
            }

    # -------------------------
    # 4) Normal LLM Mode (Refined for conciseness)
    # -------------------------
    context = "\n\n".join(context_blocks)
    
    is_first_message = not chat_history or len(chat_history) == 0

    prompt = f"""
SYSTEM: You are a direct, factual data extraction engine for the "My Home Tridasa" brochure.
TASK: Answer the user's question using ONLY the provided context.

STRICT FORMATTING RULES:
1. NO GREETINGS. No "Hello", "Hi", "Welcome".
2. NO FILLERS. No "Based on the brochure", "I found that".
3. NO BULLET POINTS. Provide the answer in a single, well-structured paragraph.
4. BE CONCISE. Avoid unnecessary details. If multiple facts are requested, join them with commas or semicolons in a paragraph.
5. CITATIONS: Cite the page number in parentheses at the end of relevant sentences, e.g., (Page 5).
6. START IMMEDIATELY with the answer.
7. GREETING EXCEPTION: ONLY if the user's message is just a greeting AND this is the start of the conversation, respond with: "I am the My Home Tridasa assistant. How can I help you with project details?"

CONTEXT:
{context}

USER QUESTION:
{question}

FINAL ANSWER (Paragraph form, Direct and Factual):
""".strip()

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")
    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL is not set in .env")

    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    answer = resp.choices[0].message.content.strip()

    return {
        "answer": answer,
        "citations": citations,
        "image_paths": image_paths,
        "primary_pdf_link": primary_pdf_link,
        "retrieved": retrieved,
    }
