# AI Enterprise Decision Intelligence Platform - Architecture

## System Overview

The AI Enterprise Decision Intelligence Platform is a production-ready system that demonstrates enterprise-grade AI engineering using LangGraph for multi-agent orchestration, RAG for knowledge retrieval, and a modern full-stack architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat UI      │  │ Doc Upload   │  │ Analytics    │          │
│  │ + Graph Viz  │  │ + Management │  │ Dashboard    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LangGraph Multi-Agent System                 │  │
│  │  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────┐  │  │
│  │  │ Planner │→ │ Research │→ │ Validator │→ │  Risk   │  │  │
│  │  │  Agent  │  │  Agent   │  │   Agent   │  │  Agent  │  │  │
│  │  └─────────┘  └──────────┘  └───────────┘  └─────────┘  │  │
│  │                                    ↓                       │  │
│  │                            ┌──────────────┐               │  │
│  │                            │   Decision   │               │  │
│  │                            │    Agent     │               │  │
│  │                            └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RAG Pipeline                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  Document  │→ │   Vector   │→ │ Retrieval  │         │  │
│  │  │ Processing │  │   Store    │  │  + Rerank  │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                    Data Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   SQLite     │  │   ChromaDB   │  │    Ollama    │          │
│  │  (Metadata)  │  │   (Vectors)  │  │    (LLM)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

### 1. Planner Agent
**Purpose**: Strategic analysis and execution planning

**Responsibilities**:
- Analyze user queries to understand decision-making needs
- Break down complex questions into research areas
- Create structured execution plans
- Identify required information sources

**Output**: Execution plan and list of research areas

### 2. Research Agent
**Purpose**: Information retrieval and synthesis

**Responsibilities**:
- Query vector database for relevant documents
- Retrieve and rank information by relevance
- Synthesize findings from multiple sources
- Provide citations for all claims

**Output**: Research findings with source citations

### 3. Validator Agent
**Purpose**: Quality assurance and critical evaluation

**Responsibilities**:
- Evaluate research findings for completeness
- Check logical consistency
- Identify gaps or contradictions
- Determine if additional research is needed

**Output**: Validation assessment and identified gaps

**Special Behavior**: Can trigger additional research iterations

### 4. Risk & Compliance Agent
**Purpose**: Risk assessment and regulatory analysis

**Responsibilities**:
- Identify financial, operational, and legal risks
- Assess regulatory compliance concerns
- Calculate risk scores (0.0 to 1.0)
- Classify risk levels (low/medium/high/critical)
- Provide mitigation strategies

**Output**: Risk assessment with scores and mitigation plans

**Special Behavior**: Flags high/critical risks for human approval

### 5. Decision Agent
**Purpose**: Final synthesis and recommendation

**Responsibilities**:
- Synthesize all agent inputs
- Generate clear, actionable recommendations
- Provide confidence scores
- Present alternative options
- Ensure evidence-based decisions

**Output**: Final decision with confidence scores and alternatives

## Graph Flow

### Standard Execution Path

```
START → Planner → Research → Validator → Risk → Decision → END
```

### Conditional Edges

#### Validation Loop
```
Validator → [needs_more_research?]
    ├─ YES → Increment Iteration → Research (max 2 iterations)
    └─ NO  → Risk
```

#### Human-in-the-Loop
```
Risk → [requires_approval?]
    ├─ YES → Human Approval → Decision
    └─ NO  → Decision
```

### Error Recovery

All agents include try-catch error handling. If an agent fails:
1. Error is logged to state
2. Execution continues with partial results
3. Error message is surfaced to user

## State Management

### State Schema

The `AgentState` TypedDict maintains:

- **Messages**: Conversation history with LangChain messages
- **User Input**: Query and session tracking
- **Planning**: Execution plan and research areas
- **Research**: Retrieved documents, findings, citations
- **Validation**: Results, gaps, iteration control
- **Risk**: Scores, levels, compliance issues, mitigation
- **Decision**: Final output, confidence, recommendations
- **Metadata**: Current agent, iteration count, approval flags
- **Audit**: Agent reasoning and execution path

### State Persistence

- **Memory Saver**: LangGraph checkpointer for state persistence
- **Database**: SQLAlchemy models for long-term storage
- **Thread ID**: Session-based state isolation

## RAG Pipeline

### Document Processing

