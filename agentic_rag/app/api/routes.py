from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from loguru import logger
from langchain_core.messages import HumanMessage

from ..agent.agent import workflow_generator_agent
from ..agent.multi_agent_unified_tracing import execute_unified_multi_agent_workflow, MultiAgentState
from ..services.session_service import SessionService

router = APIRouter()

# Initialize session service for managing conversations
session_service = SessionService()

# ============================================================================
# Legacy Single Agent API (Backward Compatibility)
# ============================================================================

class InvokeRequest(BaseModel):
    query: str

class InvokeResponse(BaseModel):
    session_id: str
    output: str

# ============================================================================
# New Multi-Agent Conversational API
# ============================================================================

class ChatStartRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ChatContinueRequest(BaseModel):
    session_id: str
    message: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage
    conversation_complete: bool = False
    current_agent: str
    metadata: Optional[Dict[str, Any]] = None

@router.post("/invoke", response_model=InvokeResponse, tags=["Legacy Agent"])
async def invoke_agent(request: InvokeRequest):
    """
    Legacy endpoint: Invokes the single PydanticAI agent with a query and returns the final result.
    
    This endpoint is maintained for backward compatibility.
    For new implementations, use /chat/start and /chat/continue endpoints.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Invoking legacy agent for session_id: {session_id} with query: '{request.query}'")

    try:
        # PydanticAI's .run() is a coroutine and must be awaited.
        response_obj = await workflow_generator_agent.run(request.query)
        logger.info(f"Legacy agent execution successful for session {session_id}.")
        # The actual string result is in the .output attribute of the returned object.
        return InvokeResponse(session_id=session_id, output=response_obj.output)
    except Exception as e:
        logger.error(f"Legacy agent execution failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Multi-Agent Conversational Endpoints
# ============================================================================

@router.post("/chat/start", response_model=ChatResponse, tags=["Multi-Agent Chat"])
async def start_chat(request: ChatStartRequest):
    """
    Start a new conversational session with the multi-agent system.
    
    This initiates a conversation where:
    1. Requirements Analyst (o3-mini) analyzes the user's request
    2. If clarification is needed, the system asks follow-up questions
    3. Once requirements are clear, Workflow Generator (Claude Opus 4) creates the n8n workflow
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Starting multi-agent chat for session_id: {session_id} with query: '{request.query}'")
    
    try:
        # Initialize the conversation state
        initial_state = MultiAgentState(
            messages=[HumanMessage(content=request.query)],
            step="analyze_requirements",
            requirements=None,
            final_workflow=None,
            error_message=None
        )
        
        # Run the multi-agent workflow with unified tracing
        result = await execute_unified_multi_agent_workflow(initial_state, session_id, "start")
        
        # Extract the assistant's response
        last_message = result["messages"][-1] if result["messages"] else None
        if not last_message:
            raise HTTPException(status_code=500, detail="No response from multi-agent system")
        
        # Store conversation state in session
        session_service.append_message(session_id, {
            "role": "user",
            "content": request.query,
            "timestamp": str(uuid.uuid4())  # Using UUID as timestamp placeholder
        })
        
        session_service.append_message(session_id, {
            "role": "assistant", 
            "content": last_message.content,
            "timestamp": str(uuid.uuid4())
        })
        
        # Create response
        response_message = ChatMessage(
            role="assistant",
            content=last_message.content,
            timestamp=str(uuid.uuid4())
        )
        
        logger.info(f"Multi-agent chat started successfully for session {session_id}")
        
        return ChatResponse(
            session_id=session_id,
            message=response_message,
            conversation_complete=result.get("step") == "complete",
            current_agent=result.get("step", "analyze_requirements"),
            metadata={
                "requirements_complete": result.get("requirements") is not None,
                "workflow_generated": result.get("final_workflow") is not None,
                "error": result.get("error_message")
            }
        )
        
    except Exception as e:
        logger.error(f"Multi-agent chat start failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")


@router.post("/chat/continue", response_model=ChatResponse, tags=["Multi-Agent Chat"])
async def continue_chat(request: ChatContinueRequest):
    """
    Continue an existing conversational session.
    
    Send additional messages to refine requirements or ask follow-up questions.
    The system will route to the appropriate agent based on the conversation state.
    """
    logger.info(f"Continuing multi-agent chat for session_id: {request.session_id} with message: '{request.message}'")
    
    try:
        # Get conversation history
        history = session_service.get_history(request.session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Reconstruct conversation state
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(HumanMessage(content=msg["content"]))  # Simplified for now
        
        # Add new user message
        messages.append(HumanMessage(content=request.message))
        
        # Create current state (simplified - in production, you'd persist full state)
        current_state = MultiAgentState(
            messages=messages,
            step="analyze_requirements",  # Default to requirements analysis
            requirements=None,
            final_workflow=None,
            error_message=None
        )
        
        # Continue the conversation with unified tracing
        result = await execute_unified_multi_agent_workflow(current_state, request.session_id, "continue")
        
        # Extract response
        last_message = result["messages"][-1] if result["messages"] else None
        if not last_message:
            raise HTTPException(status_code=500, detail="No response from multi-agent system")
        
        # Update session history
        session_service.append_message(request.session_id, {
            "role": "user",
            "content": request.message,
            "timestamp": str(uuid.uuid4())
        })
        
        session_service.append_message(request.session_id, {
            "role": "assistant",
            "content": last_message.content,
            "timestamp": str(uuid.uuid4())
        })
        
        # Create response
        response_message = ChatMessage(
            role="assistant",
            content=last_message.content,
            timestamp=str(uuid.uuid4())
        )
        
        logger.info(f"Multi-agent chat continued successfully for session {request.session_id}")
        
        return ChatResponse(
            session_id=request.session_id,
            message=response_message,
            conversation_complete=result.get("step") == "complete",
            current_agent=result.get("step", "analyze_requirements"),
            metadata={
                "requirements_complete": result.get("requirements") is not None,
                "workflow_generated": result.get("final_workflow") is not None,
                "error": result.get("error_message")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-agent chat continue failed for session {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to continue chat: {str(e)}")


@router.get("/chat/{session_id}/history", tags=["Multi-Agent Chat"])
async def get_chat_history(session_id: str):
    """
    Retrieve the conversation history for a session.
    """
    try:
        history = session_service.get_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "messages": history,
            "message_count": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat history for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")
