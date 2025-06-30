import httpx
from pydantic import BaseModel, Field

from ..config.settings import get_settings

settings = get_settings()

class ToolError(BaseModel):
    """A model to represent a structured error from a tool."""
    error: str = Field(..., description="The error message that occurred.")


async def call_n8n_webhook(url: str, query: str) -> dict:
    """
    Asynchronously calls a specified n8n webhook with a query and handles potential errors.

    :param url: The webhook URL to call.
    :param query: The search query string.
    :return: A dictionary with the webhook response or a ToolError.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"query": query}, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return ToolError(error=f"HTTP error occurred: {e.response.status_code} - {e.response.text}").dict()
    except httpx.RequestError as e:
        return ToolError(error=f"An error occurred while requesting {e.request.url!r}: {e}").dict()


async def n8n_core_search(query: str) -> dict:
    """
    Search n8n core concepts and fundamentals.
    
    Content: Flow logic, data structures, basic node types, expression system, AI agents, execution models
    Use for: Understanding n8n fundamentals, validating architectural approaches, expression syntax, AI integration concepts
    """
    return await call_n8n_webhook(settings.n8n_core_search_url, query)

async def n8n_management_search(query: str) -> dict:
    """
    Search n8n deployment and administration documentation.
    
    Content: Self-hosting, Docker setup, scaling, enterprise features, security, operational guidance
    Use for: Infrastructure setup, environment configuration, scaling, user management, security, monitoring, troubleshooting operational issues
    """
    return await call_n8n_webhook(settings.n8n_management_search_url, query)

async def n8n_integrations_search(query: str) -> dict:
    """
    Search n8n nodes and integrations documentation.
    
    Content: 200+ nodes including HTTP Request, built-in nodes, external integrations (Slack, Google, AWS, etc.)
    Use for: Node configuration, API parameters, authentication setup, integration capabilities, troubleshooting specific nodes
    """
    return await call_n8n_webhook(settings.n8n_integrations_search_url, query)

async def n8n_workflows_search(query: str) -> dict:
    """
    Search real workflow examples and implementation patterns ⭐ HIGHEST PRIORITY
    
    Content: Community workflows (geral/) and user's personal workflows (proprietário/). Contains both documentation AND actual workflow JSON
    Use for: Implementation examples, architectural patterns, learning from similar use cases, validating approaches through real workflows
    
    This should be searched FIRST for practical examples!
    """
    return await call_n8n_webhook(settings.n8n_workflows_search_url, query)


# A list of all tools that the agent can use.
# Order matters: n8n_workflows_search should be tried FIRST for practical examples
all_tools = [
    n8n_workflows_search,     # ⭐ HIGHEST PRIORITY - Real workflow examples
    n8n_integrations_search,  # 200+ nodes and integrations  
    n8n_core_search,          # Core concepts and fundamentals
    n8n_management_search,    # Deployment and administration
]
