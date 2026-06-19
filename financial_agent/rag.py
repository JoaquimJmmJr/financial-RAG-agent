import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from financial_agent.llm import get_llm
from financial_agent.config import RETRIEVAL_TOP_K

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assessor financeiro especializado. Responda apenas com base
no contexto fornecido abaixo. Se a informação não estiver na base de conhecimento, informe
explicitamente que não possui dados sobre o tema. Não invente informações.

Aviso: suas respostas são educacionais e não constituem aconselhamento financeiro profissional.

Contexto da base de conhecimento:
"""


def build_retriever(index: FAISS):
    retriever = index.as_retriever(search_kwargs={"k": RETRIEVAL_TOP_K})
    logger.info("Retriever inicializado com top_k=%d", RETRIEVAL_TOP_K)
    return retriever


def ask(retriever, question: str, chat_history: list) -> dict:
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Fallback: escapa chaves para o LangChain não interpretar {x} do contexto como variável de template.
    safe_context = context.replace("{", "{{").replace("}", "}}")
    messages = [("system", SYSTEM_PROMPT + safe_context)]
    for human_msg, ai_msg in chat_history:
        messages.append(("human", human_msg))
        messages.append(("assistant", ai_msg))
    messages.append(("human", question))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain  = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({})

    logger.info("Resposta gerada com %d chunks de contexto", len(docs))
    return {"answer": answer, "sources": docs}
