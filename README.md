# Financial RAG Agent

An intelligent financial advisor built with Retrieval-Augmented Generation (RAG). It answers investment questions based on a custom knowledge base, citing the sources used in each response.

**Goal**: Explore RAG patterns applied to the financial domain and build a production-ready portfolio example.

> Good financial knowledge bases are extensive and diffuse. A RAG system allows queries to retrieve only the passages relevant to the question's context, generating precise and traceable answers.

---

## Key Features

### 1. Complete RAG Pipeline

- Intelligent knowledge base ingestion and chunking with `MarkdownTextSplitter`
- Embedding generation via OpenAI (`text-embedding-3-small`)
- Cloud vector indexing with Pinecone
- Semantic retrieval of the most relevant passages per question
- Prompt assembly with retrieved context, sent to the LLM

### 2. Conversational Financial Advisor

- Chat interface with conversation history via `st.session_state`
- Answers grounded exclusively in the knowledge base content
- Automatic citation of the base passages used in each response
- Explicit indication when a question falls outside the base's scope

### 3. Knowledge Base Management

- Knowledge base in Markdown (`.md`) format, readable and version-controllable in Git
- Setup script for ingestion and reindexing: `python -m financial_agent.setup`
- Index persisted in Pinecone (cloud) — no need to reingest on every run
- Support for multiple documents in the `data/` folder

### 4. REST API with FastAPI

- `POST /chat` endpoint exposes the agent to any HTTP client (mobile, another backend, external frontend)
- `GET /health` endpoint for availability monitoring
- Interactive documentation auto-generated via Swagger UI at `/docs`
- Typed schemas with Pydantic (`ChatRequest`, `ChatResponse`) for automatic input/output validation
- Retriever shared between the API and Streamlit via singleton (`@lru_cache`) — no duplicated resources

### 5. Traceability and Transparency

- Each response displays the base chunks used as context
- Similarity score shown per retrieved chunk
- Enables auditing of why the model responded the way it did

---

## Known Limitations

- **Static knowledge base**: the agent has no internet access or real-time market data. Responses reflect only the content of the indexed knowledge base.
- **Base coverage**: questions outside the document's scope explicitly indicate a lack of context, but answer quality directly depends on the quality and breadth of the indexed content.
- **Residual hallucination**: even with RAG, the LLM may interpolate information not present in the retrieved chunks. Displaying the context chunks allows users to verify response fidelity.
- **Fixed chunking**: chunk size and overlap are statically configured. Documents with highly variable structure may require fine-tuning of the split parameters.
- **Embedding cost**: each reindexing triggers calls to the OpenAI embeddings API. For large knowledge bases, cost should be taken into consideration.

---

## System Architecture

```
Input:
  User question (Streamlit chat)

Pipeline:
  Question
    |
    ├── Embeddings (OpenAI text-embedding-3-small)
    |
    ├── Retrieval (Pinecone similarity search)
    |     └── Top-k most relevant chunks from the knowledge base
    |
    ├── Prompt Composition (LangChain)
    |     ├── System prompt with advisor instructions
    |     ├── Context: retrieved chunks
    |     └── Conversation history
    |
    ├── LLM (OpenAI GPT-4o-mini)
    |
    └── Formatted response + context chunks displayed

Output:
  Grounded response + cited sources (Streamlit)
```

**REST API (parallel to Streamlit)**

```
Input:
  POST /chat  { question, chat_history }

Pipeline:
  FastAPI endpoint
    |
    ├── Retrieval (Pinecone similarity search)
    |     └── Top-k most relevant chunks
    |
    ├── Prompt Composition (LangChain)
    |     ├── System prompt + retrieved context
    |     └── Conversation history
    |
    └── LLM (OpenAI GPT-4o-mini)

Output:
  { answer, sources: [{ content }] }
```

---

## Technologies Used

