# Deployment Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama (for local LLM)
- Docker & Docker Compose (optional)

## Local Development Setup

### 1. Clone and Setup Environment

```powershell
# Clone repository
git clone <your-repo-url>
cd ai-decision-intelligence

# Copy environment template
Copy-Item .env.example .env

# Edit .env with your settings
notepad .env
```

### 2. Install Ollama and Model

```powershell
# Download and install Ollama from https://ollama.ai

# Pull the Mistral model
ollama pull mistral

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 3. Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.db import init_db; init_db()"

# Run backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 4. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Docker Deployment

### Using Docker Compose

```powershell
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Ollama: `http://localhost:11434`

### Individual Containers

```powershell
# Build backend
docker build -f docker/Dockerfile.backend -t ai-backend .

# Run backend
docker run -p 8000:8000 -v ${PWD}/data:/app/data ai-backend

# Build frontend
docker build -f docker/Dockerfile.frontend -t ai-frontend .

# Run frontend
docker run -p 3000:80 ai-frontend
```

## Production Deployment

### Cloud Platforms

#### AWS Deployment

**Backend (ECS Fargate)**:
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -f docker/Dockerfile.backend -t ai-backend .
docker tag ai-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ai-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ai-backend:latest

# Deploy to ECS (use AWS Console or CLI)
```

**Frontend (S3 + CloudFront)**:
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Database (RDS PostgreSQL)**:
```bash
# Update .env
DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/dbname
```

#### Google Cloud Platform

**Backend (Cloud Run)**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-backend
gcloud run deploy ai-backend --image gcr.io/PROJECT_ID/ai-backend --platform managed
```

**Frontend (Cloud Storage + CDN)**:
```bash
cd frontend
npm run build
gsutil -m rsync -r dist/ gs://your-bucket-name
```

### Environment Variables for Production

```env
# LLM - Use cloud provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Database - Use managed PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Vector DB - Use managed service
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...

# Security
SECRET_KEY=<generate-secure-random-key>
CORS_ORIGINS=https://yourdomain.com

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=https://...
```

### Database Migration

#### SQLite to PostgreSQL

1. **Export data from SQLite**:
```python
# export_data.py
from app.db import SessionLocal, Conversation, Decision, Document
import json

db = SessionLocal()
data = {
    'conversations': [c.__dict__ for c in db.query(Conversation).all()],
    'decisions': [d.__dict__ for d in db.query(Decision).all()],
    'documents': [doc.__dict__ for doc in db.query(Document).all()],
}

with open('export.json', 'w') as f:
    json.dump(data, f)
```

2. **Update DATABASE_URL** in `.env`

3. **Initialize PostgreSQL**:
```python
from app.db import init_db
init_db()
```

4. **Import data**:
```python
# import_data.py
import json
from app.db import SessionLocal, Conversation, Decision, Document

with open('export.json') as f:
    data = json.load(f)

db = SessionLocal()
# Import logic here
```

### Scaling Considerations

#### Horizontal Scaling

**API Servers**:
- Deploy multiple FastAPI instances
- Use load balancer (AWS ALB, GCP Load Balancer)
- Ensure stateless design (no in-memory state)

**Database**:
- Use read replicas for queries
- Write to primary, read from replicas
- Connection pooling (SQLAlchemy handles this)

**Vector Database**:
- Migrate to Pinecone/Weaviate for scale
- Implement sharding if needed

#### Caching

**Redis for API Responses**:
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379)

def cache_response(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Monitoring Setup

#### Application Monitoring

**Sentry for Error Tracking**:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

#### Infrastructure Monitoring

- **CloudWatch** (AWS) or **Stackdriver** (GCP) for logs
- **DataDog** or **New Relic** for APM
- **Grafana** for custom dashboards

### Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] API keys rotated regularly
- [ ] Secrets in environment variables (not code)
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (ORM)
- [ ] CORS properly configured
- [ ] Authentication enabled
- [ ] Regular security audits
- [ ] Dependency updates automated

### Backup Strategy

**Database Backups**:
```bash
# PostgreSQL automated backups
pg_dump dbname > backup_$(date +%Y%m%d).sql

# Restore
psql dbname < backup_20240101.sql
```

**Vector Database Backups**:
- ChromaDB: Backup `data/vector_db` directory
- Pinecone: Use Pinecone backup API

**Document Storage**:
- Backup `data/uploads` directory
- Use S3 versioning for cloud storage

### Health Checks

**Kubernetes Liveness Probe**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Docker Health Check**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Performance Optimization

1. **Database Indexing**:
```python
# Add indexes to frequently queried columns
Index('idx_session_id', Conversation.session_id)
Index('idx_execution_id', Decision.execution_id)
```

2. **API Response Compression**:
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

3. **Frontend Optimization**:
```bash
# Build with optimizations
npm run build

# Analyze bundle size
npm run build -- --analyze
```

### Troubleshooting

**Ollama Connection Issues**:
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
# Windows: Restart from Task Manager
# Linux: systemctl restart ollama
```

**Database Connection Issues**:
```python
# Test database connection
from app.db import engine
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(result.fetchone())
```

**Vector Store Issues**:
```python
# Reset vector store
from app.rag import get_vector_store
vs = get_vector_store()
vs.reset()
```

### Cost Optimization

**LLM Costs**:
- Use caching for repeated queries
- Implement request deduplication
- Use cheaper models for simple tasks

**Infrastructure Costs**:
- Auto-scaling based on load
- Spot instances for non-critical workloads
- Reserved instances for predictable load

**Storage Costs**:
- Lifecycle policies for old data
- Compression for documents
- Tiered storage (hot/cold)

---

## Quick Reference

### Common Commands

```powershell
# Start development
.\setup.ps1

# Run backend
cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev

# Run with Docker
docker-compose up

# View logs
docker-compose logs -f backend

# Reset database
python -c "from app.db import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Reset vector store
python -c "from app.rag import get_vector_store; get_vector_store().reset()"
```

### Useful Endpoints

- Health: `GET /health`
- API Docs: `GET /docs`
- Execute: `POST /api/execute`
- Upload: `POST /api/documents/upload`
- Analytics: `GET /api/analytics/metrics`

---

This deployment guide covers local development, Docker deployment, and production deployment to cloud platforms with comprehensive monitoring, security, and optimization strategies.
