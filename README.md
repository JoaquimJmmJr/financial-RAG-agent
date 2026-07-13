# Financial RAG Agent

Assessor financeiro inteligente com Retrieval-Augmented Generation (RAG). Responde dúvidas de investimento com base em uma base de conhecimento personalizada, citando as fontes utilizadas em cada resposta.

**Objetivo**: Explorar padrões de RAG aplicados ao domínio financeiro e construir um exemplo production-ready para portfólio.

> Boas bases de conhecimento financeiro são extensas e difusas. Um sistema RAG permite consultar apenas os trechos relevantes ao contexto da pergunta, gerando respostas precisas e rastreáveis.

---

## Principais funcionalidades

### 1. Pipeline RAG completo

- Ingestão e chunking inteligente da base de conhecimento com `MarkdownTextSplitter`
- Geração de embeddings via OpenAI (`text-embedding-3-small`)
- Indexação vetorial em cloud com Pinecone
- Retrieval semântico dos trechos mais relevantes por pergunta
- Montagem do prompt com contexto recuperado e envio ao LLM

### 2. Assessor financeiro conversacional

- Interface de chat com histórico de conversa via `st.session_state`
- Respostas fundamentadas exclusivamente no conteúdo da base de conhecimento
- Citação automática dos trechos da base utilizados em cada resposta
- Indicação explícita quando a pergunta está fora do escopo da base

### 3. Gerenciamento da base de conhecimento

- Base de conhecimento em formato Markdown (`.md`), legível e versionável no Git
- Script de setup para ingestão e reindexação: `python -m financial_agent.setup`
- Índice persistido no Pinecone (cloud) — não é necessário reingerir a cada execução
- Suporte a múltiplos documentos na pasta `data/`

### 4. API REST com FastAPI

- Endpoint `POST /chat` expõe o agente para qualquer cliente HTTP (mobile, outro backend, frontend externo)
- Endpoint `GET /health` para monitoramento de disponibilidade
- Documentação interativa gerada automaticamente via Swagger UI em `/docs`
- Schemas tipados com Pydantic (`ChatRequest`, `ChatResponse`) para validação automática de entrada e saída
- Retriever compartilhado entre API e Streamlit via singleton (`@lru_cache`) — sem duplicação de recursos

### 5. Rastreabilidade e transparência

- Cada resposta exibe os chunks da base utilizados como contexto
- Score de similaridade exibido por chunk recuperado
- Permite auditar por que o modelo respondeu o que respondeu

---

## Limitações conhecidas

- **Base estática**: o agente não acessa internet nem dados de mercado em tempo real. As respostas refletem apenas o conteúdo da base de conhecimento indexada.
- **Cobertura da base**: perguntas fora do escopo do documento retornam indicação explícita de ausência de contexto, mas a qualidade da resposta depende diretamente da qualidade e abrangência do conteúdo indexado.
- **Alucinação residual**: mesmo com RAG, o LLM pode interpolar informações não presentes nos chunks recuperados. A exibição dos chunks de contexto permite ao usuário verificar a fidelidade da resposta.
- **Chunking fixo**: o tamanho e overlap dos chunks são configurados estaticamente. Documentos com estrutura muito variada podem requerer ajuste fino dos parâmetros de split.
- **Custo de embeddings**: cada reindexação gera chamadas à API de embeddings da OpenAI. Para bases grandes, o custo deve ser considerado.

---

## Arquitetura do sistema

```
Input:
  Pergunta do usuário (Streamlit chat)

Pipeline:
  Pergunta
    |
    ├── Embeddings (OpenAI text-embedding-3-small)
    |
    ├── Retrieval (Pinecone similarity search)
    |     └── Top-k chunks mais relevantes da base de conhecimento
    |
    ├── Prompt Composition (LangChain)
    |     ├── System prompt com instruções do assessor
    |     ├── Contexto: chunks recuperados
    |     └── Histórico da conversa
    |
    ├── LLM (OpenAI GPT-4o-mini)
    |
    └── Resposta formatada + chunks de contexto exibidos

Output:
  Resposta fundamentada + fontes citadas (Streamlit)
```

**API REST (paralela ao Streamlit)**

```
Input:
  POST /chat  { question, chat_history }

Pipeline:
  FastAPI endpoint
    |
    ├── Retrieval (Pinecone similarity search)
    |     └── Top-k chunks mais relevantes
    |
    ├── Prompt Composition (LangChain)
    |     ├── System prompt + contexto recuperado
    |     └── Histórico da conversa
    |
    └── LLM (OpenAI GPT-4o-mini)

Output:
  { answer, sources: [{ content }] }
```

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Interface | Streamlit |
| Framework RAG | LangChain |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Pinecone (cloud) |
| Backend API | FastAPI + Uvicorn |
| Configuração | python-dotenv |