| Layer | Technology |
|---|---|
| Interface | Streamlit |
| RAG Framework | LangChain |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Pinecone (cloud) |
| Backend API | FastAPI + Uvicorn |
| Configuration | python-dotenv |

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/joaquimjonkel/financial-rag-agent.git
cd financial-rag-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Mac/Linux:
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on the example:

```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=financial-rag
```

`PINECONE_INDEX_NAME` can be any name. Setup automatically creates the index in Pinecone if it doesn't already exist.

### 5. Add your knowledge base

Place your `.md` file at `data/knowledge_base.md`. The document must be in Markdown — use headings (`#`, `##`) to structure sections, since the splitter uses these markers to divide chunks semantically.

### 6. Index the knowledge base

```bash
python -m financial_agent.setup
```

This command reads the documents in `data/`, generates embeddings, and indexes the vectors in Pinecone. The index is created automatically if it doesn't already exist.

### 7. Run the application

**Streamlit interface:**
```bash
streamlit run app.py
```

**REST API (optional, port 8000):**
```bash
uvicorn api.main:app --reload
```

Interactive API documentation is available at `http://localhost:8000/docs`.

### 8. Testing the API

**Via Swagger UI (no code):**
1. Go to `http://localhost:8000/docs`
2. Click `POST /chat` → "Try it out"
3. Paste the payload and click "Execute":
```json
{
  "question": "What is a REIT?",
  "chat_history": []
}
```

**Via terminal (curl):**

Windows PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:8000/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What is a REIT?", "chat_history": []}'
```

Mac/Linux:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a REIT?", "chat_history": []}'
```

**Check if the API is running:**
```bash
curl http://localhost:8000/health
# Expected response: {"status":"ok"}
```

---

## Project Structure

```
financial-rag-agent/
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPI app + endpoints (/health, /chat)
│   ├── schemas.py          # Pydantic models (ChatRequest, ChatResponse)
│   └── dependencies.py     # Shared retriever singleton
├── financial_agent/
│   ├── __init__.py
│   ├── config.py           # Constants and .env parsing
│   ├── embeddings.py       # Ingestion, indexing, and retrieval (Pinecone)
│   ├── llm.py              # OpenAI client
│   ├── rag.py              # RAG pipeline (orchestrates embeddings + llm)
│   └── setup.py            # Knowledge base ingestion script
├── data/
│   └── knowledge_base.md   # Financial knowledge base
├── tests/
│   └── test_rag.py
├── app.py                  # Streamlit interface
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Learning Objectives

- [x] RAG architecture and patterns
- [x] Text splitting and chunking strategies
- [x] Embedding generation and persistence
- [x] Vector DB integration (FAISS)
- [x] Migration from local to cloud Vector DB (Pinecone)
- [x] Prompt engineering with LangChain
- [x] Source attribution and response grounding
- [ ] Testing for AI pipelines
- [x] Exposing the agent as a REST API (FastAPI)
- [x] Production deployment (Render)

---

## Deployment

API in production on Render: `https://financial-rag-agent-gtes.onrender.com`

Interactive documentation: `https://financial-rag-agent-gtes.onrender.com/docs`

> Free tier: the service hibernates after 15 minutes without requests. The first call after inactivity may take ~30-50s to respond.

---

## Future Improvements

- **Confidence scoring**: display a confidence indicator based on the similarity scores of retrieved chunks, alerting the user when the retrieved context is weak
- **PDF ingestion**: allow direct upload of PDF documents in addition to Markdown, with text extraction via PyMuPDF
- **Persistent memory**: save conversation history across sessions for context continuity
- **Incremental base updates**: add documents to the index without reindexing everything, using Pinecone's upsert API
- **Automated RAG evaluation**: implement retrieval quality metrics (MRR, NDCG) and response fidelity metrics (RAGAS)

---

## Disclaimer

This project and its outputs are provided for educational purposes only. They do not constitute professional financial advice. Consult a qualified financial advisor before making investment decisions.
