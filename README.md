# DocuMind AI

A production-ready AI Knowledge Assistant built with FastAPI and RAG (Retrieval-Augmented Generation).

## Features

- Upload PDF documents
- Automatic chunking and embedding generation
- FAISS vector store for semantic search
- Chat endpoint powered by RAG + OpenAI LLM

## Project Structure

```
DocuMind-AI/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   └── config.py        # Settings (env-based)
│   ├── routes/
│   │   ├── documents.py     # Upload / list / delete endpoints
│   │   └── chat.py          # Chat / Q&A endpoint
│   ├── services/
│   │   ├── document_service.py  # PDF parsing, chunking, embedding, FAISS
│   │   └── chat_service.py      # RAG retrieval + LLM response
│   ├── models/
│   │   ├── document.py      # Pydantic models for documents
│   │   └── chat.py          # Pydantic models for chat
│   └── utils/               # Shared utilities
├── uploads/                 # Uploaded PDF files (gitignored)
├── tests/                   # Test suite
├── .env.example             # Environment variable template
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Clone and enter the project

```bash
cd DocuMind-AI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

### 6. Open API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | /api/v1/documents/upload        | Upload a PDF             |
| GET    | /api/v1/documents/              | List all documents       |
| DELETE | /api/v1/documents/{document_id} | Delete a document        |
| POST   | /api/v1/chat/                   | Ask a question (RAG)     |
| GET    | /health                         | Health check             |
