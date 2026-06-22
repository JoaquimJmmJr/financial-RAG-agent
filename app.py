import logging
import streamlit as st
from financial_agent.embeddings import load_index
from financial_agent.rag import build_retriever, ask

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Financial RAG Agent", layout="centered")
st.title("Financial RAG Agent")
st.caption("Assessor financeiro com IA — respostas fundamentadas na base de conhecimento")


st.cache_resource(show_spinner="Conectando à base de conhecimento...")
def init_retriever():
    try:
        index = load_index()
        return build_retriever(index)
    except Exception as e:
        st.error(f"Erro ao conectar ao Pinecone: {e}\nVerifique PINECONE_API_KEY e PINECONE_INDEX_NAME no .env")
        st.stop()


retriever = init_retriever()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
         st.markdown(message["content"])

if prompt := st.chat_input("Faça sua pergunta sobre investimentos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
         st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conhecimento..."):
            result = ask(retriever, prompt, st.session_state.chat_history)

        st.markdown(result["answer"])

        if result["sources"]:
            with st.expander("Fontes utilizadas"):
                for i, doc in enumerate(result["sources"], 1):
                    st.markdown(f"**Trecho {i}**")
                    st.caption(doc.page_content)

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    st.session_state.chat_history.append((prompt, result["answer"]))
