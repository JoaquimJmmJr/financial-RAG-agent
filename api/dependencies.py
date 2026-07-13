from functools import lru_cache
from financial_agent.embeddings import load_index
from financial_agent.rag import build_retriever


@lru_cache(maxsize=1)
def get_retriever():
    index = load_index()
    return build_retriever(index)
