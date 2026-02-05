import streamlit as st

from rag_app.core.rag.chain import answer_question


st.set_page_config(
    page_title="Catalog AI - Brochure Q&A",
    layout="wide",
)

st.title("🏢 Catalog AI - Brochure Q&A")

# -------------------------
# Inputs
# -------------------------
question = st.text_input(
    "Ask a question about the brochure",
    placeholder="e.g. Show 2BHK east facing flats",
)

col1, col2, col3 = st.columns(3)

with col1:
    tenant_id = st.text_input("Tenant ID", value="tenant_01")

with col2:
    doc_id = st.text_input("Document ID", value="sample_01")

with col3:
    page_num = st.number_input(
        "Page number (optional)",
        min_value=1,
        step=1,
        value=None,
        placeholder="Leave empty for auto",
    )

submit = st.button("Search")

# -------------------------
# Action
# -------------------------
if submit and question:
    with st.spinner("Searching brochure…"):
        res = answer_question(
            question,
            tenant_id=tenant_id,
            doc_id=doc_id,
            page_num=int(page_num) if page_num else None,
            k=5,
            index_name="vector_index",
        )

    # -------------------------
    # Answer
    # -------------------------
    st.subheader("Answer")
    st.write(res["answer"])

    # -------------------------
    # Primary PDF link
    # -------------------------
    if res.get("primary_pdf_link"):
        st.markdown(
            f"📄 **Primary PDF page:** "
            f"[Open page]({res['primary_pdf_link']})"
        )

    # -------------------------
    # Images
    # -------------------------
    if res.get("image_paths"):
        st.subheader("Floor Plan Images")
        for img_path in res["image_paths"]:
            st.image(img_path, use_column_width=True)

    # -------------------------
    # Citations
    # -------------------------
    st.subheader("Citations")
    for c in res["citations"]:
        st.markdown(
            f"- Page {c['page_num']} | "
            f"Score: {round(c['score'], 3)} | "
            f"[PDF]({c['pdf_link']})"
        )
