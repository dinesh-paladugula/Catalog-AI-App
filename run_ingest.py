from rag_app.core.ingest.pipeline import ingest_pdf

result = ingest_pdf(
    pdf_path="rag_app/data/raw/My-Home-Tridasa-E-Brochure.pdf",
    tenant_id="tenant_01",
    doc_id="My-Home-Tridasa-E-Brochure",
    ocr_lang="eng",
)

print(result)
