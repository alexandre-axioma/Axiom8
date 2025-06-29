# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Axiom8** is an Agentic RAG system that automatically generates production-ready n8n workflows from natural language descriptions. The system transforms user workflow ideas into complete, importable n8n workflow JSON files.

**Architecture**: Python FastAPI backend with multi-agent system using LangGraph orchestration. Two specialized agents: Requirements Analyst (OpenAI o3-mini) and Workflow Generator (Claude Opus 4), integrated with n8n via HTTP/webhooks.

## Development Environment

**Python Environment**: Anaconda environment named `axiom8` with Python 3.11.13

**Environment Setup**:
```bash
conda activate axiom8
cd agentic_rag
pip install -r requirements.txt
```

**Environment Variables**: Copy required variables from `/agentic_rag/.env`:
- `ANTHROPIC_API_KEY` - Claude API access for Workflow Generator
- `OPENAI_API_KEY` - OpenAI API access for Requirements Analyst
- `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` - LangSmith observability 
- `N8N_*_URL` variables - Four n8n RAG webhook endpoints

## Common Commands

**Run Development Server**:
```bash
cd agentic_rag
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Test Agent Locally**:
```bash
cd agentic_rag/scripts
python test_local.py
```

**Health Check**:
```bash
curl http://127.0.0.1:8000/health
```

**Run Tests** (when implemented):
```bash
pytest tests/
```

## Code Architecture

### Core Structure
- `app/main.py` - FastAPI application entry point
- `app/agent/agent.py` - Legacy single PydanticAI agent (backward compatibility)
- `app/agent/multi_agent.py` - Multi-agent system with LangGraph orchestration
- `app/agent/tools.py` - RAG tools that call n8n webhooks for documentation search
- `app/api/routes.py` - HTTP endpoints (legacy `/invoke`, new `/chat/start`, `/chat/continue`)
- `app/config/settings.py` - Environment configuration with Pydantic settings

### RAG Integration
The system uses **4 specialized n8n RAG databases** accessed via webhooks:
1. `n8n_workflows` - Real workflow examples (highest priority)
2. `n8n_integrations` - 200+ nodes documentation
3. `n8n_core` - Core concepts and expressions
4. `n8n_management` - Deployment and administration

### Key Technologies
- **PydanticAI**: Agent framework for individual AI agents
- **LangGraph**: Multi-agent orchestration and state management
- **FastAPI**: Web framework with async support
- **Anthropic API**: Claude Sonnet for Workflow Generator agent
- **OpenAI API**: o3-mini for Requirements Analyst agent
- **LangSmith**: Observability and tracing
- **HTTPx**: Async HTTP client for n8n webhook calls

### Multi-Agent System
**Requirements Analyst Agent (OpenAI o3-mini)**:
- Analyzes user requests for n8n workflows
- Asks clarifying questions when requirements are unclear
- Creates structured requirements documents
- Cost-optimized for conversational/analytical tasks

**Workflow Generator Agent (Claude Opus 4)**:
- Builds production-ready n8n workflows from structured requirements
- Uses RAG tools to search n8n documentation and examples
- Outputs complete JSON workflows ready for import
- Premium model for complex technical generation

**LangGraph Orchestration**:
- Manages conversation flow between agents
- Handles state management and routing decisions
- Supports iterative refinement and user feedback
- Maintains session context across interactions

## Development Context

**Project Documentation**: Essential context in `/agentic_rag/00_project_log/`:
- `00_project_overview.md` - Complete project background
- `01_important_links.md` - Critical documentation links
- `02-tasks.md` - Current development roadmap

**Development Rules**: Always consult official documentation before implementation. Use Context7 MCP tools for research. For the liraries names and ID's you can visit the `01_important_links.md` file.   

**Architecture Evolution**: Successfully implemented two-agent system (Requirements Analyst + Workflow Generator) with LangGraph orchestration. Legacy single-agent endpoint maintained for backward compatibility.

## Integration Points

**n8n Integration**: The Python agent replaces n8n's LangChain Code node, receiving workflow requests via HTTP and returning complete n8n workflow JSON.

**Session Management**: Implemented in `services/session_service.py` for conversational workflow refinement.

**API Endpoints**:
- **Legacy**: `POST /api/v1/invoke` - Single-shot workflow generation (backward compatibility)
- **Multi-Agent**: `POST /api/v1/chat/start` - Start conversational session  
- **Multi-Agent**: `POST /api/v1/chat/continue` - Continue conversation with additional context
- **Multi-Agent**: `GET /api/v1/chat/{session_id}/history` - Retrieve conversation history

**Observability**: LangSmith tracing enabled for debugging and optimization across both single-agent and multi-agent flows.