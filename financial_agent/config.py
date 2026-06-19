import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVAL_TOP_K = 4

DATA_DIR = "data"
FAISS_INDEX_PATH = "data/faiss_index"
KNOWLEDGE_BASE_PATH = "data/knowledge_base.md"
