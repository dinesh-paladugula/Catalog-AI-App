import streamlit as st
from pathlib import Path

from rag_app.core.rag.chain import answer_question
from rag_app.core.utils.intent import needs_images

st.set_page_config(
    page_title="Catalog AI",
    layout="centered",
)

st.title("🏢 Catalog AI")
st.caption("Ask questions about the brochure. Answers are grounded with images and page links.")

# ----------------------------
# Session state: chat history
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Render chat history
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("show_images"):
            for img in msg.get("images", []):
                st.image(img, width=420)

        if msg.get("pdf_link"):
            st.markdown(f"📄 [Open brochure page]({msg['pdf_link']})")

# ----------------------------
# Chat input
# ----------------------------
question = st.chat_input("Ask about flats, plans, dimensions…")

if question:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant
    with st.chat_message("assistant"):
        with st.spinner("Searching brochure…"):
            res = answer_question(
                question,
                tenant_id="tenant_01",
                doc_id="sample_01",
                k=5,
                index_name="vector_index",
            )

        st.markdown(res["answer"])

        show_images = needs_images(question)
        images = []

        if show_images:
            images = res.get("image_paths", [])[:3]
            for img in images:
                st.image(img, width=420)

        pdf_link = res.get("primary_pdf_link")
        if pdf_link:
            st.markdown(f"📄 [Open brochure page]({pdf_link})")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": res["answer"],
            "images": images,
            "pdf_link": pdf_link,
            "show_images": show_images,
        }
    )
