# EasyPanel Deployment Guide for Axiom8

This comprehensive guide will walk you through deploying the Axiom8 Agentic RAG system on EasyPanel, integrating it with your existing n8n instance.

## 📋 Prerequisites

### Server Requirements
- **VPS with EasyPanel installed**
- **Minimum 2GB RAM** (4GB+ recommended for production)
- **Docker and Docker Swarm** (automatically installed with EasyPanel)
- **Ports 80 and 443 available** for SSL termination
- **Ubuntu 20.04+** or similar Linux distribution

### API Keys Required
- **OpenAI API Key** (for Requirements Analyst - o3-mini model)
- **Anthropic API Key** (for Workflow Generator - Claude Opus 4)
- **LangSmith API Key** (optional, for observability)

### n8n Integration
- **n8n instance running in EasyPanel** (existing)
- **n8n RAG webhook URLs** (4 endpoints for documentation search)

## 🚀 Step 1: Pre-Deployment Setup

### 1.1 Verify EasyPanel Installation
```bash
# SSH into your VPS
ssh user@your-server-ip

# Check EasyPanel status
docker ps | grep easypanel

# Access EasyPanel dashboard
# Navigate to: https://your-server-ip (or your domain)
```

### 1.2 Create Project in EasyPanel
1. **Login to EasyPanel Dashboard**
2. **Create New Project**: Click "+" → "New Project"
3. **Project Name**: `axiom8-production` (or your preferred name)
4. **Description**: `Axiom8 Agentic RAG System for n8n Workflows`

### 1.3 Prepare Environment Variables
Create a secure `.env` file with your API keys:

```env
# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Tracing (Optional but Recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=axiom8-production

# n8n RAG Webhook URLs
N8N_DOCUMENTATION_SEARCH_URL=https://your-n8n-domain.com/webhook/documentation-search
N8N_NODES_SEARCH_URL=https://your-n8n-domain.com/webhook/nodes-search
N8N_WORKFLOWS_SEARCH_URL=https://your-n8n-domain.com/webhook/workflows-search
N8N_WORKFLOW_SEARCH_URL=https://your-n8n-domain.com/webhook/workflow-search

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration
OPENAI_MODEL=o3-mini
ANTHROPIC_MODEL=claude-3-opus-20240229
```

## 🐳 Step 2: Deploy via GitHub Repository

### 2.1 Deploy from GitHub
1. **In EasyPanel Project**: Click "+" → "Service" → "App"
2. **Configuration**:
   - **Name**: `axiom8-api`
   - **Source**: `GitHub`
   - **Repository**: `https://github.com/alexandre-axioma/Axiom8`
   - **Branch**: `main`
   - **Build Path**: `/` (root directory)

### 2.2 Build Configuration
- **Dockerfile**: EasyPanel will automatically detect and use the `Dockerfile`
- **Build Context**: Root directory (`/`)
- **Auto Deploy**: ✅ Enable (for automatic updates on GitHub push)

### 2.3 Environment Variables Setup
In the **Environment** section, add all variables from your `.env` file:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=axiom8-production
N8N_DOCUMENTATION_SEARCH_URL=https://your-n8n-domain.com/webhook/documentation-search
N8N_NODES_SEARCH_URL=https://your-n8n-domain.com/webhook/nodes-search
N8N_WORKFLOWS_SEARCH_URL=https://your-n8n-domain.com/webhook/workflows-search
N8N_WORKFLOW_SEARCH_URL=https://your-n8n-domain.com/webhook/workflow-search
API_HOST=0.0.0.0
API_PORT=8000
OPENAI_MODEL=o3-mini
ANTHROPIC_MODEL=claude-3-opus-20240229
```

### 2.4 Network & Domain Configuration
- **Port**: `8000` (internal container port)
- **Domain**: `axiom8-api.your-domain.com` (or your preferred subdomain)
- **HTTPS**: ✅ Enable Let's Encrypt SSL
- **Health Check**: EasyPanel will use the built-in health check from docker-compose.yml

### 2.5 Resource Configuration
- **Memory**: `1GB` minimum, `2GB` recommended
- **CPU**: `0.5` cores minimum, `1` core recommended
- **Replicas**: `1` (can scale later)

## 🔄 Step 3: Alternative Docker Compose Deployment

If you prefer using Docker Compose directly:

### 3.1 Upload Docker Compose
1. **In EasyPanel**: Go to "Services" → "Add Service" → "Compose"
2. **Paste your docker-compose.yml content**:

```yaml
version: '3.8'

services:
  axiom8-api:
    image: ghcr.io/alexandre-axioma/axiom8:latest  # If using pre-built image
    # OR build from source:
    # build: 
    #   context: .
    #   dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      # AI API Keys
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      
      # LangSmith Tracing
      - LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT}
      
      # n8n RAG Webhook URLs
      - N8N_DOCUMENTATION_SEARCH_URL=${N8N_DOCUMENTATION_SEARCH_URL}
      - N8N_NODES_SEARCH_URL=${N8N_NODES_SEARCH_URL}
      - N8N_WORKFLOWS_SEARCH_URL=${N8N_WORKFLOWS_SEARCH_URL}
      - N8N_WORKFLOW_SEARCH_URL=${N8N_WORKFLOW_SEARCH_URL}
      
      # API Configuration
      - API_HOST=0.0.0.0
      - API_PORT=8000
      
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
    volumes:
      - ./logs:/app/logs  # Optional: persist logs
      
    networks:
      - easypanel_default  # Connect to EasyPanel's default network

