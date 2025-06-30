#!/usr/bin/env python3
"""
Comprehensive Testing Script for Axiom8 Multi-Agent System

This script performs extensive testing of all components:
1. Environment and configuration verification
2. Tool connectivity and response testing  
3. Individual agent testing
4. Multi-agent orchestration testing
5. API endpoint testing
6. Performance and logging verification
"""

import asyncio
import httpx
import json
import time
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from app.config.settings import get_settings
from app.agent.tools import all_tools, n8n_core_search, n8n_management_search, n8n_integrations_search, n8n_workflows_search
from app.agent.multi_agent_unified_tracing import execute_unified_multi_agent_workflow, MultiAgentState
from langchain_core.messages import HumanMessage

# Configure comprehensive logging
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO")

class ComprehensiveTest:
    def __init__(self):
        self.settings = get_settings()
        self.test_results = {
            "configuration": False,
            "tool_connectivity": {},
            "agent_functionality": {},
            "api_endpoints": {},
            "performance": {},
            "errors": []
        }
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🚀 STARTING COMPREHENSIVE AXIOM8 TEST SUITE")
        
        # Test 1: Configuration Verification
        await self.test_configuration()
        
        # Test 2: Tool Connectivity
        await self.test_tool_connectivity()
        
        # Test 3: Agent Functionality  
        await self.test_agent_functionality()
        
        # Test 4: Multi-Agent Orchestration
        await self.test_multi_agent_orchestration()
        
        # Test 5: API Endpoints (if server is running)
        await self.test_api_endpoints()
        
        # Final Results
        self.print_test_summary()
    
    async def test_configuration(self):
        """Test environment configuration and settings"""
        logger.info("📋 TESTING CONFIGURATION")
        
        try:
            # Test required settings
            required_settings = [
                ('anthropic_api_key', self.settings.anthropic_api_key.get_secret_value()),
                ('openai_api_key', self.settings.openai_api_key.get_secret_value()),
                ('n8n_core_search_url', self.settings.n8n_core_search_url),
                ('n8n_management_search_url', self.settings.n8n_management_search_url),
                ('n8n_integrations_search_url', self.settings.n8n_integrations_search_url),
                ('n8n_workflows_search_url', self.settings.n8n_workflows_search_url),
            ]
            
            for setting_name, setting_value in required_settings:
                if setting_value and len(str(setting_value)) > 10:
                    logger.success(f"✅ {setting_name}: Configured")
                else:
                    logger.error(f"❌ {setting_name}: Missing or invalid")
                    self.test_results["errors"].append(f"Missing {setting_name}")
            
            # Test optional settings
            optional_settings = [
                ('langchain_api_key', self.settings.langchain_api_key),
                ('langchain_project', self.settings.langchain_project),
            ]
            
            for setting_name, setting_value in optional_settings:
                if setting_value:
                    logger.info(f"📝 {setting_name}: Configured")
                else:
                    logger.warning(f"⚠️  {setting_name}: Not configured (optional)")
            
            self.test_results["configuration"] = True
            logger.success("✅ CONFIGURATION TEST PASSED")
            
        except Exception as e:
            logger.error(f"❌ CONFIGURATION TEST FAILED: {e}")
            self.test_results["errors"].append(f"Configuration error: {e}")
    
    async def test_tool_connectivity(self):
        """Test connectivity to all n8n RAG tools"""
        logger.info("🔧 TESTING TOOL CONNECTIVITY")
        
        tools_to_test = [
            ("n8n_core_search", n8n_core_search),
            ("n8n_management_search", n8n_management_search), 
            ("n8n_integrations_search", n8n_integrations_search),
            ("n8n_workflows_search", n8n_workflows_search),
        ]
        
        for tool_name, tool_function in tools_to_test:
            try:
                logger.info(f"🔧 Testing {tool_name}...")
                start_time = time.time()
                
                # Test with a simple query
                result = await tool_function("test query")
                
                execution_time = time.time() - start_time
                
                if "error" in result:
                    logger.error(f"❌ {tool_name} FAILED: {result['error']}")
                    self.test_results["tool_connectivity"][tool_name] = {
                        "status": "failed",
                        "error": result["error"],
                        "time": execution_time
                    }
                else:
                    logger.success(f"✅ {tool_name} SUCCESS: {execution_time:.2f}s")
                    self.test_results["tool_connectivity"][tool_name] = {
                        "status": "success",
                        "time": execution_time,
                        "response_size": len(str(result))
                    }
                    
            except Exception as e:
                logger.error(f"❌ {tool_name} EXCEPTION: {e}")
                self.test_results["tool_connectivity"][tool_name] = {
                    "status": "exception",
                    "error": str(e)
                }
    
    async def test_agent_functionality(self):
        """Test individual agent functionality"""
        logger.info("🤖 TESTING AGENT FUNCTIONALITY")
        
        # Import agents
        try:
            from app.agent.multi_agent_unified_tracing import requirements_analyst, workflow_generator
            
            # Test Requirements Analyst
            logger.info("🤖 Testing Requirements Analyst...")
            start_time = time.time()
            
            try:
                response = await requirements_analyst.run("I want to create a simple test workflow")
                analyst_time = time.time() - start_time
                
                logger.success(f"✅ Requirements Analyst: {analyst_time:.2f}s | Response: {response.output[:100]}...")
                self.test_results["agent_functionality"]["requirements_analyst"] = {
                    "status": "success",
                    "time": analyst_time,
                    "response_length": len(response.output)
                }
            except Exception as e:
                logger.error(f"❌ Requirements Analyst FAILED: {e}")
                self.test_results["agent_functionality"]["requirements_analyst"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test Workflow Generator
            logger.info("🎨 Testing Workflow Generator...")
            start_time = time.time()
            
            try:
                test_prompt = "Create a simple n8n workflow that receives a webhook and sends an email notification."
                response = await workflow_generator.run(test_prompt)
                generator_time = time.time() - start_time
                
                logger.success(f"✅ Workflow Generator: {generator_time:.2f}s | JSON length: {len(response.output)}")
                self.test_results["agent_functionality"]["workflow_generator"] = {
                    "status": "success", 
                    "time": generator_time,
                    "output_length": len(response.output)
                }
            except Exception as e:
                logger.error(f"❌ Workflow Generator FAILED: {e}")
                self.test_results["agent_functionality"]["workflow_generator"] = {
                    "status": "failed",
                    "error": str(e)
                }
                
        except Exception as e:
            logger.error(f"❌ AGENT IMPORT FAILED: {e}")
            self.test_results["errors"].append(f"Agent import error: {e}")
    
    async def test_multi_agent_orchestration(self):
        """Test the complete multi-agent orchestration"""
        logger.info("🎭 TESTING MULTI-AGENT ORCHESTRATION")
        
        test_cases = [
            {
                "name": "Simple Requirements",
                "query": "Create a workflow that monitors a Google Sheet for new rows and sends Slack notifications",
                "expected_completion": True
            },
            {
                "name": "Vague Requirements", 
                "query": "I need help with automation",
                "expected_completion": False
            },
            {
                "name": "Complex Requirements",
                "query": "Build a workflow that connects to multiple APIs, processes data with AI, and sends results to various channels based on conditions",
                "expected_completion": True
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"🎭 Testing: {test_case['name']}")
            
            try:
                start_time = time.time()
                
                # Create initial state
                initial_state = MultiAgentState(
                    messages=[HumanMessage(content=test_case["query"])],
                    step="analyze_requirements",
                    requirements=None,
                    final_workflow=None,
                    error_message=None
                )
                
                # Execute multi-agent workflow
                result = await execute_unified_multi_agent_workflow(
                    initial_state, 
                    session_id=f"test_{test_case['name'].lower().replace(' ', '_')}",
                    conversation_type="test"
                )
                
                execution_time = time.time() - start_time
                
                # Analyze results
                conversation_complete = result.get("step") == "complete"
                has_workflow = result.get("final_workflow") is not None
                has_error = result.get("error_message") is not None
                
                logger.success(f"✅ {test_case['name']}: {execution_time:.2f}s | Complete: {conversation_complete} | Workflow: {has_workflow} | Error: {has_error}")
                
                self.test_results["agent_functionality"][f"orchestration_{test_case['name'].lower().replace(' ', '_')}"] = {
                    "status": "success",
                    "time": execution_time,
                    "conversation_complete": conversation_complete,
                    "has_workflow": has_workflow,
                    "has_error": has_error,
                    "message_count": len(result.get("messages", []))
                }
                
            except Exception as e:
                logger.error(f"❌ {test_case['name']} FAILED: {e}")
                self.test_results["agent_functionality"][f"orchestration_{test_case['name'].lower().replace(' ', '_')}"] = {
                    "status": "failed",
                    "error": str(e)
                }
    
    async def test_api_endpoints(self):
        """Test API endpoints if server is running"""
        logger.info("🌐 TESTING API ENDPOINTS")
        
        base_url = "http://127.0.0.1:8000"
        
        try:
            async with httpx.AsyncClient() as client:
                # Test health endpoint
                response = await client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.success("✅ Health endpoint working")
                    self.test_results["api_endpoints"]["health"] = {"status": "success"}
                    
                    # Test chat/start endpoint
                    start_time = time.time()
                    chat_response = await client.post(
                        f"{base_url}/api/v1/chat/start",
                        json={"query": "Create a simple test workflow"},
                        timeout=30.0
                    )
                    api_time = time.time() - start_time
                    
                    if chat_response.status_code == 200:
                        logger.success(f"✅ Chat/start endpoint: {api_time:.2f}s")
                        self.test_results["api_endpoints"]["chat_start"] = {
                            "status": "success",
                            "time": api_time,
                            "response_size": len(chat_response.text)
                        }
                    else:
                        logger.error(f"❌ Chat/start endpoint failed: {chat_response.status_code}")
                        self.test_results["api_endpoints"]["chat_start"] = {
                            "status": "failed",
                            "status_code": chat_response.status_code
                        }
                        
                else:
                    logger.error(f"❌ Health endpoint failed: {response.status_code}")
                    self.test_results["api_endpoints"]["health"] = {
                        "status": "failed", 
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            logger.warning(f"⚠️  API endpoints not accessible (server not running?): {e}")
            self.test_results["api_endpoints"]["error"] = str(e)
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        
        # Configuration
        config_status = "✅ PASS" if self.test_results["configuration"] else "❌ FAIL"
        logger.info(f"Configuration: {config_status}")
        
        # Tool Connectivity
        tool_results = self.test_results["tool_connectivity"]
        successful_tools = len([t for t in tool_results.values() if t.get("status") == "success"])
        total_tools = len(tool_results)
        logger.info(f"Tool Connectivity: {successful_tools}/{total_tools} tools working")
        
        for tool_name, result in tool_results.items():
            status_emoji = "✅" if result.get("status") == "success" else "❌"
            time_info = f" ({result.get('time', 0):.2f}s)" if result.get("time") else ""
            logger.info(f"  {status_emoji} {tool_name}{time_info}")
        
        # Agent Functionality
        agent_results = self.test_results["agent_functionality"]
        successful_agents = len([a for a in agent_results.values() if a.get("status") == "success"])
        total_agents = len(agent_results)
        logger.info(f"Agent Functionality: {successful_agents}/{total_agents} tests passed")
        
        for agent_name, result in agent_results.items():
            status_emoji = "✅" if result.get("status") == "success" else "❌"
            time_info = f" ({result.get('time', 0):.2f}s)" if result.get("time") else ""
            logger.info(f"  {status_emoji} {agent_name}{time_info}")
        
        # API Endpoints
        api_results = self.test_results["api_endpoints"]
        if api_results:
            logger.info("API Endpoints:")
            for endpoint_name, result in api_results.items():
                if endpoint_name != "error":
                    status_emoji = "✅" if result.get("status") == "success" else "❌"
                    time_info = f" ({result.get('time', 0):.2f}s)" if result.get("time") else ""
                    logger.info(f"  {status_emoji} {endpoint_name}{time_info}")
        
        # Errors
        if self.test_results["errors"]:
            logger.error("Errors encountered:")
            for error in self.test_results["errors"]:
                logger.error(f"  ❌ {error}")
        
        # Overall Status
        total_tests = len(tool_results) + len(agent_results) + len(api_results)
        api_successes = len([a for a in api_results.values() if isinstance(a, dict) and a.get("status") == "success"])
        total_passed = successful_tools + successful_agents + api_successes
        
        if total_passed == total_tests and self.test_results["configuration"] and not self.test_results["errors"]:
            logger.success("🎉 ALL TESTS PASSED - AXIOM8 IS FULLY FUNCTIONAL!")
        else:
            logger.warning(f"⚠️  {total_passed}/{total_tests} tests passed - Some issues detected")
        
        logger.info("=" * 80)


async def main():
    """Run comprehensive tests"""
    tester = ComprehensiveTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())