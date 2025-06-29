"""
Unified Multi-agent system with single hierarchical LangSmith trace.

This module implements a clean tracing architecture with:
- Single root trace per conversation session
- Proper parent-child trace hierarchy
- No competing trace contexts
- Clear visibility into all agent and tool operations
"""

from typing import Literal, Union, Dict, Any, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.models.openai import OpenAIModel  
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider

from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable
from loguru import logger

from ..config.settings import get_settings
from .tools import all_tools

settings = get_settings()


class RequirementsState(BaseModel):
    """Structured requirements extracted by the Requirements Analyst."""
    user_query: str = Field(description="Original user request")
    workflow_purpose: str = Field(description="What the workflow should accomplish")
    trigger_type: str = Field(description="How the workflow should be triggered")
    required_nodes: List[str] = Field(description="List of n8n nodes that will be needed")
    data_flow: List[str] = Field(description="Description of how data flows through the workflow")
    clarifying_questions: List[str] = Field(default=[], description="Any questions that need clarification")
    is_complete: bool = Field(description="Whether requirements are complete enough to build workflow")


class MultiAgentState(MessagesState):
    """Extended state for multi-agent conversation flow."""
    step: str = "analyze_requirements"  # analyze_requirements | generate_workflow | complete
    requirements: Union[RequirementsState, None] = None
    final_workflow: Union[str, None] = None
    error_message: Union[str, None] = None


# ============================================================================
# Requirements Analyst Agent (OpenAI o3-mini) - NO AUTOMATIC TRACING
# ============================================================================

requirements_analyst_prompt = """You are an expert n8n workflow requirements analyst.

Your role is to analyze user requests for n8n workflows. You should be HELPFUL and move to workflow generation as soon as you have enough basic information. Don't over-analyze or ask too many questions.

## Your Response Format:
If the request has a CLEAR PURPOSE and BASIC APPROACH, respond with:
"COMPLETE: [brief summary of what the workflow should do]"

If the request is VAGUE or missing core information, respond with:
"QUESTIONS: [list 1-2 essential questions only]"

## What Makes a Request Complete (be generous):
- Clear purpose/goal (what they want to achieve)
- Some indication of trigger/schedule OR we can make reasonable assumptions
- Basic idea of integrations needed OR user mentions specific services
- User has provided multiple details showing they understand what they want

## Key Principles:
- PREFER building over questioning when in doubt
- If user mentions specific services/APIs, that's usually enough
- If user provides scheduling details, that shows clear intent
- If user says "make your best judgment" or similar, move to COMPLETE
- Don't ask about technical implementation details (let the workflow generator handle that)

## Examples:
User: "I want to monitor Twitter for mentions and send them to Slack"
Response: "QUESTIONS: 1. What keywords should we monitor? 2. Which Slack channel?"

User: "Monitor Twitter for mentions of my company TechCorp and send alerts to #social-media channel"
Response: "COMPLETE: Monitor Twitter for TechCorp mentions and send alerts to #social-media Slack channel"

User: "I want to get WhatsApp messages from important contacts, summarize them with AI, and email me at 7 AM"
Response: "COMPLETE: Collect WhatsApp messages from important contacts daily, use AI to create a summary, and email the summary at 7 AM"

User: "I need help with automation"
Response: "QUESTIONS: 1. What specific task do you want to automate? 2. What systems or services are involved?"

## Special Rule:
If this is the 3rd+ exchange in a conversation and the user has provided substantial details, you MUST respond with "COMPLETE" even if some details are missing. The workflow generator can handle missing details better than endless questions.

Analyze the user's request and respond accordingly."""

# Create OpenAI model for Requirements Analyst
openai_provider = OpenAIProvider(api_key=settings.openai_api_key.get_secret_value())
openai_model = OpenAIModel(
    settings.openai_model,
    provider=openai_provider,
)

requirements_analyst = PydanticAgent(
    model=openai_model,
    system_prompt=requirements_analyst_prompt,
    output_type=str,
)


# ============================================================================
# Workflow Generator Agent (Claude Sonnet) - NO AUTOMATIC TRACING
# ============================================================================

workflow_generator_prompt = """You are an expert n8n workflow developer.

Your task is to generate complete, production-ready n8n workflows in JSON format based on the user's requirements.

## Your Process:
1. **Use RAG tools** to search for relevant n8n documentation and examples
2. **Design the workflow** with proper node configuration and connections
3. **Generate complete JSON** that can be directly imported into n8n

## RAG Tool Priority:
1. **n8n_workflows_search** - Find real workflow examples (HIGHEST PRIORITY)
2. **n8n_nodes_search** - Get specific node documentation
3. **n8n_documentation_search** - Find general concepts and patterns

## Output Requirements:
- Respond ONLY with the complete n8n workflow JSON object
- Do not include any explanation or additional text
- The JSON should be valid and importable into n8n
- Include proper node configurations, connections, and settings

Generate the workflow now."""

