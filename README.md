# Axiom8 - Agentic RAG System for n8n Workflows

**Axiom8** is an intelligent agentic system that automatically generates production-ready n8n workflows from natural language descriptions. Transform your workflow ideas into complete, importable n8n JSON files through conversational AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Anaconda/Miniconda
- API keys for OpenAI and Anthropic

### Installation
```bash
# Clone the repository
git clone https://github.com/alexandre-axioma/Axiom8.git
cd Axiom8

# Create and activate conda environment
conda create -n axiom8 python=3.11.13
conda activate axiom8

# Install dependencies
cd agentic_rag
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit with your API keys
```

### Environment Variables
Required in `/agentic_rag/.env`:
```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key_here
N8N_DOCUMENTATION_SEARCH_URL=your_n8n_webhook_url
N8N_NODES_SEARCH_URL=your_n8n_webhook_url
N8N_WORKFLOWS_SEARCH_URL=your_n8n_webhook_url
N8N_WORKFLOW_SEARCH_URL=your_n8n_webhook_url
```

### Run the Server
```bash
cd agentic_rag
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the API at: `http://127.0.0.1:8000`

## 🏗️ Architecture

### Multi-Agent System
- **Requirements Analyst** (OpenAI o3-mini): Analyzes user requests and asks clarifying questions
- **Workflow Generator** (Claude Opus 4): Creates production-ready n8n workflows using RAG
- **LangGraph Orchestration**: Manages conversation flow and state

### API Endpoints
- `POST /api/v1/chat/start` - Start a new conversation
- `POST /api/v1/chat/continue` - Continue existing conversation
- `GET /api/v1/chat/{session_id}/history` - Get conversation history
- `POST /api/v1/invoke` - Legacy single-shot endpoint

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and run
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### EasyPanel Deployment
The application is designed for EasyPanel deployment:
1. Import the Docker Compose configuration
2. Set environment variables in EasyPanel
3. Deploy alongside your n8n instance
4. Configure n8n to use local API endpoints

## 📝 Usage Examples

### Start a Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/chat/start" \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to monitor Twitter for mentions and send alerts to Slack"}'
```

### Continue Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/chat/continue" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "message": "Monitor for mentions of my company TechCorp"}'
```

## 🔧 Development

### Project Structure
```
agentic_rag/
├── app/
│   ├── agent/           # Multi-agent system
│   ├── api/             # FastAPI routes
│   ├── config/          # Configuration
│   ├── services/        # Business logic
│   └── main.py          # Application entry point
├── scripts/             # Utility scripts
└── requirements.txt     # Dependencies
```

### Testing
```bash
# Interactive testing
cd agentic_rag/scripts
python interactive_chat.py

# Health check
curl http://127.0.0.1:8000/health
```

## 🎯 Integration with n8n

This system integrates with n8n through:
1. **RAG System**: Queries n8n documentation via webhooks
2. **Workflow Output**: Generates importable n8n JSON
3. **API Integration**: n8n can call this service for workflow generation

## 📊 Observability

- **LangSmith Tracing**: Full conversation and tool call tracking
- **Structured Logging**: Detailed execution logs with Loguru
- **Health Monitoring**: Built-in health checks and metrics

## 🚀 Roadmap

- [ ] Web interface for workflow generation
- [ ] Advanced workflow templates
- [ ] User authentication and sessions
- [ ] Workflow version control
- [ ] Advanced RAG improvements

## 📄 License

This project is proprietary software developed by Axioma Digital Solutions.

## 🤝 Contributing

Please read CLAUDE.md for development guidelines and architecture details.