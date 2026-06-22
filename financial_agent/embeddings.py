import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from financial_agent.config import (
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    KNOWLEDGE_BASE_PATH,
)

logger = logging.getLogger(__name__)


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def _ensure_index_exists(pc: Pinecone) -> None:
    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        logger.info("Criando índice Pinecone '%s'...", PINECONE_INDEX_NAME)
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info("Índice criado.")


def load_and_split() -> list:
    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    documents = loader.load()
    splitter = MarkdownTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    logger.info("Base carregada: %d chunks gerados", len(chunks))
    return chunks


def build_index(chunks: list) -> PineconeVectorStore:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    _ensure_index_exists(pc)
    embeddings = _get_embeddings()
    index = PineconeVectorStore.from_documents(chunks, embeddings, index_name=PINECONE_INDEX_NAME)
    logger.info("Chunks indexados no Pinecone ('%s')", PINECONE_INDEX_NAME)
    return index


def load_index() -> PineconeVectorStore:
    embeddings = _get_embeddings()
    index = PineconeVectorStore.from_existing_index(PINECONE_INDEX_NAME, embeddings)
    logger.info("Índice Pinecone '%s' carregado", PINECONE_INDEX_NAME)
    return index