networks:
  easypanel_default:
    external: true
```

## 🌐 Step 4: Network Integration with n8n

### 4.1 Internal Docker Network Setup
If both n8n and Axiom8 are in the same EasyPanel project:

1. **Service Discovery**: Use service name `axiom8-api` for internal communication
2. **Internal URL**: `http://axiom8-api:8000`
3. **External URL**: `https://axiom8-api.your-domain.com`

### 4.2 Configure n8n to Use Axiom8
Update your n8n workflows to call Axiom8:

**For n8n HTTP Request nodes:**
- **URL**: `http://axiom8-api:8000/api/v1/chat/start` (internal)
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "query": "{{ $json.user_request }}"
}
```

## 🔍 Step 5: Deployment Verification

### 5.1 Health Check
```bash
# Test health endpoint
curl https://axiom8-api.your-domain.com/health

# Expected response:
{"status":"ok"}
```

### 5.2 API Functionality Test
```bash
# Test legacy endpoint
curl -X POST "https://axiom8-api.your-domain.com/api/v1/invoke" \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a simple test workflow"}'

# Test multi-agent endpoint
curl -X POST "https://axiom8-api.your-domain.com/api/v1/chat/start" \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to monitor emails and send notifications"}'
```

### 5.3 EasyPanel Monitoring
1. **Logs**: View real-time logs in EasyPanel dashboard
2. **Metrics**: Monitor CPU, memory, and network usage
3. **Health Status**: Green indicator for healthy service

## 🔧 Step 6: Production Configuration

### 6.1 SSL/HTTPS Setup
EasyPanel automatically provisions Let's Encrypt certificates:
- ✅ **Enable HTTPS** in domain settings
- ✅ **Force HTTPS redirect**
- 🔄 **Auto-renewal** handled by EasyPanel

### 6.2 Scaling Configuration
For high-traffic scenarios:
- **Horizontal Scaling**: Increase replicas to 2-3 instances
- **Load Balancing**: EasyPanel handles automatically
- **Resource Limits**: Set memory/CPU limits in EasyPanel

### 6.3 Backup Strategy
- **GitHub Repository**: Source code backup
- **Environment Variables**: Export from EasyPanel regularly
- **Logs**: Configure log rotation and external logging if needed

## 🚨 Troubleshooting

### Common Issues

**1. Service Won't Start**
```bash
# Check logs in EasyPanel
# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Port conflicts
```

**2. n8n Can't Connect**
```bash
# Verify network connectivity
docker exec -it easypanel_axiom8-api_1 curl http://localhost:8000/health

# Check internal DNS resolution
docker exec -it easypanel_n8n_1 nslookup axiom8-api
```

**3. SSL Certificate Issues**
- Ensure domain points to your server IP
- Check EasyPanel proxy configuration
- Verify ports 80/443 are open

**4. High Memory Usage**
- Monitor in EasyPanel dashboard
- Increase memory allocation if needed
- Check for memory leaks in logs

### Performance Optimization

**1. Response Time Optimization**
- Use external caching if needed
- Monitor LangSmith traces for bottlenecks
- Consider increasing CPU allocation

**2. API Rate Limiting**
- Implement rate limiting if needed
- Monitor OpenAI/Anthropic usage
- Set up alerts for quota limits

## 📊 Monitoring & Maintenance

### 6.1 EasyPanel Built-in Monitoring
- **Real-time logs** streaming
- **Resource usage** graphs
- **Health check** status
- **Deployment history**

### 6.2 External Monitoring (Optional)
- **LangSmith**: AI agent performance tracking
- **Uptime monitoring**: External service monitoring
- **Error tracking**: Application error reporting

### 6.3 Update Process
1. **Push to GitHub**: Changes automatically deploy
2. **Manual deployment**: Use EasyPanel rebuild button
3. **Rollback**: Use EasyPanel deployment history

## 🔐 Security Best Practices

### 6.1 Environment Variables
- ✅ **Never commit API keys** to GitHub
- ✅ **Use EasyPanel secrets** for sensitive data
- ✅ **Rotate API keys** regularly
- ✅ **Monitor API usage** for anomalies

### 6.2 Network Security
- ✅ **HTTPS only** for external communication
- ✅ **Internal network** for n8n communication
- ✅ **Firewall rules** properly configured
- ✅ **Regular security updates**

### 6.3 Access Control
- ✅ **EasyPanel authentication** enabled
- ✅ **SSH key authentication** only
- ✅ **Regular backup** of configurations
- ✅ **Audit logs** monitoring

## 🎯 Next Steps

1. **Deploy the service** following this guide
2. **Test all endpoints** thoroughly
3. **Update n8n workflows** to use new API
4. **Monitor performance** for the first week
5. **Scale resources** as needed
6. **Implement additional monitoring** if required

## 📞 Support

If you encounter issues:
1. **Check EasyPanel logs** first
2. **Review GitHub Issues** for similar problems
3. **Check API documentation** in README.md
4. **Verify environment variables** are correct
5. **Test API endpoints** individually

---

**Congratulations!** 🎉 Your Axiom8 system is now deployed and ready to generate n8n workflows automatically.