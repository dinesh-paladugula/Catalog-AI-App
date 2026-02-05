import base64
from pathlib import Path
import streamlit as st

from rag_app.core.rag.chain import answer_question

st.set_page_config(page_title="Catalog AI – Brochure Q&A", layout="wide")
st.title("Catalog AI – Brochure Q&A")


def embed_pdf(pdf_path: str, page: int | None = None, height: int = 700):
    """Embed PDF inside Streamlit to avoid file:// blocked issues."""
    data = Path(pdf_path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    page_part = f"#page={page}" if page else ""
    html = f"""
    <iframe
      src="data:application/pdf;base64,{b64}{page_part}"
      width="100%"
      height="{height}px"
      style="border: 1px solid #ddd; border-radius: 10px;"
    ></iframe>
    """
    st.components.v1.html(html, height=height, scrolling=True)


# Session state for page lock
if "page_lock" not in st.session_state:
    st.session_state.page_lock = None

# -------------------------
# Sidebar controls
# -------------------------
with st.sidebar:
    st.header("Controls")

    tenant_id = st.text_input("Tenant ID", value="tenant_01")
    doc_id = st.text_input("Document ID", value="sample_01")

    k = st.slider("Top K", min_value=1, max_value=15, value=5, step=1)

    use_page_lock = st.checkbox("Use page lock", value=st.session_state.page_lock is not None)
    page_lock = st.number_input(
        "Page number",
        min_value=1,
        step=1,
        value=int(st.session_state.page_lock) if st.session_state.page_lock else 1,
        disabled=not use_page_lock,
    )

    show_all_images = st.checkbox("Show all images", value=False)
    debug_mode = st.checkbox("Debug mode (show chunks)", value=False)

# -------------------------
# Main input
# -------------------------
question = st.text_input(
    "Ask a question about the brochure",
    placeholder="e.g. Show 2BHK east facing flats / Master bedroom dimensions",
)

col_a, col_b = st.columns([1, 5])
with col_a:
    submit = st.button("Search", use_container_width=True)
with col_b:
    if st.session_state.page_lock is not None:
        st.info(f"Page lock is ON → Page {st.session_state.page_lock}. Turn off in sidebar to auto-search.")

# -------------------------
# Run query
# -------------------------
if submit and question:
    page_num = int(page_lock) if use_page_lock else None

    with st.spinner("Searching brochure…"):
        res = answer_question(
            question,
            tenant_id=tenant_id,
            doc_id=doc_id,
            page_num=page_num,
            k=int(k),
            index_name="vector_index",
        )

    # Figure out the PDF path from retrieved
    pdf_path = None
    if res.get("retrieved"):
        pdf_path = res["retrieved"][0].get("source_pdf")

    # -------------------------
    # Tabs
    # -------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["Answer", "Images", "PDF", "Debug"])

    # -------- Answer tab
    with tab1:
        st.subheader("Answer")
        st.write(res.get("answer", ""))

        st.subheader("Citations (click to open that page)")
        for c in res.get("citations", []):
            page = c.get("page_num")
            score = c.get("score")
            chunk = c.get("chunk_index")

            left, right = st.columns([4, 1])
            with left:
                st.write(f"Page {page} | score {round(float(score), 3)} | chunk {chunk}")
            with right:
                if st.button(f"Open {page}", key=f"open_{page}_{chunk}"):
                    st.session_state.page_lock = int(page)
                    st.rerun()

    # -------- Images tab
    with tab2:
        st.subheader("Floor plan images")
        imgs = res.get("image_paths") or []
        if not imgs:
            st.info("No images returned.")
        else:
            # Show fewer by default
            display_imgs = imgs if show_all_images else imgs[:3]

            cols = st.columns(3)
            for i, img_path in enumerate(display_imgs):
                with cols[i % 3]:
                    st.image(img_path, width=260)  # thumbnail
                    with st.expander("View larger"):
                        st.image(img_path, use_container_width=True)

            if (not show_all_images) and len(imgs) > 3:
                st.caption(f"Showing 3 of {len(imgs)} images. Enable “Show all images” in sidebar to see more.")

    # -------- PDF tab
    with tab3:
        st.subheader("PDF access (no blocked links)")

        if not pdf_path:
            st.info("PDF path not available from retrieved results.")
        else:
            pdf_bytes = Path(pdf_path).read_bytes()

            c1, c2 = st.columns([1, 2])
            with c1:
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=Path(pdf_path).name,
                    mime="application/pdf",
                    use_container_width=True,
                )

            with c2:
                open_viewer = st.checkbox("Open PDF viewer here", value=True)

            if open_viewer:
                # If we have a locked page, open that page in viewer
                viewer_page = st.session_state.page_lock if st.session_state.page_lock else None
                embed_pdf(pdf_path, page=viewer_page)

            st.caption(
                "Note: Browsers block opening local file:// links from a web app. "
                "Use Download or the in-app viewer instead."
            )

    # -------- Debug tab
    with tab4:
        if not debug_mode:
            st.info("Enable Debug mode in the sidebar to see retrieved chunks.")
        else:
            st.subheader("Top retrieved chunks")
            for r in res.get("retrieved", []):
                st.write(f"Score: {round(float(r.get('score', 0)), 3)} | Page: {r.get('page_num')} | Chunk: {r.get('chunk_index')}")
                st.code((r.get("text") or "")[:800])
