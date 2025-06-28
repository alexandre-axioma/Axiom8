# Axiom8 Implementation Tasks

This document outlines the development tasks for building the Axiom8 agent. It will be updated as the project progresses.

## Phase 1: Foundation and Services

### Step 1: Environment & Configuration
- [ ] Review `requirements.txt` and add any missing dependencies (`fastapi`, `uvicorn`, `pydantic-ai`, `langgraph`, `anthropic`, `httpx`, `python-dotenv`, `langchain-langsmith`).
- [ ] Create `.env.example` file listing all required environment variables (`ANTHROPIC_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`).
- [ ] Implement `app/config/settings.py` to load environment variables using Pydantic's `BaseSettings`.
- [ ] Add `__init__.py` to all necessary directories to ensure they are treated as Python packages.

### Step 2: Core Service Implementation
- [ ] Define the RAG tool functions in `app/services/rag_service.py`.
    - [ ] Create an async function `call_rag_tool` using `httpx.AsyncClient`.
    - [ ] Create wrapper functions for each of the four RAG tools:
        - [ ] `n8n_core_search`
        - [ ] `n8n_management_search`
        - [ ] `n8n_integrations_search`
        - [ ] `n8n_workflows_search`
- [ ] Implement `app/services/claude_service.py` to provide a singleton instance of the Anthropic client.

## Phase 2: Agent and Orchestration

### Step 3: Agent State Definition
- [ ] Define the `AgentState` TypedDict in `app/agent/state.py` to manage the graph's state.
    - [ ] Include fields for `messages`, `user_query`, `structured_requirements`, `tool_outputs`, `final_workflow`, etc.

### Step 4: Agent Tools
- [ ] Create Python tool functions in `app/agent/tools.py`.
- [ ] Wrap each function from `rag_service.py` with the `@tool` decorator from `langchain_core.tools`.

### Step 5: Agent Nodes
- [ ] Implement the primary agent logic in `app/agent/nodes.py`.
    - [ ] Create `requirements_analyst_node`.
        - [ ] This node will invoke the LLM with the user query and chat history.
        - [ ] It will decide if more information is needed or if the requirements are clear.
    - [ ] Create `workflow_generator_node`.
        - [ ] This node will take structured requirements.
        - [ ] It will decide which RAG tools to call via the `ToolNode`.
        - [ ] It will generate the final n8n workflow JSON.
    - [ ] Define the logic for a `conditional_edge` to route between the nodes.

### Step 6: Graph Orchestration
- [ ] Build the `StatefulGraph` in `app/agent/graph.py`.
    - [ ] Instantiate the graph with the `AgentState`.
    - [ ] Add the `requirements_analyst_node` as the entry point.
    - [ ] Add a `ToolNode` to execute the RAG tools.
    - [ ] Add the `workflow_generator_node`.
    - [ ] Define the conditional edges to manage the flow:
        - [ ] `(requirements_analyst)` -> `(conditional_edge)`
        - [ ] `(conditional_edge)` -> `(workflow_generator)` OR `(end)`
        - [ ] `(workflow_generator)` -> `(tool_node)` OR `(end)`
        - [ ] `(tool_node)` -> `(workflow_generator)`
    - [ ] Compile the graph into a runnable `app`.

## Phase 3: API and Finalization

### Step 7: API Layer
- [ ] Define API data models in `app/api/models.py`.
    - [ ] Create a `ChatRequest` model for incoming requests from n8n.
    - [ ] Create a `ChatResponse` model for streaming responses back.
- [ ] Implement API routes in `app/api/routes.py`.
    - [ ] Create a new `APIRouter`.
    - [ ] Define the `/agent/invoke` endpoint.
    - [ ] The endpoint will accept `ChatRequest` and stream back `ChatResponse` objects.
    - [ ] The endpoint will call the compiled LangGraph `app.astream_events(...)`.

### Step 8: Application Entrypoint
- [ ] Configure the FastAPI app in `app/main.py`.
    - [ ] Create the FastAPI app instance.
    - [ ] Include the API router from `app/api/routes.py`.
    - [ ] Configure CORS middleware if necessary.

### Step 9: Testing and Refinement
- [ ] Create `scripts/test_local.py` to send a sample request to the running API for easy testing.
- [ ] Create unit tests in the `tests/` directory.
    - [ ] `test_api.py` for API endpoint validation.
    - [ ] `test_agent.py` for agent graph logic.
- [ ] Refine prompts and agent logic based on test results.
- [ ] Write a `README.md` with instructions on how to set up and run the project. 