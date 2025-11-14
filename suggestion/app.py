"""
Suggestion Service - AI-powered suggestion and recommendation engine
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
RELATED_SERVICE_URL = os.getenv('RELATED_SERVICE_URL', 'http://localhost:8001')
MULTIAGENT_SERVICE_URL = os.getenv('MULTIAGENT_SERVICE_URL', 'http://localhost:8002')

# Request/Response Models
class SuggestionRequest(BaseModel):
    query: str
    context: Optional[str] = None
    max_results: Optional[int] = 5

class SuggestionItem(BaseModel):
    text: str
    score: float
    source: str

class SuggestionResponse(BaseModel):
    suggestions: List[SuggestionItem]
    query: str
    timestamp: str

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Suggestion Service starting up...")
    yield
    logger.info("Suggestion Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Suggestion Service",
    description="AI-powered suggestion and recommendation engine",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "suggestion",
        "status": "running",
        "version": "1.0.0",
        "description": "AI-powered suggestion service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "service": "suggestion",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {}
    }
    
    # Check Related Service
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RELATED_SERVICE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    health_status["dependencies"]["related"] = "healthy"
                else:
                    health_status["dependencies"]["related"] = "unhealthy"
    except Exception as e:
        health_status["dependencies"]["related"] = f"unreachable: {str(e)}"
    
    # Check Multiagent Service
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{MULTIAGENT_SERVICE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    health_status["dependencies"]["multiagent"] = "healthy"
                else:
                    health_status["dependencies"]["multiagent"] = "unhealthy"
    except Exception as e:
        health_status["dependencies"]["multiagent"] = f"unreachable: {str(e)}"
    
    return health_status

@app.post("/suggest", response_model=SuggestionResponse)
async def get_suggestions(request: SuggestionRequest):
    """
    Get AI-powered suggestions based on query
    """
    try:
        logger.info(f"Received suggestion request: {request.query}")
        
        # Generate suggestions (mock implementation)
        suggestions = []
        
        # Add some mock suggestions based on query
        base_suggestions = [
            f"Consider {request.query} with additional context",
            f"Alternative approach to {request.query}",
            f"Best practices for {request.query}",
            f"Related topics to {request.query}",
            f"Advanced techniques for {request.query}"
        ]
        
        for idx, text in enumerate(base_suggestions[:request.max_results]):
            suggestions.append(SuggestionItem(
                text=text,
                score=0.9 - (idx * 0.1),
                source="suggestion"
            ))
        
        response = SuggestionResponse(
            suggestions=suggestions,
            query=request.query,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Generated {len(suggestions)} suggestions")
        return response
        
    except Exception as e:
        logger.error(f"Suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest/enhanced")
async def get_enhanced_suggestions(request: SuggestionRequest):
    """
    Get enhanced suggestions by combining with related and multiagent services
    """
    try:
        logger.info(f"Received enhanced suggestion request: {request.query}")
        
        all_suggestions = []
        
        # Get base suggestions
        base_response = await get_suggestions(request)
        all_suggestions.extend([s.dict() for s in base_response.suggestions])
        
        # Try to get related suggestions
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{RELATED_SERVICE_URL}/related",
                    json={"query": request.query, "max_results": 3},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        related_data = await resp.json()
                        for item in related_data.get("related_items", []):
                            all_suggestions.append({
                                "text": item["text"],
                                "score": item["score"],
                                "source": "related"
                            })
        except Exception as e:
            logger.warning(f"Could not fetch related suggestions: {str(e)}")
        
        # Try to get multiagent suggestions
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MULTIAGENT_SERVICE_URL}/agents/suggest",
                    json={"query": request.query, "agent_count": 2},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        agent_data = await resp.json()
                        for item in agent_data.get("agent_responses", []):
                            all_suggestions.append({
                                "text": item["suggestion"],
                                "score": item["confidence"],
                                "source": f"agent-{item['agent_id']}"
                            })
        except Exception as e:
            logger.warning(f"Could not fetch multiagent suggestions: {str(e)}")
        
        # Sort by score and limit results
        all_suggestions.sort(key=lambda x: x["score"], reverse=True)
        all_suggestions = all_suggestions[:request.max_results]
        
        return {
            "suggestions": all_suggestions,
            "query": request.query,
            "sources_used": list(set([s["source"] for s in all_suggestions])),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """
    Get service metrics
    """
    return {
        "service": "suggestion",
        "requests_total": 0,
        "cache_hit_rate": 0.0,
        "avg_response_time_ms": 0.0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Suggestion Service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
