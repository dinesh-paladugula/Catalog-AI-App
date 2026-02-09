import streamlit as st
from pathlib import Path

from rag_app.core.rag.chain import answer_question

st.set_page_config(
    page_title="Catalog AI - My Home Tridasa",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stImage {
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 My Home Tridasa - AI Assistant")
st.caption("Direct, factual information about the Tridasa project. Includes floor plans and site layouts.")

# ----------------------------
# Sidebar for configuration
# ----------------------------
with st.sidebar:
    st.header("Settings")
    doc_id = st.text_input("Document ID", value="My-Home-Tridasa-E-Brochure")
    tenant_id = st.text_input("Tenant ID", value="tenant_01")
    k_value = st.slider("Context chunks (k)", 1, 25, 15)
    
    st.divider()
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

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

        # Display images and their individual source links
        if msg.get("show_images"):
            images = msg.get("images", [])
            page_nums = msg.get("page_nums", [])
            pdf_links = msg.get("pdf_links", [])
            
            if images:
                cols = st.columns(min(len(images), 2))
                for idx, img in enumerate(images[:2]):
                    with cols[idx]:
                        caption = f"Page {page_nums[idx]}" if idx < len(page_nums) else "Source Image"
                        st.image(img, width="stretch", caption=caption)
                        # Show individual link for this specific page using standard markdown
                        if idx < len(pdf_links) and pdf_links[idx]:
                            st.markdown(f"🔗 [Source {page_nums[idx]}]({pdf_links[idx]})")

# ----------------------------
# Chat input
# ----------------------------
question = st.chat_input("Ask about towers, dimensions, or site plans...")

if question:
    # 1. Add user message to state and UI
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 2. Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing brochure..."):
            try:
                # Prepare chat history for the chain
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                
                # Call the RAG chain
                res = answer_question(
                    question,
                    tenant_id=tenant_id,
                    doc_id=doc_id,
                    k=k_value,
                    index_name="vector_index",
                    chat_history=history
                )
                
                # Display the answer
                st.markdown(res["answer"])

                # 3. Handle Images and individual links
                images = []
                page_nums = []
                pdf_links = []
                seen_pages = set()
                
                # Sort citations by score
                sorted_citations = sorted(
                    res.get("citations", []), 
                    key=lambda x: x.get("score", 0), 
                    reverse=True
                )

                for c in sorted_citations:
                    img = c.get("image_path")
                    page = c.get("page_num")
                    link = c.get("pdf_link")
                    if img and page not in seen_pages:
                        images.append(img)
                        page_nums.append(page)
                        pdf_links.append(link)
                        seen_pages.add(page)
                
                show_images = len(images) > 0

                if show_images:
                    cols = st.columns(min(len(images), 2))
                    for idx, img in enumerate(images[:2]):
                        with cols[idx]:
                            st.image(img, width="stretch", caption=f"Page {page_nums[idx]}")
                            # Show individual link for this specific page using standard markdown
                            if idx < len(pdf_links) and pdf_links[idx]:
                                st.markdown(f"🔗 [Source{page_nums[idx]}]({pdf_links[idx]})")

                # 4. Save assistant message to session state
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": res["answer"],
                        "images": images,
                        "page_nums": page_nums,
                        "pdf_links": pdf_links,
                        "show_images": show_images,
                    }
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Technical Details: Ensure MongoDB is connected and the .env file is correctly configured.")
