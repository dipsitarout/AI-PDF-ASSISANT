import streamlit as st
import tempfile
import base64
from fpdf import FPDF
from rag_pipeline import RAGPipeline

st.set_page_config(page_title="AI PDF Assistant", page_icon="🤖")

# ---------------- SESSION STATE ---------------- #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "preview_pdf" not in st.session_state:
    st.session_state.preview_pdf = None

if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False

if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

rag = st.session_state.rag

# ---------------- TITLE ---------------- #

st.title("📄 AI PDF Knowledge Assistant")
st.caption("Ask questions from your documents")

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.header("📂 Document Manager")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    doc_names = ["All Documents"]

    for file in uploaded_files or []:
        doc_names.append(file.name)

    selected_doc = st.selectbox(
        "Filter by document",
        doc_names
    )

    selected_page = st.number_input(
        "Filter by page (optional)",
        min_value=0,
        step=1,
        value=0
    )

    if selected_page == 0:
        selected_page = None

    st.divider()

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.preview_pdf = None

    st.divider()

    if st.session_state.chat_history:

        if st.button("⬇ Download Chat"):

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for chat in st.session_state.chat_history:

                if chat["role"] == "user":
                    text = f"User: {chat['content']}"
                else:
                    text = f"Assistant: {chat['content']}"

                pdf.multi_cell(0, 8, text)

            pdf.output("chat_history.pdf")

            with open("chat_history.pdf", "rb") as f:
                st.download_button(
                    "Download PDF",
                    f,
                    file_name="chat_history.pdf"
                )

# ---------------- RESET WHEN NEW PDF UPLOADED ---------------- #

if uploaded_files:
    st.session_state.documents_loaded = False

# ---------------- PROCESS PDFs ---------------- #

if uploaded_files and not st.session_state.documents_loaded:

    pdf_paths = []

    with st.spinner("Processing documents..."):

        for file in uploaded_files:

            file_bytes = file.read()

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(file_bytes)
            temp.close()

            pdf_paths.append({
                "path": temp.name,
                "filename": file.name
            })

        rag.load_pdfs(pdf_paths)

        st.session_state.documents_loaded = True

    st.success("Documents processed successfully!")

# ---------------- CHAT INPUT ---------------- #

user_input = st.chat_input("Ask a question")

if user_input:

    with st.spinner("Thinking..."):

        answer, sources = rag.ask(
            user_input,
            selected_doc,
            selected_page
        )

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

# ---------------- DISPLAY CHAT ---------------- #

for chat_index, chat in enumerate(st.session_state.chat_history):

    if chat["role"] == "user":

        with st.chat_message("user"):
            st.write(chat["content"])

    else:

        with st.chat_message("assistant"):

            st.write(chat["content"])

            if "sources" in chat:

                st.caption("📄 Sources")

                for i, s in enumerate(chat["sources"]):

                    st.write(
                        f"📄 **{s['filename']}** • Page {s['page']} • {s['section']}"
                    )

                    if st.button(
                        f"Preview Page {s['page']}",
                        key=f"{chat_index}_{i}"
                    ):

                        with open(s["path"], "rb") as f:
                            pdf_bytes = f.read()

                        st.session_state.preview_pdf = {
                            "bytes": pdf_bytes,
                            "page": s["page"]
                        }
                        st.rerun()

# ---------------- PDF PREVIEW ---------------- #

# ---------------- PDF PREVIEW ---------------- #

if st.session_state.preview_pdf:

    pdf_bytes = st.session_state.preview_pdf["bytes"]
    page = st.session_state.preview_pdf["page"]

    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    st.markdown("## 📄 PDF Preview")

    pdf_display = f"""
    <iframe
    src="data:application/pdf;base64,{base64_pdf}#page={page}"
    width="100%"
    height="900"
    type="application/pdf">
    </iframe>
    """

    st.markdown(pdf_display, unsafe_allow_html=True)