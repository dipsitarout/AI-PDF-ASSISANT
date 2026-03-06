from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


# ---------- SECTION TITLE EXTRACTION ----------

def extract_section(text):

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if line.isupper() and len(line) < 60:
            return line

    return "General"


class RAGPipeline:

    def __init__(self):

        self.chat_history = []

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = None

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant"
        )

    # ---------- LOAD PDFs ----------

    def load_pdfs(self, pdf_paths):

        documents = []

        for pdf in pdf_paths:

            path = pdf["path"]
            filename = pdf["filename"]

            loader = PyPDFLoader(path)
            pages = loader.load()

            for page in pages:

                page.metadata["source"] = path
                page.metadata["filename"] = filename
                page.metadata["section"] = extract_section(
                    page.page_content
                )

            documents.extend(pages)

        if not documents:
            raise ValueError("No documents loaded.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(documents)

        if not chunks:
            raise ValueError("No chunks created.")

        print(f"Loaded {len(documents)} pages")
        print(f"Generated {len(chunks)} chunks")

        self.vectorstore = FAISS.from_documents(
            chunks,
            self.embeddings
        )

    # ---------- ASK QUESTION ----------

    def ask(self, question, selected_doc=None, selected_page=None):

        if not self.vectorstore:
            raise ValueError("Upload PDFs first.")

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        docs = retriever.invoke(question)

        if selected_doc and selected_doc != "All Documents":

            docs = [
                d for d in docs
                if selected_doc == d.metadata.get("filename")
            ]

        if selected_page:

            docs = [
                d for d in docs
                if d.metadata.get("page") == selected_page
            ]

        context = "\n".join([doc.page_content for doc in docs])

        history = "\n".join(self.chat_history)

        prompt = f"""
You are an AI assistant answering questions from documents.

Conversation so far:
{history}

Context from documents:
{context}

User question:
{question}

Answer clearly using the provided context.
"""

        response = self.llm.invoke(prompt)

        self.chat_history.append(f"User: {question}")
        self.chat_history.append(f"Assistant: {response.content}")

        sources = []
        seen = set()

        for d in docs:

            key = (
                d.metadata.get("filename"),
                d.metadata.get("page")
            )

            if key not in seen:

                seen.add(key)

                sources.append({
                    "path": d.metadata.get("source"),
                    "filename": d.metadata.get("filename"),
                    "page": d.metadata.get("page"),
                    "section": d.metadata.get("section")
                })

        return response.content, sources