# 🏢 Catalog AI - Assistant

An advanced Retrieval-Augmented Generation (RAG) application designed to provide direct, factual information about the **My Home Tridasa** real estate project. This tool extracts data from project brochures, including floor plans, site layouts, and room dimensions, providing cited answers alongside relevant visual aids.

## 🚀 Features

*   **Direct Factual Responses**: AI-driven answers that skip polite fillers and greetings to provide immediate data.
*   **Intelligent Dimension Extraction**: Specialized regex-based parsing to extract room dimensions (e.g., "12' 0\" x 13' 9\"") even from noisy OCR text.
*   **Visual Context**: Automatically displays relevant floor plans and site layout images based on the retrieved context.
*   **Interactive PDF Linking**: Every answer includes direct links to the specific pages of the official online brochure.
*   **Smart Chunking**: Uses `RecursiveCharacterTextSplitter` with page-aware metadata to ensure high-quality retrieval.
*   **Modern UI**: A clean Streamlit interface with a focused chat experience.

## 🛠️ Technical Stack

*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **LLM**: [Groq API](https://groq.com/) (Llama 3 / Mixtral)
*   **Vector Database**: [MongoDB Atlas Vector Search](https://www.mongodb.com/products/platform/atlas-vector-search)
*   **Embeddings**: [HuggingFace](https://huggingface.co/)
*   **OCR**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
*   **Framework**: [LangChain](https://www.langchain.com/)
*   **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 📋 Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed on your system.
- Tesseract OCR installed on your system.
- A MongoDB Atlas account with a Vector Search index named `vector_index`.
- API Keys for Groq and HuggingFace.

## ⚙️ Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd CatalogAIApp
    ```

2.  **Install dependencies using uv**:
    ```bash
    # Create virtual environment and install dependencies
    uv sync
    ```
    *Alternatively, if using uv pip:*
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_key
    HUGGINGFACE_API_KEY=your_hf_key
    MONGODB_URI=your_mongodb_connection_string
    GROQ_MODEL=llama3-8b-8192
    ```

4.  **Ingest Data**:
    Place the brochure PDF in `rag_app/data/raw/` and run the ingestion pipeline:
    ```bash
    uv run run_ingest.py
    ```

## 🖥️ Running the App

Start the Streamlit frontend using uv:
```bash
 uv run python -m streamlit run rag_app/apps/ui/app.py
```

## 📂 Project Structure

*   `rag_app/apps/ui/`: Streamlit frontend application.
*   `rag_app/core/rag/`: Core RAG logic, including the chain and dimension extraction.
*   `rag_app/core/ingest/`: Data ingestion pipeline and text chunking strategy.
*   `rag_app/core/utils/`: Utility functions for link generation and intent detection.
*   `rag_app/data/raw/`: Storage for source PDF brochures.

## 📝 Example Queries

*   "Can you show me the site layout plan?"
*   "What is the Master bedroom size in Flat no. 2?"
*   "How many towers are in the project?"
*   "What are the project specifications?"

---
*Developed as a specialized RAG solution for real estate data extraction.*
