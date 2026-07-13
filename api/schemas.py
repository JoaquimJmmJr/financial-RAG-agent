from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    chat_history: list[tuple[str, str]] = []


class SourceDocument(BaseModel):
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
