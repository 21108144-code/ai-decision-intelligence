"""
Core configuration management using Pydantic Settings.
Supports multiple LLM providers and easy switching via environment variables.
"""
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="AI Decision Intelligence Platform")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # LLM Configuration - Provider Agnostic
    llm_provider: Literal["ollama", "openai", "anthropic", "google", "groq"] = Field(default="groq")
    
    # Ollama Settings
    ollama_model: str = Field(default="mistral")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_temperature: float = Field(default=0.7)
    
    # OpenAI Settings (for future use)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4")
    
    # Anthropic Settings (for future use)
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    
    # Google Settings (for future use)
    google_api_key: Optional[str] = Field(default=None)
    google_model: str = Field(default="gemini-pro")
    
    # Groq Settings
    groq_api_key: Optional[str] = Field(default=None)
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/app.db")
    
    # Vector Database
    vector_db_path: str = Field(default="./data/vector_db")
    vector_db_type: str = Field(default="chromadb")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    # File Upload
    max_upload_size_mb: int = Field(default=50)
    allowed_extensions: str = Field(default="pdf,docx,txt,csv,json")
    upload_dir: str = Field(default="./data/uploads")
    
    # RAG Settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    top_k_results: int = Field(default=5)
    
    # Agent Settings
    max_iterations: int = Field(default=10)
    enable_human_in_loop: bool = Field(default=True)
    timeout_seconds: int = Field(default=300)
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Parse allowed extensions from comma-separated string."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def get_data_dir(self) -> Path:
        """Get data directory path and ensure it exists."""
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    def get_upload_dir(self) -> Path:
        """Get upload directory path and ensure it exists."""
        upload_dir = Path(self.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    def get_vector_db_path(self) -> Path:
        """Get vector DB path and ensure it exists."""
        vector_path = Path(self.vector_db_path)
        vector_path.mkdir(parents=True, exist_ok=True)
        return vector_path


# Global settings instance
settings = Settings()
