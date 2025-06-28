from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel
import uuid
from loguru import logger

from ..agent.graph import get_agent
from pydantic_ai import Agent

router = APIRouter()

class InvokeRequest(BaseModel):
    query: str

class InvokeResponse(BaseModel):
    session_id: str
    output: str

@router.post("/invoke", response_model=InvokeResponse, tags=["Agent"])
async def invoke_agent(
    request: InvokeRequest, 
    agent: Agent = Depends(get_agent)
):
    """
    Invokes the PydanticAI agent with a query and returns the final result.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Invoking agent for session_id: {session_id} with query: '{request.query}'")

    try:
        response = await agent.run(request.query)
        logger.info(f"Agent execution successful for session {session_id}.")
        return InvokeResponse(session_id=session_id, output=response.output)
    except Exception as e:
        logger.error(f"Agent execution failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
