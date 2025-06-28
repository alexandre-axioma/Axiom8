from ..services import rag_service

# Each function is a potential tool for the PydanticAI agent.
# The agent uses the function's signature and docstring to decide when to call it.
# PydanticAI does not require a special decorator, just a plain Python function.


async def n8n_core_search(query: str, max_results: int = 5) -> str:
    """Search n8n core concepts and fundamentals. Use this to understand n8n's
    foundational features, flow logic, data structures, expression system,
    and execution models."""
    return await rag_service.n8n_core_search(query, max_results)


async def n8n_management_search(query: str, max_results: int = 5) -> str:
    """Search n8n deployment and administration documentation. Use this for topics
    like self-hosting, Docker setup, scaling, security, and operational guidance."""
    return await rag_service.n8n_management_search(query, max_results)


async def n8n_integrations_search(query: str, max_results: int = 5) -> str:
    """Search documentation for over 200 n8n nodes and integrations, such as
    HTTP Request, Slack, Google, and AWS. Use this to understand node configuration,
    API parameters, and authentication setups."""
    return await rag_service.n8n_integrations_search(query, max_results)


async def n8n_workflows_search(query: str, max_results: int = 5) -> str:
    """Search a library of real n8n workflow examples and implementation patterns.
    This is the highest priority tool for finding practical, real-world examples.
    Use this to see how others have solved similar problems."""
    return await rag_service.n8n_workflows_search(query, max_results)


# A list of all tools that the agent can use.
# This list will be passed to the agent runtime.
all_tools = [
    n8n_core_search,
    n8n_management_search,
    n8n_integrations_search,
    n8n_workflows_search,
]
