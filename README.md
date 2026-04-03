# DocuMind AI

DocuMind AI is a web application that lets you **upload PDF documents and ask questions about them using AI**. Instead of reading through a long document yourself, you can just ask "What is this document about?" or "What are the key points?" and get an instant AI-generated answer.

---

## How It Works (Simple Explanation)

Here's what happens step by step when you upload a PDF and ask a question:

1. **You upload a PDF** → The app reads all the text from it
2. **The text gets split into small chunks** → Like cutting a book into paragraphs
3. **Each chunk gets converted into numbers (embeddings)** → This is how AI "understands" text — it turns words into a list of numbers that capture their meaning
4. **These numbers are stored in a database (FAISS)** → FAISS is a special database built for searching through numbers very fast
5. **You ask a question** → Your question also gets converted into numbers
6. **The app finds the most relevant chunks** → By comparing your question's numbers to the stored chunks (this is called "semantic search")
7. **Those chunks are sent to an AI (Groq/LLaMA)** → Along with your question
8. **The AI reads the context and writes an answer** → Grounded in your document, not made up

This approach is called **RAG (Retrieval-Augmented Generation)** — it retrieves relevant information first, then generates an answer from it.

---

## Tech Stack

| What | Tool | Why |
|------|------|-----|
| Web framework | FastAPI | Builds the API that the UI talks to |
| PDF reading | PyPDF | Extracts text from PDF files |
| Text splitting | LangChain | Breaks text into smaller chunks |
| Embeddings | Sentence Transformers | Converts text to numbers (vectors) |
| Vector database | FAISS | Stores and searches through embeddings |
| AI model | Groq (LLaMA 3.3 70B) | Generates the final answer |
| Frontend | HTML + CSS + JS | The web UI you interact with |

---

## Project Structure

```
DocuMind-AI/
│
├── app/                        # All backend code lives here
│   ├── main.py                 # Starts the web server, connects all pieces
│   │
│   ├── core/
│   │   └── config.py           # Reads settings from the .env file
│   │
│   ├── routes/                 # Defines what URLs the app responds to
│   │   ├── documents.py        # /upload, /list, /delete endpoints
│   │   └── chat.py             # /chat endpoint (ask a question)
│   │
│   ├── services/               # The core logic / brain of the app
│   │   ├── document_service.py # Reads PDF → chunks → embeds → stores in FAISS
│   │   └── chat_service.py     # Searches FAISS → calls Groq AI → returns answer
│   │
│   └── models/                 # Defines the shape of data (inputs & outputs)
│       ├── document.py         # What a document upload response looks like
│       └── chat.py             # What a chat request/response looks like
│
├── static/                     # Frontend (what you see in the browser)
│   ├── index.html              # The web page structure
│   ├── style.css               # The styling (colors, layout, fonts)
│   └── app.js                  # Handles clicks, uploads, and API calls
│
├── uploads/                    # Where uploaded PDFs are saved
├── faiss_index/                # Where the vector database is saved
├── .env                        # Your secret API keys (never share this!)
├── .env.example                # A template showing what goes in .env
└── requirements.txt            # List of Python packages needed
```

---

## Setup & Run

### Step 1 — Enter the project folder

```bash
cd DocuMind-AI
```

### Step 2 — Create a virtual environment

A virtual environment keeps this project's packages separate from the rest of your system.

```bash
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` at the start of your terminal line — that means it's active.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
pip install "httpx==0.27.0"
pip install "numpy<2.0"
```

### Step 4 — Set up your API key

```bash
cp .env.example .env
```

Open the `.env` file and replace `your-groq-api-key-here` with your actual key from [console.groq.com](https://console.groq.com).

```
GROQ_API_KEY=gsk_your_actual_key_here
```

### Step 5 — Start the server

```bash
uvicorn app.main:app --reload
```

### Step 6 — Open the app

Go to **http://127.0.0.1:8000** in your browser.

> Every time you open a new terminal, remember to activate the virtual environment first:
> `source venv/bin/activate`

---

## How to Use the App

1. **Upload a PDF** — Click "Browse File" or drag and drop a PDF into the left panel
2. **Wait for processing** — The app will read and index the document (a few seconds)
3. **Ask a question** — Type your question in the chat box and press Enter
4. **Get an answer** — The AI will answer based on the content of your document

You can also click on a document in the list to scope your question to that specific document only.

---

## API Endpoints

If you want to interact with the backend directly (without the UI), you can use these endpoints. Visit **http://127.0.0.1:8000/docs** for an interactive interface.

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/api/v1/documents/upload` | Upload a PDF |
| GET | `/api/v1/documents/` | List all uploaded documents |
| DELETE | `/api/v1/documents/{document_id}` | Delete a document |
| POST | `/api/v1/chat/` | Ask a question |
| GET | `/health` | Check if the server is running |

---

## Common Issues

**`command not found: uvicorn`**
→ You forgot to activate the virtual environment. Run `source venv/bin/activate` first.

**`Address already in use`**
→ A previous server is still running. Kill it with `kill $(lsof -ti:8000)` then try again.

**`Could not reach the server`**
→ Check that the server is running in your terminal. Also make sure your `.env` file has the correct Groq API key.

**Slow first startup**
→ The embedding model (`all-MiniLM-L6-v2`) downloads on first use (~90MB). After that it's cached and starts fast.
