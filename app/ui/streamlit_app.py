from pathlib import Path

import streamlit as st

from app.config import (
    UPLOAD_DIR,
    EMBEDDING_MODEL_NAME,
    RETRIEVAL_TOP_K,
    TARGET_CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CHUNK_SIZE,
    OLLAMA_BASE_URL,
    LLM_MODEL_NAME,
)
from app.ingestion.file_router import FileRouter
from app.processing.chunker import TextChunker
from app.retrieval.embedder import Embedder
from app.retrieval.retriever import InMemoryRetriever
from app.qa.answer_service import AnswerService


st.set_page_config(
    page_title="Document Insight Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

router = FileRouter()

chunker = TextChunker(
    target_chunk_size=TARGET_CHUNK_SIZE,
    max_chunk_size=MAX_CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    min_chunk_size=MIN_CHUNK_SIZE,
)

embedder = Embedder(model_name_or_path=EMBEDDING_MODEL_NAME)

answer_service = AnswerService(
    base_url=OLLAMA_BASE_URL,
    model_name=LLM_MODEL_NAME,
)


# -------------------------
# Custom CSS
# -------------------------
st.markdown(
    """
    <style>
        .main {
            padding-top: 1.2rem;
        }

        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #0f766e 100%);
            color: white;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        }

        .hero h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .hero p {
            margin-top: 0.6rem;
            margin-bottom: 0;
            color: rgba(255,255,255,0.88);
            font-size: 1rem;
            line-height: 1.5;
        }

        .info-card {
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: rgba(15, 23, 42, 0.55);
            border-radius: 16px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
            min-height: 96px;
        }

        .info-label {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
        }

        .info-value {
            font-size: 1rem;
            font-weight: 600;
            color: #e2e8f0;
            line-height: 1.4;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.7rem;
            color: #e5e7eb;
        }

        .answer-card {
            border-radius: 18px;
            padding: 1.15rem 1.2rem;
            background: linear-gradient(180deg, rgba(13, 148, 136, 0.14) 0%, rgba(15, 23, 42, 0.72) 100%);
            border: 1px solid rgba(45, 212, 191, 0.25);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
            margin-top: 0.4rem;
            margin-bottom: 1rem;
        }

        .answer-title {
            font-size: 0.85rem;
            color: #99f6e4;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .answer-text {
            color: #f8fafc;
            font-size: 1rem;
            line-height: 1.65;
        }

        .subtle-note {
            color: #94a3b8;
            font-size: 0.92rem;
            margin-top: 0.2rem;
            margin-bottom: 0.8rem;
        }

        .small-badge {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.24);
            color: #cbd5e1;
            font-size: 0.78rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        div[data-testid="stFileUploader"] {
            border-radius: 16px;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 12px;
        }

        div[data-testid="stDownloadButton"] button,
        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------
# Header / Hero
# -------------------------
st.markdown(
    """
    <div class="hero">
        <h1>Document Insight Assistant</h1>
        <p>
            Upload a document, extract its content, retrieve the most relevant evidence,
            and generate a grounded answer using a local LLM.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Supported Formats</div>
            <div class="info-value">PDF · JPG · PNG</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">Embedding Model</div>
            <div class="info-value">{EMBEDDING_MODEL_NAME}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">Local LLM</div>
            <div class="info-value">{LLM_MODEL_NAME}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Pipeline</div>
            <div class="info-value">Extract → Chunk → Retrieve → Answer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.header("System Info")
    st.write("*Uploaded files are stored in `data/uploads`.*")
    st.write(f"**Embedding Model:** {EMBEDDING_MODEL_NAME}")
    st.write(f"**LLM Model:** {LLM_MODEL_NAME}")
    st.write(f"**Ollama URL:** {OLLAMA_BASE_URL}")


# -------------------------
# Session state init
# -------------------------
if "save_path" not in st.session_state:
    st.session_state.save_path = None

if "extracted_pages" not in st.session_state:
    st.session_state.extracted_pages = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "retrieval_results" not in st.session_state:
    st.session_state.retrieval_results = None

if "answer_result" not in st.session_state:
    st.session_state.answer_result = None

if "last_processed_filename" not in st.session_state:
    st.session_state.last_processed_filename = None

if "last_query" not in st.session_state:
    st.session_state.last_query = None

if "active_section" not in st.session_state:
    st.session_state.active_section = "Ask & Answer"


def _save_uploaded_file(uploaded_file) -> Path:
    save_path = UPLOAD_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path


def _build_download_button(extracted_pages: list[dict]) -> None:
    full_text = "\n\n".join(
        f"--- Page {p['page_number']} ---\n{p['text']}" for p in extracted_pages
    )
    st.download_button(
        label="Download extracted text",
        data=full_text,
        file_name="extracted_text.txt",
        mime="text/plain",
    )


def _build_chunk_download_button(chunks: list[dict]) -> None:
    full_text = "\n\n".join(
        f"--- {c['chunk_id']} ---\n{c['text']}" for c in chunks
    )
    st.download_button(
        label="Download chunked text",
        data=full_text,
        file_name="chunked_text.txt",
        mime="text/plain",
    )


def _is_list_like_query(query: str) -> bool:
    q = query.lower()
    keywords = [
        "reference", "references", "citation", "citations",
        "bibliography", "source", "sources", "list",
        "atıf", "atıflar", "kaynakça", "referans", "referanslar",
        "listele", "kaynaklar"
    ]
    return any(k in q for k in keywords)


def _is_reference_query(query: str) -> bool:
    q = query.lower()
    keywords = [
        "reference", "references", "bibliography", "citation", "citations",
        "kaynakça", "referans", "referanslar", "atıf", "atıflar"
    ]
    return any(k in q for k in keywords)


def _collect_reference_chunks(all_chunks: list[dict]) -> list[dict]:
    matched = []

    for chunk in all_chunks:
        text = chunk.get("text", "").lower()
        if "references" in text or "bibliography" in text or "kaynakça" in text:
            item = dict(chunk)
            item["score"] = None
            matched.append(item)

    if matched:
        target_pages = {item["page_number"] for item in matched}
        target_file = matched[0]["source_file"]

        expanded = []
        for chunk in all_chunks:
            if chunk["source_file"] == target_file and chunk["page_number"] in target_pages:
                item = dict(chunk)
                item["score"] = None
                expanded.append(item)

        expanded.sort(key=lambda x: (x["page_number"], x["chunk_index"]))
        return expanded

    return []


def _expand_results_for_list_query(results: list[dict], all_chunks: list[dict]) -> list[dict]:
    if not results:
        return results

    target_pages = {item["page_number"] for item in results}
    target_file = results[0]["source_file"]

    score_map = {item["chunk_id"]: item.get("score") for item in results}

    expanded = []
    for chunk in all_chunks:
        if chunk["source_file"] == target_file and chunk["page_number"] in target_pages:
            item = dict(chunk)
            item["score"] = score_map.get(item["chunk_id"])
            expanded.append(item)

    expanded.sort(key=lambda x: (x["page_number"], x["chunk_index"]))
    return expanded


def _render_extraction_result(extracted_pages: list[dict], src_path: Path) -> None:
    st.markdown('<div class="section-title">Extracted Pages</div>', unsafe_allow_html=True)
    st.success(f"Extraction completed successfully. Total pages found: {len(extracted_pages)}")
    _build_download_button(extracted_pages)

    for page in extracted_pages:
        title = f"📄 Page {page['page_number']}  ·  {page['extraction_method']}"
        with st.expander(title):
            st.markdown(
                f"""
                <span class="small-badge">Source: {src_path.name}</span>
                <span class="small-badge">Page: {page['page_number']}</span>
                <span class="small-badge">Method: {page['extraction_method']}</span>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                label="Extracted Text",
                value=page["text"],
                height=260,
                key=f"page_{page['source_file']}_{page['page_number']}",
            )


def _render_chunk_result(chunks: list[dict]) -> None:
    st.markdown('<div class="section-title">Chunked Document Segments</div>', unsafe_allow_html=True)

    if not chunks:
        st.warning("No chunks were generated.")
        return

    st.success(f"Total chunks generated: {len(chunks)}")
    _build_chunk_download_button(chunks)

    for chunk in chunks:
        title = f"🧩 {chunk['chunk_id']}  ·  Page {chunk['page_number']}  ·  {chunk['char_length']} chars"
        with st.expander(title):
            st.markdown(
                f"""
                <span class="small-badge">Source: {chunk['source_file']}</span>
                <span class="small-badge">Page: {chunk['page_number']}</span>
                <span class="small-badge">Chunk Index: {chunk['chunk_index']}</span>
                <span class="small-badge">Method: {chunk['extraction_method']}</span>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                label="Chunk Text",
                value=chunk["text"],
                height=220,
                key=chunk["chunk_id"],
            )


def _build_retriever(chunks: list[dict]) -> InMemoryRetriever:
    retriever = InMemoryRetriever(embedder)
    retriever.build(chunks)
    return retriever


def _render_retrieval_and_answer(chunks: list[dict]) -> None:
    st.markdown('<div class="section-title">Ask Your Document</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle-note">Ask a question in Turkish or English. The system will retrieve the most relevant evidence and generate a grounded answer.</div>',
        unsafe_allow_html=True,
    )

    if not chunks:
        st.warning("No chunks available for retrieval.")
        return

    if st.session_state.retriever is None:
        with st.spinner("Generating chunk embeddings..."):
            st.session_state.retriever = _build_retriever(chunks)

    with st.form("qa_form", clear_on_submit=False):
        user_query = st.text_input(
            "Ask a question about the uploaded document",
            key="retrieval_query_input",
            placeholder="For example: What is the date of this document?",
        )
        ask_clicked = st.form_submit_button("Ask Document")

    if ask_clicked and user_query.strip():
        # eski sonucu temizle
        st.session_state.retrieval_results = None
        st.session_state.answer_result = None
        st.session_state.last_query = user_query

        with st.spinner("Searching for the most relevant evidence..."):
            if _is_reference_query(user_query):
                results = _collect_reference_chunks(chunks)

                if not results:
                    top_k = 10
                    results = st.session_state.retriever.retrieve(user_query, top_k=top_k)
                    results = _expand_results_for_list_query(results, chunks)
            else:
                top_k = 10 if _is_list_like_query(user_query) else RETRIEVAL_TOP_K

                results = st.session_state.retriever.retrieve(
                    user_query,
                    top_k=top_k,
                )

                if _is_list_like_query(user_query):
                    results = _expand_results_for_list_query(results, chunks)

            st.session_state.retrieval_results = results

        with st.spinner("Generating final answer with local LLM..."):
            st.session_state.answer_result = answer_service.answer(
                user_query,
                st.session_state.retrieval_results,
            )

    results = st.session_state.retrieval_results
    answer_result = st.session_state.answer_result

    if not st.session_state.last_query:
        st.info("Your final answer and supporting evidence will appear here after you ask a question.")
        return

    st.markdown(f"**Last question:** {st.session_state.last_query}")

    if not results:
        st.warning("No relevant chunks were found.")
        return

    if answer_result:
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="answer-title">Final Answer</div>
                <div class="answer-text">{answer_result["answer"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Retrieved Evidence</div>', unsafe_allow_html=True)

    for item in results:
        score = item.get("score")
        score_text = f"{score:.4f}" if isinstance(score, (int, float)) else "expanded"
        score_badge = f"{score:.4f}" if isinstance(score, (int, float)) else "expanded"

        title = f"🔎 {item['chunk_id']}  ·  Page {item['page_number']}  ·  Score {score_text}"
        with st.expander(title):
            st.markdown(
                f"""
                <span class="small-badge">Source: {item['source_file']}</span>
                <span class="small-badge">Page: {item['page_number']}</span>
                <span class="small-badge">Method: {item['extraction_method']}</span>
                <span class="small-badge">Score: {score_badge}</span>
                """,
                unsafe_allow_html=True,
            )
            st.text_area(
                label="Retrieved Text",
                value=item["text"],
                height=220,
                key=f"retrieved_{item['chunk_id']}",
            )

    if answer_result:
        with st.expander("Prompt / Messages Debug"):
            st.json(answer_result["messages"])


st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload a PDF, JPG, or PNG file",
    type=["pdf", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    st.success(f"Selected file: {uploaded_file.name}")

    if st.session_state.last_processed_filename != uploaded_file.name:
        st.session_state.save_path = None
        st.session_state.extracted_pages = None
        st.session_state.chunks = None
        st.session_state.retriever = None
        st.session_state.retrieval_results = None
        st.session_state.answer_result = None
        st.session_state.last_query = None

    if st.button("Process Document"):
        with st.spinner("Processing document..."):
            try:
                save_path = _save_uploaded_file(uploaded_file)
                extracted_pages = router.route_and_extract(save_path)
                chunks = chunker.chunk_document_pages(extracted_pages)

                st.session_state.save_path = save_path
                st.session_state.extracted_pages = extracted_pages
                st.session_state.chunks = chunks
                st.session_state.retriever = None
                st.session_state.retrieval_results = None
                st.session_state.answer_result = None
                st.session_state.last_processed_filename = uploaded_file.name
                st.session_state.last_query = None

                st.success("Document processed successfully.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

if st.session_state.extracted_pages and st.session_state.chunks and st.session_state.save_path:
    section = st.radio(
        "Navigation",
        ["Extraction", "Chunks", "Ask & Answer"],
        horizontal=True,
        key="active_section",
    )

    if section == "Extraction":
        _render_extraction_result(
            st.session_state.extracted_pages,
            st.session_state.save_path,
        )

    elif section == "Chunks":
        _render_chunk_result(st.session_state.chunks)

    elif section == "Ask & Answer":
        _render_retrieval_and_answer(st.session_state.chunks)
