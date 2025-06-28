from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""

    query: str = Field(
        ...,
        description="The user's query or message.",
        examples=["Create a workflow to get the weather and send it to Slack."],
    )
    session_id: Optional[str] = Field(
        None,
        description="A unique session ID to maintain conversation history.",
        examples=["e8b5a8e3-b27e-4bfa-8f5b-9d2a1b3c4d5e"],
    )


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""

    session_id: str = Field(
        ...,
        description="The session ID for the conversation.",
        examples=["e8b5a8e3-b27e-4bfa-8f5b-9d2a1b3c4d5e"],
    )
    output: str = Field(
        ...,
        description="The output from the agent.",
        examples=["Here is the generated workflow: ..."],
    )