1. **Upload**: Files uploaded via REST API
2. **Extraction**: Format-specific parsers (PDF, DOCX, TXT, CSV, JSON)
3. **Chunking**: Recursive character splitting with overlap
   - Chunk size: 1000 characters
   - Overlap: 200 characters
4. **Embedding**: sentence-transformers/all-MiniLM-L6-v2
5. **Storage**: ChromaDB with metadata

### Retrieval Process

1. **Query Embedding**: Convert user query to vector
2. **Similarity Search**: Find top-k most similar chunks
3. **Re-ranking**: Sort by relevance score
4. **Filtering**: Apply minimum score threshold (0.3)
5. **Citation Extraction**: Track source documents

## LLM Provider Architecture

### Provider-Agnostic Design

The system uses a factory pattern for LLM instantiation:

```python
def get_llm() -> BaseChatModel:
    if provider == "ollama":
        return ChatOllama(...)
    elif provider == "openai":
        return ChatOpenAI(...)
    # etc.
```

### Switching Providers

Change provider via environment variable:

```env
LLM_PROVIDER=ollama  # or openai, anthropic, google
```

No code changes required!

### Model Tiers

- **Fast LLM**: Quick tasks (planning, simple analysis)
- **Smart LLM**: Complex reasoning (validation, risk assessment)

## Database Schema

### Core Tables

- **conversations**: Session tracking
- **messages**: Chat history
- **documents**: Uploaded files
- **decisions**: Decision records
- **audit_logs**: Agent reasoning trail
- **executions**: Graph execution tracking

### Upgrade Path

SQLite → PostgreSQL requires only connection string change:

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
```

All models use SQLAlchemy ORM for database abstraction.

## Security Considerations

### Current Implementation

- CORS configuration for frontend
- File upload validation (type, size)
- SQL injection protection (ORM)
- Path traversal prevention

### Production Enhancements

- JWT authentication (structure in place)
- API rate limiting
- Input sanitization
- Secrets management (environment variables)
- HTTPS/TLS encryption

## Scalability Discussion

### Current Bottlenecks

1. **SQLite**: Single-writer limitation
2. **Local LLM**: CPU/GPU constraints
3. **In-memory state**: No distributed support

### Scaling Strategies

#### Horizontal Scaling

- **Database**: Migrate to PostgreSQL with read replicas
- **LLM**: Switch to cloud providers (OpenAI, Anthropic)
- **State**: Use Redis for distributed checkpointing
- **API**: Load balance with multiple FastAPI instances

#### Vertical Scaling

- **LLM**: GPU acceleration for local models
- **Vector DB**: Increase ChromaDB resources
- **Caching**: Add Redis for query results

#### Async Optimization

- **Background Tasks**: Celery for long-running workflows
- **Streaming**: SSE for real-time updates
- **Batch Processing**: Queue multiple executions

## Monitoring & Observability

### Logging

- Structured logging with JSON format
- Correlation IDs for request tracking
- Agent-level execution logs

### Metrics

- Execution time per agent
- Success/failure rates
- Confidence score distributions
- Risk level distributions

### Health Checks

- `/health` endpoint with system status
- Database connectivity
- Vector store availability
- LLM provider status

## Why LangGraph?

### Advantages Over Alternatives

**vs. LangChain Chains**:
- Explicit state management
- Conditional branching
- Human-in-the-loop support
- Visual workflow representation

**vs. Custom Orchestration**:
- Built-in checkpointing
- Streaming support
- Error recovery
- Production-tested framework

**vs. AutoGPT/BabyAGI**:
- Deterministic flow control
- Transparent reasoning
- Enterprise reliability
- Audit trail support

### Trade-offs

**Pros**:
- Structured workflows
- State persistence
- Production-ready
- Active development

**Cons**:
- Learning curve
- Framework dependency
- Less flexibility than custom code

## Production Deployment

### Recommended Stack

- **Compute**: AWS ECS / Google Cloud Run
- **Database**: AWS RDS PostgreSQL
- **Vector DB**: Pinecone / Weaviate
- **LLM**: OpenAI / Anthropic API
- **Monitoring**: DataDog / New Relic
- **Logging**: CloudWatch / Stackdriver

### Environment Separation

- **Development**: SQLite + Ollama
- **Staging**: PostgreSQL + Cloud LLM
- **Production**: Full cloud stack + monitoring

---

This architecture demonstrates production-grade AI engineering while remaining accessible for learning and portfolio development.
