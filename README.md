# Financial RAG Agent

Assessor financeiro inteligente com Retrieval-Augmented Generation (RAG). Responde dúvidas de investimento com base em uma base de conhecimento personalizada, citando as fontes utilizadas em cada resposta.

**Objetivo**: Explorar padrões de RAG aplicados ao domínio financeiro e construir um exemplo production-ready para portfólio.

> Boas bases de conhecimento financeiro são extensas e difusas. Um sistema RAG permite consultar apenas os trechos relevantes ao contexto da pergunta, gerando respostas precisas e rastreáveis.

---

## Principais funcionalidades

### 1. Pipeline RAG completo

- Ingestão e chunking inteligente da base de conhecimento com `MarkdownTextSplitter`
- Geração de embeddings via OpenAI (`text-embedding-3-small`)
- Indexação vetorial local com FAISS
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
- Índice FAISS persistido em disco — não é necessário reingerir a cada execução
- Suporte a múltiplos documentos na pasta `data/`

### 4. Rastreabilidade e transparência

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
    ├── Retrieval (FAISS similarity search)
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

**Roadmap de arquitetura (v2.0)**

```
Input:
  Requisição HTTP (cliente web ou mobile)

Pipeline:
  FastAPI endpoint
    |
    ├── LangChain RAG Agent
    |     ├── Retrieval (Pinecone cloud)
    |     └── LLM (OpenAI GPT-4o-mini)
    |
    └── JSON Response com metadata (chunks, scores, tokens usados)
```

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Interface | Streamlit |
| Framework RAG | LangChain |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | FAISS (local, MVP) |
| Configuração | python-dotenv |

### Roadmap de tecnologias (v2.0)

| Camada | Tecnologia |
|---|---|
| Vector DB | Pinecone (cloud, produção) |
| Backend API | FastAPI |

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
OPENAI_API_KEY=your_key_here
```

### 5. Adicione sua base de conhecimento

Coloque seu arquivo `.md` em `data/knowledge_base.md`. O documento deve estar em Markdown — use headings (`#`, `##`) para estruturar seções, pois o splitter usa esses marcadores para dividir chunks semanticamente.

### 6. Indexe a base de conhecimento

```bash
python -m financial_agent.setup
```

Este comando lê os documentos em `data/`, gera os embeddings e salva o índice FAISS em `data/faiss_index/`.

### 7. Execute a aplicação

```bash
streamlit run app.py
```

---

## Estrutura do projeto

```
financial-rag-agent/
├── financial_agent/
│   ├── __init__.py
│   ├── config.py           # Constantes e leitura do .env
│   ├── embeddings.py       # Ingestão, indexação e retrieval (FAISS)
│   ├── llm.py              # Cliente OpenAI
│   ├── rag.py              # Pipeline RAG (orquestra embeddings + llm)
│   ├── agent.py            # Lógica conversacional (histórico, chain)
│   └── setup.py            # Script de ingestão da base de conhecimento
├── data/
│   ├── knowledge_base.md   # Base de conhecimento financeira
│   └── faiss_index/        # Índice vetorial gerado (ignorado pelo Git)
├── tests/
│   └── test_rag.py
├── app.py                  # Entry point Streamlit
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Objetivos de aprendizado

- [ ] Arquitetura e padrões de RAG
- [ ] Text splitting e estratégias de chunking
- [ ] Geração e persistência de embeddings
- [ ] Integração com Vector DB (FAISS)
- [ ] Prompt engineering com LangChain
- [ ] Atribuição de fonte e grounding de respostas
- [ ] Testes para pipelines de IA
- [ ] Migração de Vector DB local para cloud (Pinecone)
- [ ] Exposição do agente como API REST (FastAPI)

---

## Melhorias futuras

- **Migrar para Pinecone**: substituir o índice FAISS local por Pinecone para persistência cloud, escalabilidade e atualizações incrementais da base sem reindexação completa
- **API REST com FastAPI**: expor o agente como endpoint HTTP, desacoplando o backend do Streamlit e permitindo integração com outros clientes
- **Scoring de confiança**: exibir um indicador de confiança baseado nos scores de similaridade dos chunks recuperados, alertando o usuário quando o contexto recuperado é fraco
- **Ingestão de PDF**: permitir upload direto de documentos PDF além de Markdown, com extração de texto via PyMuPDF
- **Memoria persistente**: salvar o histórico de conversas entre sessões para continuidade do contexto
- **Atualização incremental da base**: adicionar documentos ao índice sem reindexar tudo, usando FAISS `add_with_ids`
- **Avaliação automatizada do RAG**: implementar métricas de qualidade do retrieval (MRR, NDCG) e fidelidade das respostas (RAGAS)

---

## Aviso legal

Este projeto e seus outputs sao fornecidos exclusivamente para fins educacionais. Não constituem aconselhamento financeiro profissional. Consulte um assessor financeiro qualificado antes de tomar decisoes de investimento.