---

## Como executar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/joaquimjonkel/financial-rag-agent.git
cd financial-rag-agent
```

### 2. Crie e ative o ambiente virtual

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

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` com base no exemplo:

```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=financial-rag
```

`PINECONE_INDEX_NAME` pode ser qualquer nome. O setup cria o índice automaticamente no Pinecone caso ele ainda não exista.

### 5. Adicione sua base de conhecimento

Coloque seu arquivo `.md` em `data/knowledge_base.md`. O documento deve estar em Markdown — use headings (`#`, `##`) para estruturar seções, pois o splitter usa esses marcadores para dividir chunks semanticamente.

### 6. Indexe a base de conhecimento

```bash
python -m financial_agent.setup
```

Este comando lê os documentos em `data/`, gera os embeddings e indexa os vetores no Pinecone. O índice é criado automaticamente se ainda não existir.

### 7. Execute a aplicação

**Interface Streamlit:**
```bash
streamlit run app.py
```

**API REST (opcional, porta 8000):**
```bash
uvicorn api.main:app --reload
```

A documentação interativa da API estará disponível em `http://localhost:8000/docs`.

### 8. Testando a API

**Via Swagger UI (sem código):**
1. Acesse `http://localhost:8000/docs`
2. Clique em `POST /chat` → "Try it out"
3. Cole o payload e clique em "Execute":
```json
{
  "question": "O que é um FII?",
  "chat_history": []
}
```

**Via terminal (curl):**

Windows PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:8000/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "O que é um FII?", "chat_history": []}'
```

Mac/Linux:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é um FII?", "chat_history": []}'
```

**Verificar se a API está no ar:**
```bash
curl http://localhost:8000/health
# Resposta esperada: {"status":"ok"}
```

---

## Estrutura do projeto

```
financial-rag-agent/
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPI app + endpoints (/health, /chat)
│   ├── schemas.py          # Modelos Pydantic (ChatRequest, ChatResponse)
│   └── dependencies.py     # Retriever singleton compartilhado
├── financial_agent/
│   ├── __init__.py
│   ├── config.py           # Constantes e leitura do .env
│   ├── embeddings.py       # Ingestão, indexação e retrieval (Pinecone)
│   ├── llm.py              # Cliente OpenAI
│   ├── rag.py              # Pipeline RAG (orquestra embeddings + llm)
│   └── setup.py            # Script de ingestão da base de conhecimento
├── data/
│   └── knowledge_base.md   # Base de conhecimento financeira
├── tests/
│   └── test_rag.py
├── app.py                  # Interface Streamlit
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Objetivos de aprendizado

- [x] Arquitetura e padrões de RAG
- [x] Text splitting e estratégias de chunking
- [x] Geração e persistência de embeddings
- [x] Integração com Vector DB (FAISS)
- [x] Migração de Vector DB local para cloud (Pinecone)
- [x] Prompt engineering com LangChain
- [x] Atribuição de fonte e grounding de respostas
- [ ] Testes para pipelines de IA
- [x] Exposição do agente como API REST (FastAPI)
- [x] Deploy em produção (Render)

---

## Deploy

API em produção no Render: `https://financial-rag-agent-gtes.onrender.com`

Documentação interativa: `https://financial-rag-agent-gtes.onrender.com/docs`

> Plano gratuito: o serviço hiberna após 15 minutos sem requisições. A primeira chamada após inatividade pode levar ~30-50s para responder.

---

## Melhorias futuras

- **Scoring de confiança**: exibir um indicador de confiança baseado nos scores de similaridade dos chunks recuperados, alertando o usuário quando o contexto recuperado é fraco
- **Ingestão de PDF**: permitir upload direto de documentos PDF além de Markdown, com extração de texto via PyMuPDF
- **Memoria persistente**: salvar o histórico de conversas entre sessões para continuidade do contexto
- **Atualização incremental da base**: adicionar documentos ao índice sem reindexar tudo, usando a API de upsert do Pinecone
- **Avaliação automatizada do RAG**: implementar métricas de qualidade do retrieval (MRR, NDCG) e fidelidade das respostas (RAGAS)

---

## Aviso legal

Este projeto e seus outputs sao fornecidos exclusivamente para fins educacionais. Não constituem aconselhamento financeiro profissional. Consulte um assessor financeiro qualificado antes de tomar decisoes de investimento.
