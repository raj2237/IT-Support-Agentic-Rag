# IT Support Agentic RAG

An IT support assistant that answers from a private company knowledge base first, checks whether the retrieved evidence is sufficient, and uses web search as a fallback. It includes a small web chat UI, source/trace details, and an API for chat and document ingestion.

## How it works

1. LangGraph routes each question to knowledge-base retrieval or a direct response.
2. For support questions, the agent searches the configured Pinecone index and grades the evidence.
3. If the evidence is weak, it searches the web with Tavily and can rewrite and retry the query.
4. The agent returns an answer with its source, citations, and workflow trace.

## Requirements

- Python 3.13+
- API keys for [Groq](https://console.groq.com/), [Tavily](https://app.tavily.com/), and [Pinecone](https://app.pinecone.io/)

## Run locally

From the repository root, create and activate a virtual environment, then install dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your-groq-api-key
TAVILY_API_KEY=your-tavily-api-key
PINECONE_API_KEY=your-pinecone-api-key
ADMIN_API_KEY=replace-with-a-long-random-value
```

The default chat model is `openai/gpt-oss-20b`; the default embedding model is `sentence-transformers/all-MiniLM-L6-v2`. The app creates the configured Pinecone index and namespace when needed. The embedding model is downloaded locally on first use.

Start the app:

```powershell
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> for the chat UI or <http://127.0.0.1:8000/docs> for interactive API documentation.

To index the included sample knowledge-base documents:

```powershell
python ingest_sample_kb.py
```

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `POST /api/chat` | Answer a question; accepts `{"question": "..."}` |
| `POST /api/ingest` | Upload and index a PDF, TXT, Markdown, or DOCX file; requires the `X-Admin-Key` header |

The upload endpoint is also available from the UI’s **Add Company Document** button. Set a strong `ADMIN_API_KEY` before exposing the app, and keep `.env` out of version control.
