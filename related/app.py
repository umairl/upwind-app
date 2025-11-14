"""
Related Service - Find related content using semantic similarity
"""
import os
import logging
import random
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response Models
class RelatedRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    threshold: Optional[float] = 0.5

class RelatedItem(BaseModel):
    text: str
    score: float
    category: str

class RelatedResponse(BaseModel):
    related_items: List[RelatedItem]
    query: str
    timestamp: str

# Mock database of content
CONTENT_DATABASE = [
    {"text": "Machine learning algorithms for prediction", "category": "ML"},
    {"text": "Deep learning neural networks", "category": "AI"},
    {"text": "Natural language processing techniques", "category": "NLP"},
    {"text": "Computer vision and image recognition", "category": "CV"},
    {"text": "Data preprocessing and cleaning", "category": "Data"},
    {"text": "Feature engineering best practices", "category": "Data"},
    {"text": "Model evaluation and metrics", "category": "ML"},
    {"text": "Deployment strategies for ML models", "category": "MLOps"},
    {"text": "Kubernetes orchestration patterns", "category": "DevOps"},
    {"text": "Docker containerization guide", "category": "DevOps"},
    {"text": "CI/CD pipeline automation", "category": "DevOps"},
    {"text": "Cloud infrastructure management", "category": "Cloud"},
    {"text": "API design and best practices", "category": "API"},
    {"text": "Microservices architecture patterns", "category": "Architecture"},
    {"text": "Database optimization techniques", "category": "Database"},
]

# Simple similarity calculator
def calculate_similarity(query: str, text: str) -> float:
    """
    Mock similarity calculation
    In production, this would use sentence embeddings
    """
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    
    if not query_words or not text_words:
        return 0.0
    
    intersection = query_words.intersection(text_words)
    union = query_words.union(text_words)
    
    # Jaccard similarity with some randomness
    base_similarity = len(intersection) / len(union) if union else 0.0
    noise = random.uniform(-0.1, 0.1)
    
    return max(0.0, min(1.0, base_similarity + noise + 0.3))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown"""
    logger.info("Related Service starting up...")
    logger.info("Initializing similarity model...")
    # In production, load sentence transformer model here
    logger.info("Model initialized successfully")
    yield
    logger.info("Related Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Related Service",
    description="Find semantically related content",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "related",
        "status": "running",
        "version": "1.0.0",
        "description": "Semantic similarity and related content service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "related",
        "status": "healthy",
        "model_loaded": True,
        "content_items": len(CONTENT_DATABASE),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/related", response_model=RelatedResponse)
async def find_related(request: RelatedRequest):
    """
    Find related content based on semantic similarity
    """
    try:
        logger.info(f"Finding related content for: {request.query}")
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Calculate similarity scores for all content
        scored_items = []
        for item in CONTENT_DATABASE:
            score = calculate_similarity(request.query, item["text"])
            if score >= request.threshold:
                scored_items.append({
                    "text": item["text"],
                    "score": round(score, 4),
                    "category": item["category"]
                })
        
        # Sort by score descending
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit results
        scored_items = scored_items[:request.max_results]
        
        related_items = [RelatedItem(**item) for item in scored_items]
        
        response = RelatedResponse(
            related_items=related_items,
            query=request.query,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Found {len(related_items)} related items")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Related search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similarity")
async def calculate_similarity_endpoint(text1: str, text2: str):
    """
    Calculate similarity between two texts
    """
    try:
        score = calculate_similarity(text1, text2)
        return {
            "text1": text1,
            "text2": text2,
            "similarity_score": round(score, 4),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Similarity calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content/stats")
async def get_content_stats():
    """
    Get statistics about the content database
    """
    categories = {}
    for item in CONTENT_DATABASE:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_items": len(CONTENT_DATABASE),
        "categories": categories,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """
    Get service metrics
    """
    return {
        "service": "related",
        "total_searches": 0,
        "avg_results_per_search": 0.0,
        "cache_hit_rate": 0.0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8001))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Related Service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
