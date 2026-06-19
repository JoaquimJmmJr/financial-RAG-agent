from langchain_openai import ChatOpenAI
from financial_agent.config import LLM_MODEL

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=LLM_MODEL, temperature=0.2)
