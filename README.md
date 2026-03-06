# AI PDF Chatbot using Retrieval-Augmented Generation (RAG)

## Overview

This project implements a **production-style Retrieval-Augmented Generation (RAG) based AI chatbot** that answers user queries using one or more PDF documents as knowledge sources.

The system extracts text from uploaded PDFs, converts them into semantic embeddings, stores them in a vector database, retrieves relevant information using similarity search, and generates responses using a Large Language Model (LLM).

The chatbot supports **multi-document ingestion, conversational memory, metadata filtering, source citations, and PDF page preview**.

---

# Features

## Level 1 – Basic RAG System
- PDF parsing and text extraction
- Text chunking for semantic retrieval
- Embedding generation using transformer models
- Vector database storage using FAISS
- Top-K similarity search
- Streamlit interface for interaction

## Level 2 – Production-Ready RAG
- Modular pipeline architecture
- Multiple PDF upload support
- Dynamic LLM configuration
- Streamlit chat interface
- Environment-based API key integration

## Level 3 – Conversational Memory
- Maintains conversation history
- Supports follow-up questions
- Multi-turn question answering using previous context

## Level 4 – Metadata Filtering
- Document-level filtering
- Page-level filtering
- Source citations with page numbers
- Metadata-aware retrieval

---

# Additional Enhancements
- Chat-style UI using Streamlit
- PDF source preview within the app
- Download chat history as PDF
- Multi-document knowledge base
- Clear conversation functionality

---

# System Architecture

User Query  
↓  
Streamlit Chat Interface  
↓  
Retriever (FAISS Vector Database)  
↓  
Top-K Relevant Chunks  
↓  
Prompt Construction (with conversation history)  
↓  
Groq Llama-3.1 LLM  
↓  
Generated Answer + Source Citations  

---

# Technologies Used

- **Python**
- **LangChain**
- **FAISS Vector Database**
- **Sentence Transformers**
- **Groq Llama-3.1 LLM**
- **Streamlit**
- **PyPDF Loader**

---

# Project Structure
