from pathlib import Path 
from fastapi import APIRouter, Depends, HTTPException ,File, Header , UploadFile
from pydantic import BaseModel 
from app.core.config import get_settings 
from app.rag.workflow import route_question, ask 
from app.rag.vectorstore import add_documents
from app.services.ingestion import load_file, chunk_documents, SUPPORTED
from app.services.audit import write_audit 


router = APIRouter(prefix = "/api")

settings = get_settings()

class ChatRequest(BaseModel):
    question: str


@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/chat")
def chat(payload:ChatRequest):
    try:
        result= ask(payload.question)
        write_audit(payload.question,result['source_used'],result.get("trace",[]))

        return {
            "answer": result['answer'],
            "source_used": result['source_used'],
            "trace": result.get("trace", []),
            "citations": result.get("citations", []),
            "rewrittern_query": result.get("current_query", payload.question)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest(file: UploadFile = File(...), x_admin_key: str = Header(default="")):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Supported: {', '.join(sorted(SUPPORTED))}")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / Path(file.filename).name
    dest.write_bytes(await file.read())
    docs = load_file(dest) 
    chunks = chunk_documents(docs)
    ids = add_documents(chunks)
    return {"message": "Document indexed", "file": dest.name, "chunks": len(chunks), "ids_created": len(ids)}