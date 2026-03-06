import streamlit as st
import tempfile
import base64
from fpdf import FPDF
from rag_pipeline import RAGPipeline

st.set_page_config(page_title="AI PDF Assistant", page_icon="🤖")

st.title("📄 AI PDF Knowledge Assistant")
st.caption("Ask questions from your documents")

rag = RAGPipeline()

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

    st.divider()

    if "chat_history" in st.session_state and st.session_state.chat_history:

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

# ---------------- CHAT STATE ---------------- #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- PROCESS PDFs ---------------- #

if uploaded_files:

    pdf_paths = []

    with st.spinner("Processing documents..."):

        for file in uploaded_files:

            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(file.read())
            pdf_paths.append({
                "path": temp.name,
                "filename": file.name
                })

        rag.load_pdfs(pdf_paths)

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

for chat in st.session_state.chat_history:

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
                        f"{s['filename']} (Page {s['page']}) - {s['section']}"
                    )

                    if st.button(
                        f"Preview {s['filename']} Page {s['page']}",
                        key=f"{s['filename']}_{s['page']}_{i}"
                    ):

                        with open(s["path"], "rb") as f:
                            base64_pdf = base64.b64encode(
                                f.read()
                            ).decode("utf-8")

                        pdf_display = f"""
                        <iframe src="data:application/pdf;base64,{base64_pdf}#page={s['page']}"
                        width="700" height="900"></iframe>
                        """

                        st.markdown(pdf_display, unsafe_allow_html=True)