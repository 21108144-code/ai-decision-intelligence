"""
LLM provider factory for easy switching between different providers.
Supports Ollama (local), OpenAI, Anthropic, and Google.
"""
from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from app.core.config import settings


def get_llm(temperature: float | None = None, **kwargs: Any) -> BaseChatModel:
    """
    Get LLM instance based on configured provider.
    
    Args:
        temperature: Override default temperature
        **kwargs: Additional provider-specific arguments
        
    Returns:
        BaseChatModel instance
        
    Raises:
        ValueError: If provider is not supported
    """
    temp = temperature if temperature is not None else settings.ollama_temperature
    
    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temp,
            **kwargs
        )
    
    elif settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=temp,
            **kwargs
        )
    
    elif settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=temp,
            **kwargs
        )
    
    elif settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        
        return ChatGoogleGenerativeAI(
            model=settings.google_model,
            google_api_key=settings.google_api_key,
            temperature=temp,
            **kwargs
        )
    
    elif settings.llm_provider == "groq":
        from langchain_groq import ChatGroq
        
        if not settings.groq_api_key:
            raise ValueError("Groq API key not configured")
        
        return ChatGroq(
            model=settings.groq_model,
            groq_api_key=settings.groq_api_key,
            temperature=temp,
            **kwargs
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def get_fast_llm(**kwargs: Any) -> BaseChatModel:
    """Get a faster, cheaper LLM for simple tasks."""
    if settings.llm_provider == "ollama":
        # Use same model but with higher temperature for creativity
        return get_llm(temperature=0.3, **kwargs)
    elif settings.llm_provider == "openai":
        return get_llm(model="gpt-3.5-turbo", **kwargs)
    else:
        return get_llm(**kwargs)


def get_smart_llm(**kwargs: Any) -> BaseChatModel:
    """Get the most capable LLM for complex reasoning."""
    if settings.llm_provider == "ollama":
        # Use same model but with lower temperature for precision
        return get_llm(temperature=0.1, **kwargs)
    elif settings.llm_provider == "openai":
        return get_llm(model="gpt-4", **kwargs)
    elif settings.llm_provider == "anthropic":
        return get_llm(model="claude-3-5-sonnet-20241022", **kwargs)
    else:
        return get_llm(**kwargs)
