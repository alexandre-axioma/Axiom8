from __future__ import annotations

from typing import Any, List, Optional

import httpx
from loguru import logger

from ..config.settings import get_settings

settings = get_settings()


async def call_rag_tool(
    url: str, query: str, max_results: int = 5, **kwargs: Optional[Any]
) -> List[dict[str, Any]]:
    """
    Asynchronously calls a specific RAG tool webhook.

    Args:
        url: The webhook URL of the RAG tool.
        query: The search query string.
        max_results: The maximum number of results to return.
        **kwargs: Additional filter parameters for the payload.

    Returns:
        A list of documents from the RAG tool.
    """
    payload = {"query": query, "max_results": max_results, "filters": kwargs}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            logger.info(f"RAG tool at {url} returned {len(results)} results for query: '{query}'")
            return results
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling RAG tool at {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred when calling RAG tool at {url}: {e}")
            return []


async def n8n_core_search(
    query: str, max_results: int = 5, **kwargs: Optional[Any]
) -> List[dict[str, Any]]:
    """Search n8n core concepts and fundamentals."""
    return await call_rag_tool(
        str(settings.n8n_core_rag_url), query, max_results, **kwargs
    )


async def n8n_management_search(
    query: str, max_results: int = 5, **kwargs: Optional[Any]
) -> List[dict[str, Any]]:
    """Search n8n deployment and administration documentation."""
    return await call_rag_tool(
        str(settings.n8n_management_rag_url), query, max_results, **kwargs
    )


async def n8n_integrations_search(
    query: str, max_results: int = 5, **kwargs: Optional[Any]
) -> List[dict[str, Any]]:
    """Search n8n nodes and integrations documentation."""
    return await call_rag_tool(
        str(settings.n8n_integrations_rag_url), query, max_results, **kwargs
    )


async def n8n_workflows_search(
    query: str, max_results: int = 5, **kwargs: Optional[Any]
) -> List[dict[str, Any]]:
    """Search real workflow examples and implementation patterns."""
    return await call_rag_tool(
        str(settings.n8n_workflows_rag_url), query, max_results, **kwargs
    )
