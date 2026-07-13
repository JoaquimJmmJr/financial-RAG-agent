import logging
from fastapi import FastAPI, HTTPException
from api.schemas import ChatRequest, ChatResponse, SourceDocument
from api.dependencies import get_retriever
from financial_agent.rag import ask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial RAG Agent API",
    description="API REST para o assessor financeiro com RAG. Respostas fundamentadas na base de conhecimento.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        retriever = get_retriever()
        result = ask(retriever, request.question, request.chat_history)
        return ChatResponse(
            answer=result["answer"],
            sources=[SourceDocument(content=doc.page_content) for doc in result["sources"]],
        )
    except Exception as e:
        logger.error("Erro ao processar pergunta: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
