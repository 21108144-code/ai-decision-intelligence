"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db import init_db
from app.models import HealthResponse
from app.api.graph_routes import router as graph_router
from app.api.document_routes import router as document_router
from app.api.conversation_routes import router as conversation_router
from app.api.analytics_routes import router as analytics_router
from app.api.simple_routes import router as simple_router
from app.rag import get_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting AI Decision Intelligence Platform...")
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Initialize vector store
    print("🔍 Initializing vector store...")
    get_vector_store()
    
    print("✅ Application started successfully!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready AI Enterprise Decision Intelligence Platform using LangGraph",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(graph_router)
app.include_router(document_router)
app.include_router(conversation_router)
app.include_router(analytics_router)
app.include_router(simple_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Decision Intelligence Platform API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    from app.rag import get_vector_store
    
    vector_store = get_vector_store()
    chunk_count = vector_store.get_document_count()
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        llm_provider=settings.llm_provider,
        database="sqlite" if "sqlite" in settings.database_url else "postgresql",
        vector_store_chunks=chunk_count
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
