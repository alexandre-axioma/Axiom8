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


async def n8n_documentation_search(query: str) -> dict:
    """
    Search n8n's official documentation, including core concepts, nodes, and guides.
    Use this for questions about how n8n works, node configurations, and general usage.
    """
    return await call_n8n_webhook(settings.n8n_documentation_search_url, query)

async def n8n_nodes_search(query: str) -> dict:
    """
    Search specifically for n8n nodes and integrations (e.g., Slack, Google Sheets, AWS).
    Use this to find out if a specific integration exists or how to configure a particular node.
    """
    return await call_n8n_webhook(settings.n8n_nodes_search_url, query)

async def n8n_workflows_search(query: str) -> dict:
    """
    Search a community library of real n8n workflow examples and templates.
    This is the best tool for finding practical, real-world examples of how to build workflows.
    """
    return await call_n8n_webhook(settings.n8n_workflows_search_url, query)

async def n8n_workflow_search(query: str) -> dict:
    """
    Search a library of real n8n workflow examples and implementation patterns.
    This is a high-priority tool for finding practical examples.
    """
    return await call_n8n_webhook(settings.n8n_workflow_search_url, query)


# A list of all tools that the agent can use.
all_tools = [
    n8n_documentation_search,
    n8n_nodes_search,
    n8n_workflows_search,
    n8n_workflow_search, # Including the duplicate for now, as it's in settings.
]