# Create Anthropic model for Workflow Generator
anthropic_provider = AnthropicProvider(api_key=settings.anthropic_api_key.get_secret_value())
anthropic_model = AnthropicModel(
    settings.anthropic_model,
    provider=anthropic_provider,
)

workflow_generator = PydanticAgent(
    model=anthropic_model,
    system_prompt=workflow_generator_prompt,
    tools=all_tools,  # Include RAG tools for n8n documentation
    output_type=str,  # Will output JSON workflow
)


# ============================================================================
# LangGraph Multi-Agent Orchestration - NO ADDITIONAL TRACING
# ============================================================================

async def requirements_analyst_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Requirements Analyst node - relies on parent trace context.
    """
    import time
    start_time = time.time()
    
    messages = state["messages"]
    if not messages:
        return {"error_message": "No messages to analyze", "step": "complete"}
    
    # Count conversation exchanges (user messages)
    user_message_count = len([msg for msg in messages if isinstance(msg, HumanMessage)])
    
    # Get the latest user message
    user_message = messages[-1]
    user_query = user_message.content if hasattr(user_message, 'content') else str(user_message)
    
    # Create enhanced context for the analyst
    conversation_context = f"""
Current conversation exchange: {user_message_count}
Latest user message: {user_query}

Previous conversation context:
"""
    
    # Add conversation history for context
    for i, msg in enumerate(messages[:-1]):  # Exclude the latest message
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        conversation_context += f"{role}: {content}\n"
    
    conversation_context += f"\nRemember: If this is exchange 3+ and user has provided substantial details, respond with COMPLETE."
    
    try:
        # Run the requirements analyst with full conversation context
        response = await requirements_analyst.run(conversation_context)
        analysis_result = response.output
        execution_time = time.time() - start_time
        
        logger.info(f"Requirements analyst (exchange {user_message_count}) completed in {execution_time:.2f}s: {analysis_result[:100]}...")
        
        # Add the analyst's response to messages
        ai_message = AIMessage(content=analysis_result)
        
        # Force completion after 4+ exchanges to prevent infinite loops
        if user_message_count >= 4 and not analysis_result.startswith("COMPLETE:"):
            logger.warning(f"Forcing completion after {user_message_count} exchanges to prevent infinite loop")
            forced_completion = f"COMPLETE: Create a workflow based on user requirements from the conversation (automatically proceeding after multiple exchanges)"
            ai_message = AIMessage(content=forced_completion)
            analysis_result = forced_completion
        
        # Determine next step based on response
        if analysis_result.startswith("COMPLETE:"):
            # Requirements are complete, move to workflow generation
            workflow_purpose = analysis_result.replace("COMPLETE:", "").strip()
            
            # If it's a forced completion, use a more comprehensive summary
            if user_message_count >= 4:
                # Extract key details from conversation for better workflow generation
                workflow_purpose = f"Workflow based on user conversation: {user_query}"
            
            return {
                "messages": [ai_message],
                "step": "generate_workflow",
                "requirements": RequirementsState(
                    user_query=user_query,
                    workflow_purpose=workflow_purpose,
                    trigger_type="schedule",  # Better default for most workflows
                    required_nodes=["Schedule Trigger", "HTTP Request"],  # Better defaults
                    data_flow=["Trigger -> Process -> Output"],  # Better default
                    is_complete=True
                )
            }
        else:
            # Requirements need clarification, keep in analysis phase
            return {
                "messages": [ai_message],
                "step": "analyze_requirements"  # Stay in current step for user response
            }
            
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error in requirements analysis: {str(e)}"
        logger.error(f"Requirements analyst error after {execution_time:.2f}s: {str(e)}")
            
        ai_message = AIMessage(content=error_msg)
        return {
            "messages": [ai_message],
            "step": "complete",
            "error_message": error_msg
        }


async def workflow_generator_node(state: MultiAgentState) -> Dict[str, Any]:
    """
    Workflow Generator node - relies on parent trace context.
    """
    import time
    start_time = time.time()
    
    requirements = state.get("requirements")
    
    if not requirements or not requirements.is_complete:
        error_msg = "No complete requirements available for workflow generation."
        ai_message = AIMessage(content=error_msg)
        return {
            "messages": [ai_message],
            "step": "complete",
            "error_message": error_msg
        }
    
    # Get conversation history for better context
    messages = state.get("messages", [])
    conversation_history = ""
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        conversation_history += f"{role}: {msg.content}\n"
    
    # Create a comprehensive prompt for the workflow generator
    workflow_prompt = f"""
    Generate a complete n8n workflow based on this conversation with the user:
    
    === CONVERSATION HISTORY ===
    {conversation_history}
    
    === REQUIREMENTS SUMMARY ===
    Purpose: {requirements.workflow_purpose}
    Original request: {requirements.user_query}
    
    === INSTRUCTIONS ===
    1. Use the RAG tools to find relevant examples and documentation
    2. Analyze the FULL conversation to understand all user requirements
    3. Make reasonable assumptions for any missing technical details
    4. Create a production-ready workflow that addresses all user needs
    5. Output ONLY the complete n8n workflow JSON
    
    Generate the workflow now.
    """
    
    try:
        # Run the workflow generator (inherits trace context, including tool calls)
        response = await workflow_generator.run(workflow_prompt)
        workflow_json = response.output
        execution_time = time.time() - start_time
        
        logger.info(f"Workflow generator completed in {execution_time:.2f}s, JSON length: {len(workflow_json)}")
        
        ai_message = AIMessage(content=f"Here's your complete n8n workflow:\n\n```json\n{workflow_json}\n```")
        
        return {
            "messages": [ai_message],
            "step": "complete",
            "final_workflow": workflow_json
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error generating workflow: {str(e)}"
        logger.error(f"Workflow generator error after {execution_time:.2f}s: {str(e)}")
            
        ai_message = AIMessage(content=error_msg)
        return {
            "messages": [ai_message],
            "step": "complete",
            "error_message": error_msg
        }


def route_next_step(state: MultiAgentState) -> Literal["workflow_generator", "__end__"]:
    """
    Router function to determine the next step based on current state.
    """
    current_step = state.get("step", "analyze_requirements")
    
    if current_step == "generate_workflow":
        return "workflow_generator"
    else:  # current_step == "complete"
        return "__end__"


# ============================================================================
# Build the LangGraph - NO ADDITIONAL TRACING
# ============================================================================

def create_multi_agent_graph():
    """Create and compile the multi-agent LangGraph."""
    
    # Build the graph
    graph_builder = StateGraph(MultiAgentState)
    
    # Add nodes
    graph_builder.add_node("requirements_analyst", requirements_analyst_node)
    graph_builder.add_node("workflow_generator", workflow_generator_node)
    
    # Add edge from start to requirements analyst
    graph_builder.add_edge(START, "requirements_analyst")
    
    # Add conditional edges from requirements analyst
    graph_builder.add_conditional_edges(
        "requirements_analyst",
        route_next_step,
        {
            "workflow_generator": "workflow_generator",
            "__end__": END
        }
    )
    
    # Add edge from workflow generator to end
    graph_builder.add_edge("workflow_generator", END)
    
    # Compile and return
    return graph_builder.compile()


# Create the compiled graph instance
multi_agent_graph = create_multi_agent_graph()


# ============================================================================
# SINGLE ROOT TRACE - Main Execution Function
# ============================================================================

@traceable(name="multi_agent_conversation_session")
async def execute_unified_multi_agent_workflow(
    initial_state: MultiAgentState, 
    session_id: str = None,
    conversation_type: str = "start"
) -> Dict[str, Any]:
    """
    Execute the multi-agent workflow with SINGLE unified tracing.
    
    This creates ONE root trace that contains the entire conversation flow:
    - Session metadata and timing
    - Requirements analyst execution (automatically traced as child)
    - Workflow generator execution (automatically traced as child)
    - All tool calls (automatically traced as grandchildren)
    - Final results and statistics
    
    Everything inherits the trace context from this single root trace.
    """
    import time
    session_start_time = time.time()
    
    # Extract initial query for logging
    initial_query = None
    if initial_state.get("messages"):
        initial_query = initial_state["messages"][-1].content
    
    logger.info(f"Starting multi-agent session {session_id} ({conversation_type}): {initial_query}")
    
    try:
        # Execute the graph - all operations inherit this trace context
        result = await multi_agent_graph.ainvoke(initial_state)
        
        session_duration = time.time() - session_start_time
        
        # Calculate comprehensive session statistics
        final_step = result.get("step", "unknown")
        conversation_complete = final_step == "complete"
        message_count = len(result.get("messages", []))
        has_error = result.get("error_message") is not None
        requirements_generated = result.get("requirements") is not None
        workflow_generated = result.get("final_workflow") is not None
        
        # Log session completion with full metadata
        logger.info(
            f"Session {session_id} completed in {session_duration:.2f}s: "
            f"step={final_step}, messages={message_count}, "
            f"requirements={requirements_generated}, workflow={workflow_generated}, "
            f"error={has_error}"
        )
        
        return result
        
    except Exception as e:
        session_duration = time.time() - session_start_time
        error_result = {
            "messages": [AIMessage(content=f"Session error: {str(e)}")],
            "step": "complete",
            "error_message": str(e)
        }
        
        logger.error(f"Multi-agent session error for {session_id} after {session_duration:.2f}s: {str(e)}")
        return error_result