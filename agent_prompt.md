# Axiom8 - Agent Context Prompt

## 🎯 What You're Working On

You are helping to build **Axiom8**, an intelligent agent system that **generates production-ready n8n workflows** from user ideas.

**Core Concept:**
- **Input:** User describes a workflow idea (e.g., "monitor spreadsheet and send email alerts")
- **Output:** Complete, ready-to-use n8n workflow with all nodes and configurations

**Key Points:**
- We have existing RAG tools with n8n documentation and workflow examples
- Currently limited by n8n's AI capabilities - building Python alternative
- Must integrate with existing n8n infrastructure (chat interface + RAG tools)
- Two-agent system: Requirements analysis + Workflow generation

## 🛠️ Available Tools

You have access to powerful **MCP tools** that should be your **first choice** for information gathering:

### Context7 MCP - Documentation Access
- **resolve-library-id**: Convert library names to documentation IDs
- **get-library-docs**: Get comprehensive documentation for libraries
- **Use for:** PydanticAI, LangGraph, Anthropic API, FastAPI documentation
- **How to get specific libary id's:** In the 01_important_links.md file you can find some links for the documentation, but firstly you will find exactly the name to search for each library. This name was hand-picked for each documentation. Always search for this name first using the resolve-library-id tool, that will most likely return the desired documentation id. 

### Brave Search MCP - Web Search  
- **brave_web_search**: Execute web searches with filtering
- **brave_local_search**: Local search with web fallback
- **Use for:** Latest updates, troubleshooting, community solutions

### Supabase MCP - Database Access (Future)
- **Status:** Not yet configured  
- **Future capability:** Direct database operations and RAG tool integration

**Search Strategy:** 
1. 🥇 **Try MCP tools first** (Context7 for docs, Brave for search)
2. 🥈 **Consult project links** only if MCP doesn't provide enough detail

## 📁 Where to Find Information

**All project details are in the `00__project__log/` folder:**

- **`00__project__overview.md`** → Complete project context, current architecture, goals, and technical details
- **`01__links.md`** → Critical documentation links for PydanticAI, LangGraph, Claude API

## 🚨 Important

**Always read the project log folder first** before making any implementation decisions. The specific:
- Architecture details may have evolved
- Technology choices may have changed  
- Implementation approaches may have been refined
- New requirements may have been added

The **core goal** (generating n8n workflows) remains constant, but implementation details evolve during development.

## 🔄 Your Role

1. **Check project log** for current state and decisions
2. **Use MCP tools** as primary information source (Context7 for docs, Brave for search)
3. **Consult documentation links** only when MCP tools are insufficient
4. **Update session logs** with any significant changes or decisions
5. **Maintain focus** on the core goal: production-ready n8n workflow generation

---

**Start by reading `00__project__overview.md` for complete context.**