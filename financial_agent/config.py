import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-rag")

LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVAL_TOP_K = 4

DATA_DIR = "data"
KNOWLEDGE_BASE_PATH = "data/knowledge_base.md"
