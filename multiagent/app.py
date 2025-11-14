"""
Multiagent Service - Multi-agent AI system for collaborative problem solving
"""
import os
import logging
import asyncio
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    agent_count: Optional[int] = 3
    timeout: Optional[int] = 30

class AgentResponse(BaseModel):
    agent_id: str
    suggestion: str
    confidence: float
    reasoning: Optional[str] = None

class MultiAgentResponse(BaseModel):
    agent_responses: List[AgentResponse]
    consensus: Optional[str] = None
    consensus_score: float
    query: str
    timestamp: str

class AgentTaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    agent_count: Optional[int] = 3

# Agent personalities and specializations
AGENT_PROFILES = [
    {
        "id": "analyzer",
        "name": "Analytical Agent",
        "specialty": "Data analysis and logical reasoning",
        "approach": "analytical"
    },
    {
        "id": "creative",
        "name": "Creative Agent",
        "specialty": "Creative problem solving",
        "approach": "creative"
    },
    {
        "id": "pragmatic",
        "name": "Pragmatic Agent",
        "specialty": "Practical solutions",
        "approach": "pragmatic"
    },
    {
        "id": "optimizer",
        "name": "Optimizer Agent",
        "specialty": "Performance optimization",
        "approach": "optimization"
    },
    {
        "id": "security",
        "name": "Security Agent",
        "specialty": "Security and risk assessment",
        "approach": "security-focused"
    }
]

async def agent_process(agent_profile: Dict, query: str, delay: float = 1.0) -> AgentResponse:
    """
    Simulate an agent processing a query
    """
    # Simulate processing time
    await asyncio.sleep(delay)
    
    agent_id = agent_profile["id"]
    specialty = agent_profile["specialty"]
    
    # Generate a response based on agent type
    suggestions = {
        "analyzer": f"Based on analysis of '{query}', consider data-driven approach with metrics",
        "creative": f"Innovative solution for '{query}': think outside the box with novel methods",
        "pragmatic": f"Practical approach to '{query}': focus on immediate, actionable steps",
        "optimizer": f"Optimized solution for '{query}': maximize efficiency and minimize resources",
        "security": f"Secure implementation of '{query}': prioritize safety and risk mitigation"
    }
    
    suggestion = suggestions.get(agent_id, f"Agent {agent_id} suggests reviewing '{query}' carefully")
    confidence = random.uniform(0.7, 0.95)
    
    return AgentResponse(
        agent_id=agent_id,
        suggestion=suggestion,
        confidence=round(confidence, 4),
        reasoning=f"Based on {specialty} perspective"
    )

def calculate_consensus(responses: List[AgentResponse]) -> tuple:
    """
    Calculate consensus from multiple agent responses
    """
    if not responses:
        return None, 0.0
    
    # Average confidence as consensus score
    avg_confidence = sum(r.confidence for r in responses) / len(responses)
    
    # Mock consensus - in production, use NLP to find common themes
    consensus = f"Agents agree to combine analytical, creative, and practical approaches"
    
    return consensus, round(avg_confidence, 4)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Multiagent Service starting up...")
    logger.info(f"Initialized {len(AGENT_PROFILES)} agent profiles")
    yield
    logger.info("Multiagent Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Multiagent Service",
    description="Multi-agent AI system for collaborative problem solving",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "multiagent",
        "status": "running",
        "version": "1.0.0",
        "description": "Multi-agent collaborative AI system",
        "available_agents": len(AGENT_PROFILES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "multiagent",
        "status": "healthy",
        "active_agents": len(AGENT_PROFILES),
        "agent_profiles": [a["id"] for a in AGENT_PROFILES],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents/suggest", response_model=MultiAgentResponse)
async def multi_agent_suggest(request: AgentRequest):
    """
    Get suggestions from multiple agents working in parallel
    """
    try:
        logger.info(f"Multi-agent request: {request.query} with {request.agent_count} agents")
        
        if request.agent_count < 1 or request.agent_count > len(AGENT_PROFILES):
            raise HTTPException(
                status_code=400,
                detail=f"Agent count must be between 1 and {len(AGENT_PROFILES)}"
            )
        
        # Select agents
        selected_agents = AGENT_PROFILES[:request.agent_count]
        
        # Run agents in parallel
        tasks = [
            agent_process(agent, request.query, delay=random.uniform(0.5, 2.0))
            for agent in selected_agents
        ]
        
        # Wait for all agents with timeout
        try:
            agent_responses = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=request.timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Agent processing timeout")
        
        # Calculate consensus
        consensus, consensus_score = calculate_consensus(agent_responses)
        
        response = MultiAgentResponse(
            agent_responses=agent_responses,
            consensus=consensus,
            consensus_score=consensus_score,
            query=request.query,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Multi-agent processing complete with {len(agent_responses)} responses")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/task")
async def create_agent_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    """
    Create a background task for agents to process
    """
    try:
        task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Creating agent task: {request.task_type} (ID: {task_id})")
        
        # In production, this would queue the task
        # For now, return task created status
        
        return {
            "task_id": task_id,
            "task_type": request.task_type,
            "agent_count": request.agent_count,
            "status": "queued",
            "message": "Task created successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Task creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/profiles")
async def get_agent_profiles():
    """
    Get all available agent profiles
    """
    return {
        "agents": AGENT_PROFILES,
        "total_agents": len(AGENT_PROFILES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents/{agent_id}")
async def get_agent_profile(agent_id: str):
    """
    Get specific agent profile
    """
    agent = next((a for a in AGENT_PROFILES if a["id"] == agent_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent": agent,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents/vote")
async def vote_on_solutions(solutions: List[str], voter_count: int = 3):
    """
    Have multiple agents vote on proposed solutions
    """
    try:
        if voter_count > len(AGENT_PROFILES):
            voter_count = len(AGENT_PROFILES)
        
        voters = AGENT_PROFILES[:voter_count]
        votes = {}
        
        for solution in solutions:
            votes[solution] = {
                "votes": random.randint(0, voter_count),
                "confidence": round(random.uniform(0.6, 0.95), 4)
            }
        
        # Find winner
        winner = max(votes.items(), key=lambda x: x[1]["votes"])
        
        return {
            "solutions": solutions,
            "votes": votes,
            "winner": {
                "solution": winner[0],
                "votes": winner[1]["votes"],
                "confidence": winner[1]["confidence"]
            },
            "voter_count": voter_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Voting error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """
    Get service metrics
    """
    return {
        "service": "multiagent",
        "total_requests": 0,
        "active_agents": len(AGENT_PROFILES),
        "avg_consensus_score": 0.0,
        "avg_processing_time_ms": 0.0,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8002))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Multiagent Service on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
