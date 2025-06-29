#!/usr/bin/env python3
"""
Interactive chat script for testing the multi-agent n8n workflow generator.

This script provides a conversational interface to test the multi-agent system
as a real user would interact with it.
"""

import requests
import json
import sys
from typing import Optional

class Colors:
    """ANSI color codes for pretty terminal output."""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MultiAgentChat:
    """Interactive chat client for the multi-agent system."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.conversation_complete = False
        
    def print_banner(self):
        """Print welcome banner."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
        print("🤖 Axiom8 Multi-Agent n8n Workflow Generator")
        print("   Two-Agent System: Requirements Analyst + Workflow Builder")
        print(f"{'='*70}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}💡 How it works:{Colors.END}")
        print(f"   1. {Colors.GREEN}Requirements Analyst{Colors.END} (OpenAI o3-mini) - Analyzes your request")
        print(f"   2. {Colors.BLUE}Workflow Generator{Colors.END} (Claude Sonnet) - Builds the n8n workflow")
        print(f"   3. {Colors.WHITE}Conversational{Colors.END} - Ask follow-up questions until complete\n")
        
        print(f"{Colors.YELLOW}Commands:{Colors.END}")
        print(f"   {Colors.CYAN}/help{Colors.END}     - Show this help")
        print(f"   {Colors.CYAN}/history{Colors.END}  - Show conversation history") 
        print(f"   {Colors.CYAN}/new{Colors.END}      - Start a new conversation")
        print(f"   {Colors.CYAN}/quit{Colors.END}     - Exit the chat")
        print(f"   {Colors.CYAN}/status{Colors.END}   - Show current session status\n")
        
    def check_health(self) -> bool:
        """Check if the server is running."""
        try:
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def start_conversation(self, query: str) -> bool:
        """Start a new conversation with the multi-agent system."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/start",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            self.session_id = data["session_id"]
            self.conversation_complete = data.get("conversation_complete", False)
            
            # Print agent response
            message = data["message"]
            current_agent = data.get("current_agent", "unknown")
            metadata = data.get("metadata", {})
            
            self._print_agent_response(message, current_agent, metadata)
            
            return True
            
        except requests.RequestException as e:
            print(f"{Colors.RED}❌ Error starting conversation: {e}{Colors.END}")
            return False
    
    def continue_conversation(self, message: str) -> bool:
        """Continue the conversation with additional input."""
        if not self.session_id:
            print(f"{Colors.RED}❌ No active session. Start a new conversation first.{Colors.END}")
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/chat/continue",
                json={"session_id": self.session_id, "message": message},
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout for workflow generation
            )
            response.raise_for_status()
            
            data = response.json()
            self.conversation_complete = data.get("conversation_complete", False)
            
            # Print agent response
            message_data = data["message"]
            current_agent = data.get("current_agent", "unknown")
            metadata = data.get("metadata", {})
            
            self._print_agent_response(message_data, current_agent, metadata)
            
            return True
            
        except requests.RequestException as e:
            print(f"{Colors.RED}❌ Error continuing conversation: {e}{Colors.END}")
            return False
    
    def get_history(self) -> bool:
        """Get and display conversation history."""
        if not self.session_id:
            print(f"{Colors.RED}❌ No active session.{Colors.END}")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/chat/{self.session_id}/history",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            messages = data.get("messages", [])
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}📋 Conversation History ({len(messages)} messages):{Colors.END}")
            print(f"{Colors.CYAN}Session ID: {self.session_id}{Colors.END}\n")
            
            for i, msg in enumerate(messages, 1):
                role_color = Colors.GREEN if msg["role"] == "user" else Colors.BLUE
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                
                print(f"{role_color}{Colors.BOLD}{i}. {role_icon} {msg['role'].title()}:{Colors.END}")
                print(f"   {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}\n")
            
            return True
            
        except requests.RequestException as e:
            print(f"{Colors.RED}❌ Error getting history: {e}{Colors.END}")
            return False
    
    def _print_agent_response(self, message_data: dict, current_agent: str, metadata: dict):
        """Print formatted agent response."""
        content = message_data.get("content", "")
        
        # Determine which agent is responding
        if current_agent == "analyze_requirements":
            agent_name = "Requirements Analyst"
            agent_icon = "🔍"
            agent_color = Colors.GREEN
            model_info = "(OpenAI o3-mini)"
        elif current_agent == "complete":
            agent_name = "Workflow Generator" 
            agent_icon = "⚙️"
            agent_color = Colors.BLUE
            model_info = "(Claude Sonnet)"
        else:
            agent_name = "System"
            agent_icon = "🤖"
            agent_color = Colors.WHITE
            model_info = ""
        
        # Print agent header
        print(f"\n{agent_color}{Colors.BOLD}{agent_icon} {agent_name} {model_info}:{Colors.END}")
        
        # Print metadata if interesting
        if metadata:
            req_complete = metadata.get("requirements_complete", False)
            workflow_generated = metadata.get("workflow_generated", False)
            
            status_parts = []
            if req_complete:
                status_parts.append(f"{Colors.GREEN}✅ Requirements Complete{Colors.END}")
            if workflow_generated:
                status_parts.append(f"{Colors.BLUE}✅ Workflow Generated{Colors.END}")
            
            if status_parts:
                print(f"   Status: {' | '.join(status_parts)}")
        
        # Print the actual message
        print(f"{Colors.WHITE}{content}{Colors.END}")
        
        # Show completion status
        if self.conversation_complete:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Conversation Complete!{Colors.END}")
            print(f"{Colors.YELLOW}💡 You can start a new conversation with /new{Colors.END}")
    
    def show_status(self):
        """Show current session status."""
        if not self.session_id:
            print(f"{Colors.YELLOW}📊 Status: No active session{Colors.END}")
        else:
            status = "Complete" if self.conversation_complete else "In Progress"
            status_color = Colors.GREEN if self.conversation_complete else Colors.YELLOW
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}📊 Current Session Status:{Colors.END}")
            print(f"   Session ID: {Colors.WHITE}{self.session_id}{Colors.END}")
            print(f"   Status: {status_color}{status}{Colors.END}")
            print(f"   Server: {Colors.WHITE}{self.base_url}{Colors.END}\n")
    
    def run(self):
        """Run the interactive chat loop."""
        self.print_banner()
        
        # Check if server is running
        if not self.check_health():
            print(f"{Colors.RED}❌ Server not running at {self.base_url.replace('/api/v1', '')}")
            print(f"Please start the server with: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000{Colors.END}")
            return
        
        print(f"{Colors.GREEN}✅ Server is running and ready!{Colors.END}")
        print(f"\n{Colors.BOLD}Start by describing the n8n workflow you want to create:{Colors.END}")
        
        while True:
            try:
                # Get user input
                if self.session_id and not self.conversation_complete:
                    prompt = f"{Colors.CYAN}💬 Continue:{Colors.END} "
                else:
                    prompt = f"{Colors.CYAN}🚀 Your request:{Colors.END} "
                
                user_input = input(prompt).strip()
                
                # Handle commands
                if user_input.lower() in ['/quit', '/exit', '/q']:
                    print(f"\n{Colors.YELLOW}👋 Thanks for using Axiom8 Multi-Agent System!{Colors.END}")
                    break
                elif user_input.lower() == '/help':
                    self.print_banner()
                    continue
                elif user_input.lower() == '/new':
                    self.session_id = None
                    self.conversation_complete = False
                    print(f"{Colors.GREEN}🆕 Started new conversation session{Colors.END}")
                    continue
                elif user_input.lower() == '/history':
                    self.get_history()
                    continue
                elif user_input.lower() == '/status':
                    self.show_status()
                    continue
                elif not user_input:
                    continue
                
                # Process user message
                if not self.session_id or self.conversation_complete:
                    # Start new conversation
                    print(f"\n{Colors.YELLOW}🔄 Starting new conversation...{Colors.END}")
                    if self.start_conversation(user_input):
                        if self.conversation_complete:
                            self.session_id = None  # Reset for next conversation
                else:
                    # Continue existing conversation
                    print(f"\n{Colors.YELLOW}🔄 Processing your message...{Colors.END}")
                    if self.continue_conversation(user_input):
                        if self.conversation_complete:
                            self.session_id = None  # Reset for next conversation
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")

def main():
    """Main entry point."""
    chat = MultiAgentChat()
    chat.run()

if __name__ == "__main__":
    main()