import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from financial_agent.config import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    FAISS_INDEX_PATH,
    KNOWLEDGE_BASE_PATH,
)

logger = logging.getLogger(__name__)


def load_and_split() -> list:
    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    documents = loader.load()
    splitter = MarkdownTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    logger.info("Base carregada: %d chunks gerados", len(chunks))
    return chunks


def build_index(chunks: list) -> FAISS:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    index = FAISS.from_documents(chunks, embeddings)
    index.save_local(FAISS_INDEX_PATH)
    logger.info("Índice FAISS salvo em %s", FAISS_INDEX_PATH)
    return index


def load_index() -> FAISS:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    index = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    logger.info("Índice FAISS carregado de %s", FAISS_INDEX_PATH)
    return index
