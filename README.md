# 🧠 AI Enterprise Decision Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready, enterprise-grade AI system that demonstrates **multi-agent orchestration** using LangGraph. Five specialized AI agents collaborate to analyze complex business questions and provide traceable, auditable decisions with confidence scores.

![Agent Flow Demo](docs/demo-flow.gif)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent System** | 5 specialized AI agents working in orchestrated workflow |
| 📊 **Visual Execution Flow** | Real-time visualization of agent execution using React Flow |
| 🔍 **Complete Audit Trail** | Every step is logged and traceable |
| ⚠️ **Risk Assessment** | Automatic risk scoring with mitigation strategies |
| 💯 **Confidence Scores** | Quantified confidence in recommendations |
| 🔄 **Validation Loop** | Quality-checked research with automatic re-research if needed |
| 📚 **RAG Ready** | Document upload and vector search capabilities |
| ⚡ **Fast Inference** | Powered by Groq (LLaMA 3.3 70B) with Ollama fallback |

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │               FRONTEND                      │
                    │   React + TypeScript + TailwindCSS          │
                    │        + React Flow Visualization           │
                    └──────────────────┬──────────────────────────┘
                                       │ REST API
                    ┌──────────────────▼──────────────────────────┐
                    │               BACKEND                       │
                    │              FastAPI                        │
                    └──────────────────┬──────────────────────────┘
                                       │
        ┌──────────────────────────────▼────────────────────────────────┐
        │                        LANGGRAPH                              │
        │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────┐  ┌────────┐ │
        │  │ Planner │→│ Research│→│Validator│→│ Risk │→│Decision│ │
        │  └─────────┘  └─────────┘  └────┬────┘  └──────┘  └────────┘ │
        │                                 │ ↑                          │
        │                                 └─┘ (validation loop)        │
        └───────────────────────────────────────────────────────────────┘
                    │                               │
        ┌───────────▼───────────┐     ┌─────────────▼─────────────┐
        │      ChromaDB         │     │    SQLite + SQLAlchemy    │
        │   (Vector Storage)    │     │     (Persistence)         │
        └───────────────────────┘     └───────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API Key ([Get free key](https://console.groq.com/))
- OR Ollama installed locally

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-decision-intelligence.git
cd ai-decision-intelligence

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Configure environment
cd ..
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file:

```env
# LLM Provider (groq or ollama)
LLM_PROVIDER=groq
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# For local inference (optional)
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate     # Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📖 How It Works

### The 5 AI Agents

| # | Agent | Purpose | Output |
|---|-------|---------|--------|
| 1 | **Planner** | Analyzes query, creates execution plan | Structured plan, research areas |
| 2 | **Research** | Gathers information on each area | Findings with citations |
| 3 | **Validator** | Quality-checks research, finds gaps | Pass/Fail, identified gaps |
| 4 | **Risk** | Assesses risks and compliance | Risk score (0-100%), mitigations |
| 5 | **Decision** | Synthesizes final recommendation | Decision, confidence score |

### Example Queries

```
"Should we acquire a startup that specializes in AI?"

"Evaluate the legal risks of using AI in our hiring process"

"Analyze the decision to expand our e-commerce platform to Southeast Asia"

"What GDPR compliance requirements apply to customer data processing?"
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
ai-decision-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                 # REST endpoints
│   │   │   ├── graph_routes.py  # Workflow execution
│   │   │   ├── document_routes.py
│   │   │   └── analytics_routes.py
│   │   ├── agents/              # LangGraph agents
│   │   │   ├── planner_agent.py
│   │   │   ├── research_agent.py
│   │   │   ├── validator_agent.py
│   │   │   ├── risk_agent.py
│   │   │   └── decision_agent.py
│   │   ├── graph/               # Workflow definition
│   │   │   ├── state.py         # State schema
│   │   │   └── workflow.py      # Graph construction
│   │   ├── core/                # Configuration
│   │   │   ├── config.py
│   │   │   └── llm.py           # LLM factory
│   │   ├── rag/                 # RAG pipeline
│   │   └── db/                  # Database models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── GraphVisualization.tsx
│   │   │   └── DecisionResults.tsx
│   │   ├── services/api.ts
│   │   └── types/index.ts
│   └── package.json
├── docs/
│   ├── PROJECT_DOCUMENTATION.md  # Comprehensive technical docs
│   ├── ARCHITECTURE.md
│   └── INTERVIEW_PREP.md
├── docker/
└── .env.example
```

---

## 📚 Documentation


- [🏗️ Architecture Deep Dive](docs/ARCHITECTURE.md)
- [🚀 Deployment Guide](docs/DEPLOYMENT.md)

---

## 🛠️ Technology Stack

### Backend
- **LangGraph** - Multi-agent orchestration framework
- **LangChain** - LLM application framework
- **FastAPI** - Modern async web framework
- **Groq** - Ultra-fast cloud inference (LLaMA 3.3 70B)
- **Ollama** - Local LLM inference
- **ChromaDB** - Vector database for RAG
- **SQLAlchemy** - ORM for database operations

### Frontend
- **React 18** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first styling
- **React Flow** - Node-based visualizations
- **Axios** - HTTP client

---

## 🎯 Use Cases

- **M&A Analysis** - Evaluate acquisitions and mergers
- **Risk Assessment** - Compliance and regulatory analysis
- **Strategic Planning** - Market expansion decisions
- **Policy Review** - Internal policy compliance checks
- **Vendor Evaluation** - Third-party risk assessment

---

## 🤝 Contributing

This is a portfolio/learning project. Feel free to fork and customize!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Groq](https://groq.com) - Fast inference
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [React](https://react.dev) - Frontend library

---

**⭐ Star this repo if you found it helpful!**
