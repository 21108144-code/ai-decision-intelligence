"""
Simple query endpoint - bypasses LangGraph entirely for immediate results.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os

router = APIRouter(prefix="/api", tags=["simple"])

class SimpleQueryRequest(BaseModel):
    query: str

class SimpleQueryResponse(BaseModel):
    query: str
    response: str
    model: str = "llama-3.3-70b-versatile"

@router.post("/simple-query", response_model=SimpleQueryResponse)
async def simple_query(request: SimpleQueryRequest):
    """
    Simple endpoint that calls Groq directly without any agent orchestration.
    Use this for immediate results.
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        # Initialize Groq LLM
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7
        )
        
        # Create messages
        messages = [
            SystemMessage(content="""You are an AI business analyst and decision intelligence assistant.
Provide comprehensive, well-reasoned analysis for business questions.
Include:
- Clear recommendations
- Risk assessment
- Alternative options
- Implementation considerations
Be professional, thorough, and actionable."""),
            HumanMessage(content=request.query)
        ]
        
        # Get response
        response = await llm.ainvoke(messages)
        
        return SimpleQueryResponse(
            query=request.query,
            response=response.content
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
