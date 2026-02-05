from rag_app.core.rag.chain import answer_question

# Option A: if you know the exact page you want, set page_num=10 (example).
# If you don't know the page yet, keep page_num=None (default) for normal retrieval.
res = answer_question(
    "Master bedroom dimensions for 2BHK east facing",
    tenant_id="tenant_01",
    doc_id="sample_01",
    k=5,
    index_name="vector_index",
)

print("\nANSWER:\n", res["answer"])

print("\nPRIMARY PDF LINK:\n", res.get("primary_pdf_link"))

print("\nCITATIONS:")
for c in res["citations"]:
    print(
        f'- Page {c.get("page_num")} | chunk {c.get("chunk_index")} | score {c.get("score")}\n'
        f'  PDF: {c.get("pdf_link")}\n'
        f'  Image: {c.get("image_path")}\n'
    )

print("\nIMAGES (unique):\n", res["image_paths"])

print("\nTOP CHUNKS:")
for r in res["retrieved"]:
    print("score:", r.get("score"), "| page:", r.get("page_num"), "| chunk:", r.get("chunk_index"))
    print((r.get("text") or "")[:180])
    print("PDF:", r.get("source_pdf"))
    print("IMG:", r.get("image_path"))
    print("-" * 50)
