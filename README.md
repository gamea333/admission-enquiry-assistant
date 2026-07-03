# Admission Enquiry Assistant

A RAG-powered assistant for university admission enquiries. Combines document retrieval (Chroma + Gemini embeddings) with structured SQL data (programs, deadlines, FAQs) to answer student questions.

## Project Structure

```
admission-enquiry-assistant/
├── app/                  # FastAPI backend
│   ├── main.py           # Application entrypoint
│   ├── config.py         # Environment settings
│   ├── router.py         # /chat and /health endpoints
│   ├── schemas.py        # Pydantic models
│   ├── rag/              # Document ingestion & generation
│   └── db/               # SQLAlchemy models & queries
├── data/
│   ├── documents/        # Source PDFs, DOCX, TXT files
│   └── vectorstore/      # Persisted Chroma index
├── frontend/             # Streamlit chat UI
└── tests/
```

## Setup

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install pytest httpx  # for running tests
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_API_KEY
   ```

4. **Add documents** — place PDF, DOCX, or TXT files in `data/documents/`.

5. **Build the vector store**

   ```bash
   python -m app.rag.ingest
   ```

6. **Seed sample data** (also runs automatically on API startup)

   ```bash
   python -m app.db.seed
   ```

## Running

**API server:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Streamlit frontend:**

```bash
streamlit run frontend/streamlit_app.py
```

## API

| Method | Endpoint      | Description              |
|--------|---------------|--------------------------|
| GET    | `/api/health` | Health check             |
| POST   | `/api/chat`   | Send an admission query  |

**Example request:**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the MBA admission deadlines?"}'
```

## Tests

```bash
pip install pytest
pytest tests/
```
