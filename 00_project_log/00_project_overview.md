# Project Overview: Axiom8 - Agentic RAG for n8n Workflow Generation

**Project Start Date:** June 27, 2025  
**Version:** 1.0 (Initial Context)

## 📋 Table of Contents
- [Project Vision](#project-vision)
- [Current State](#current-state)
- [Target State](#target-state)
- [Available RAG Tools](#available-rag-tools)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Development Environment](#development-environment)
- [Integration Requirements](#integration-requirements)
- [Success Criteria](#success-criteria)

## 🎯 Project Vision

### What is Axiom8?
**Axiom8** is an agentic RAG system designed to automatically generate **production-ready n8n workflows** based on user ideas and requirements.

### Core Use Case
**Input:** User provides a workflow idea (e.g., "Monitor inventory spreadsheet and send email alerts when stock is low")  
**Output:** Complete, production-ready n8n workflow with all necessary nodes, configurations, and connections

### Secondary Use Cases
- **Workflow refinement:** Iterative improvements based on user feedback
- **Troubleshooting:** Help users solve specific n8n node errors or issues
- **Best practices:** Suggest n8n workflow optimizations and patterns

## 🏗️ Current State

### Existing n8n RAG Implementation
We have a functional RAG system built entirely in n8n with the following architecture:

```
┌─────────────────┐
│   Chat Node     │ ← User Interface
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ LangChain Code  │ ← AI Processing (Limited)
│     Node        │
└─────────────────┘
         │
         ▼ (calls all 4 tools)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   n8n Core      │  │ n8n Management  │  │ n8n Integrations│  │ n8n Workflows   │
│     Tool        │  │     Tool        │  │     Tool        │  │     Tool        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Current Limitations
1. **LangChain Code Node** runs outdated JavaScript libraries
2. **No access to Claude Opus 4** advanced features (thinking, prompt caching, built-in tools)
3. **Limited AI capabilities** - cannot use latest Anthropic features
4. **No PydanticAI support** in n8n environment

## 🚀 Target State

### New Architecture Vision
```
┌─────────────────┐    HTTP      ┌─────────────────┐    Webhooks    ┌─────────────────┐
│   n8n Chat      │ ──────────► │ Python Agent    │ ────────────► │  4 RAG Tools    │
│     Node        │             │   (Axiom8)      │               │  (as Webhooks)  │
└─────────────────┘             └─────────────────┘               └─────────────────┘
```

### Agent Architecture
**Two-Agent System using PydanticAI:**

1. **Requirements Agent**
   - Analyzes user input for completeness
   - Asks clarifying questions when needed
   - Breaks down requirements into detailed specifications
   - Outputs structured requirements for workflow generation

2. **Workflow Generator Agent**  
   - Takes detailed requirements from Requirements Agent
   - Uses RAG tools to find relevant n8n patterns and nodes
   - Generates complete n8n workflow JSON
   - Ensures production-ready configuration

**Orchestration:** LangGraph manages the flow between both agents

## 🛠️ Available RAG Tools

### Tool 1: n8n Core
**Purpose:** Search n8n core concepts and fundamentals  
**Content:** Flow logic, data structures, basic node types, expression system, AI agents, execution models  
**Parameters:**
- `query` (required): Search term in English for core concepts
- `max_results` (optional): Number of results (1-10, default: 5)  
- `filters` (optional): Object with exclude_chunk_ids array and/or filter_file_name string

**Use for:** Understanding n8n fundamentals, validating architectural approaches, expression syntax, AI integration concepts

### Tool 2: n8n Management  
**Purpose:** Search n8n deployment and administration documentation  
**Content:** Self-hosting, Docker setup, scaling, enterprise features, security, operational guidance  
**Parameters:** Same as Core tool

**Use for:** Infrastructure setup, environment configuration, scaling, user management, security, monitoring, troubleshooting operational issues

### Tool 3: n8n Integrations
**Purpose:** Search n8n nodes and integrations documentation  
**Content:** 200+ nodes including HTTP Request, built-in nodes, external integrations (Slack, Google, AWS, etc.)  
**Parameters:** Same as Core tool

**Use for:** Node configuration, API parameters, authentication setup, integration capabilities, troubleshooting specific nodes

### Tool 4: n8n Workflows ⭐ 
**Purpose:** Search real workflow examples and implementation patterns  
**Content:** Community workflows (geral/) and user's personal workflows (proprietário/). Contains both documentation AND actual workflow JSON  
**Parameters:**
- `query` (required): Search term for workflow examples or automation patterns
- `max_results` (optional): Number of results (1-10, default: 5)
- `filters` (optional): 
  - `filter_workflow_scope`: "proprietário" for user's workflows, "geral" for community
  - `filter_integrations`: array of integration names
  - `exclude_file_ids`: array of file IDs to exclude

**Use for:** Implementation examples, architectural patterns, learning from similar use cases, validating approaches through real workflows. **MAXIMUM PRIORITY** - search here first for practical examples

### RAG Tool Characteristics
- Each tool performs **complete search pipeline**: Hybrid Search (RRF algorithm) + Cohere 3.5 rerank
- **Input:** HTTP request with parameters
- **Output:** Ranked, relevant results ready for agent consumption
- **Current trigger:** Subworkflow (will change to Webhook)

## 💻 Technology Stack

### Core Technologies
- **PydanticAI:** Agent framework for building AI agents
- **LangGraph:** Orchestration between multiple agents  
- **FastAPI:** Web framework for API endpoints
- **Anthropic API:** Claude Opus 4 with full capabilities
- **LangSmith:** Monitoring and observability (user has account)

### Development Environment
- **Python 3.11.13** (Anaconda environment: `axiom8`)
- **Platform:** Windows 11 + PowerShell + Cursor IDE
- **Dependencies:** All installed and verified ✅

### Integration Layer
- **HTTPx:** Async HTTP client for n8n webhook calls
- **n8n:** Chat interface + RAG tools (converted to webhooks)

## 📁 Project Structure

```
agentic_rag/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/                 # PydanticAI agents
│   │   ├── requirements_agent.py
│   │   └── workflow_generator_agent.py
│   ├── orchestration/          # LangGraph orchestration
│   │   └── agent_graph.py
│   ├── services/               # External integrations
│   │   ├── claude_service.py
│   │   ├── rag_service.py      # n8n RAG tools integration
│   │   └── langsmith_service.py
│   ├── api/                    # FastAPI routes and models
│   └── config/                 # Configuration management
├── tests/                      # Test suite
├── scripts/                    # Development utilities
├── docs/
│   ├── links_and_resources.md  # External documentation
│   └── session_logs/           # Development session logs
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
├── project_overview.md         # This file
└── README.md
```

## 🔧 Development Environment

### Current Status ✅
- **Conda environment** `axiom8` active with Python 3.11.13
- **All dependencies installed:**
  - FastAPI 0.115.14
  - Anthropic 0.55.0  
  - LangGraph 0.5.0
  - HTTPx 0.28.1
  - PydanticAI components
  - All supporting libraries

### Configuration Needed
- **Anthropic API Key:** [TO BE CONFIGURED]
- **n8n Webhook URLs:** [TO BE CONFIGURED] 
- **LangSmith Integration:** [TO BE CONFIGURED]

## 🔄 Integration Requirements

### n8n Side Changes
1. **Convert RAG tools** from subworkflow triggers to webhook triggers
2. **Update main workflow** to use HTTP Request node instead of LangChain Code node
3. **Configure webhook authentication** (method TBD)

### Python Agent Integration
- **Receive requests** from n8n Chat Node via HTTP
- **Call RAG tools** via n8n webhooks when needed
- **Return structured responses** back to n8n for user display
- **Maintain session state** during conversation

### LangSmith Integration
- **Monitor agent interactions** and decision-making
- **Track tool usage** and performance
- **Log workflow generation** process for debugging

## 🎯 Success Criteria

### Primary Goals
1. **Generate production-ready n8n workflows** from user descriptions
2. **Iterative refinement** based on user feedback
3. **Maintain chat interface** usability from current n8n implementation
4. **Leverage all Claude Opus 4 capabilities** (thinking, caching, built-in tools)

### Technical Goals  
- **Seamless integration** with existing n8n RAG tools
- **Fast response times** with efficient caching
- **Robust error handling** and user guidance
- **Comprehensive monitoring** via LangSmith

### Future Considerations
- **Migration path to Kestra** for more advanced orchestration
- **Custom chat interface** to replace n8n Chat Node
- **Additional workflow optimization** features

---

## 📝 Implementation Notes

This document provides the **initial context** for building Axiom8. The implementation approach, specific architectures, and detailed configurations should be determined by the development agent based on:

- **PydanticAI best practices** for agent design
- **LangGraph patterns** for multi-agent orchestration  
- **FastAPI conventions** for API design
- **n8n integration requirements** for seamless tool usage

**Next Phase:** Development agent will create the initial implementation plan and begin building the core components.

---

**This is the foundational context document. Future iterations will include session logs with decisions made, changes implemented, and lessons learned.**