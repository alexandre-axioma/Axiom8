# n8n Integration Guide for Axiom8

This guide shows you how to integrate your deployed Axiom8 system with n8n workflows to automatically generate n8n workflows from natural language descriptions.

## 🎯 Integration Overview

### How It Works
1. **User Input**: User describes workflow requirements in natural language
2. **n8n Triggers**: Webhook, form submission, or manual trigger in n8n
3. **Axiom8 Processing**: Multi-agent system analyzes and generates workflow
4. **n8n Output**: Complete workflow JSON ready for import

### Integration Patterns
- **Single-Shot Generation**: One API call for simple workflow requests
- **Conversational Mode**: Multi-turn conversation for complex requirements
- **Batch Processing**: Multiple workflow generations in sequence

## 🔗 Step 1: Basic n8n HTTP Request Setup

### 1.1 Create HTTP Request Node
1. **Add Node**: `HTTP Request` node in your n8n workflow
2. **Configure**:
   - **Method**: `POST`
   - **URL**: Choose based on your deployment:
     - **Internal**: `http://axiom8-api:8000/api/v1/chat/start` (same EasyPanel project)
     - **External**: `https://axiom8-api.your-domain.com/api/v1/chat/start`

### 1.2 Basic Configuration
```json
{
  "method": "POST",
  "url": "http://axiom8-api:8000/api/v1/chat/start",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "query": "{{ $json.user_request }}"
  }
}
```

## 🚀 Step 2: Single-Shot Workflow Generation

### 2.1 Simple Workflow Generator
Perfect for straightforward requests where users provide clear requirements.

```json
{
  "nodes": [
    {
      "parameters": {
        "path": "generate-workflow",
        "responseMode": "responseNode",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "name": "Workflow Request",
      "position": [200, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "name": "user_request",
              "value": "{{ $json.body.description }}",
              "type": "string"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.set",
      "name": "Extract Request",
      "position": [400, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://axiom8-api:8000/api/v1/invoke",
        "options": {
          "timeout": 60000
        },
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "query": "{{ $json.user_request }}"
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "name": "Generate Workflow",
      "position": [600, 300]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "name": "workflow_json",
              "value": "{{ $json.output }}",
              "type": "string"
            },
            {
              "name": "session_id", 
              "value": "{{ $json.session_id }}",
              "type": "string"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.set",
      "name": "Format Response",
      "position": [800, 300]
    },
    {
      "parameters": {
        "options": {}
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "name": "Return Workflow",
      "position": [1000, 300]
    }
  ]
}
```

### 2.2 Usage Example
```bash
# Test the webhook
curl -X POST "https://your-n8n-domain.com/webhook/generate-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a workflow that monitors Twitter for mentions and sends alerts to Slack"
  }'
```

## 💬 Step 3: Conversational Workflow Generation

### 3.1 Multi-Turn Conversation Setup
For complex workflows requiring clarification and refinement.

```json
{
  "nodes": [
    {
      "parameters": {
        "path": "chat-workflow",
        "responseMode": "responseNode"
      },
      "type": "n8n-nodes-base.webhook",
      "name": "Chat Webhook",
      "position": [200, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "{{ $json.body.session_id }}",
              "operation": "exists"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.if",
      "name": "Check Session",
      "position": [400, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://axiom8-api:8000/api/v1/chat/start",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "query": "{{ $json.body.message }}"
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "name": "Start Conversation",
      "position": [600, 200]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://axiom8-api:8000/api/v1/chat/continue",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "session_id": "{{ $json.body.session_id }}",
          "message": "{{ $json.body.message }}"
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "name": "Continue Conversation",
      "position": [600, 400]
    },
    {
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "name": "response",
              "value": "{{ $json.message.content }}",
              "type": "string"
            },
            {
              "name": "session_id",
              "value": "{{ $json.session_id }}",
              "type": "string"
            },
            {
              "name": "conversation_complete",
              "value": "{{ $json.conversation_complete }}",
              "type": "boolean"
            },
            {
              "name": "current_agent",
              "value": "{{ $json.current_agent }}",
              "type": "string"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.set",
      "name": "Format Chat Response",
      "position": [800, 300]
    }
  ]
}
```

### 3.2 Conversation Flow Example
```bash
# Start conversation
curl -X POST "https://your-n8n-domain.com/webhook/chat-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to automate my email processing"
  }'

# Response:
# {
#   "session_id": "abc-123",
#   "response": "QUESTIONS: 1. What email service are you using? 2. What should happen to the processed emails?",
#   "conversation_complete": false
# }

# Continue conversation
curl -X POST "https://your-n8n-domain.com/webhook/chat-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "message": "Gmail, and I want to save important emails to Google Drive"
  }'
```

## 📊 Step 4: Advanced Integration Patterns

### 4.1 Workflow with Form Input
Create a user-friendly form for workflow requests:

```json
{
  "nodes": [
    {
      "parameters": {
        "formTitle": "Axiom8 Workflow Generator",
        "formDescription": "Describe the n8n workflow you want to create",
        "formFields": {
          "values": [
            {
              "fieldLabel": "Workflow Description",
              "fieldType": "textarea",
              "requiredField": true,
              "fieldOptions": {
                "placeholder": "Describe your workflow requirements in detail..."
              }
            },
            {
              "fieldLabel": "Complexity",
              "fieldType": "select",
              "fieldOptions": {
                "values": [
                  {"option": "Simple - Basic automation"},
                  {"option": "Medium - Multiple steps"},
                  {"option": "Complex - Advanced logic"}
                ]
              }
            }
          ]
        },
        "options": {}
      },
      "type": "n8n-nodes-base.formTrigger",
      "name": "Workflow Request Form",
      "position": [200, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://axiom8-api:8000/api/v1/chat/start",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "query": "{{ $json['Workflow Description'] }}"
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "name": "Generate Workflow",
      "position": [400, 300]
    }
  ]
}
```

### 4.2 Workflow Import Automation
Automatically import generated workflows into n8n:

```json
{
  "parameters": {
    "method": "POST",
    "url": "http://localhost:5678/api/v1/workflows",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": "={{ JSON.parse($json.workflow_json) }}"
  },
  "type": "n8n-nodes-base.httpRequest",
  "name": "Import Workflow",
  "position": [1000, 300]
}
```

### 4.3 Error Handling & Retry Logic
```json
{
  "parameters": {
    "conditions": {
      "number": [
        {
          "value1": "{{ $httpStatusCode }}",
          "operation": "equal",
          "value2": 200
        }
      ]
    }
  },
  "type": "n8n-nodes-base.if",
  "name": "Check Success",
  "position": [600, 300]
},
{
  "parameters": {
    "amount": 3,
    "unit": "seconds"
  },
  "type": "n8n-nodes-base.wait",
  "name": "Wait Before Retry",
  "position": [600, 500]
}
```

## 🔍 Step 5: Monitoring & Analytics

### 5.1 Usage Tracking
Track Axiom8 usage and performance:

```json
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "name": "timestamp",
          "value": "={{ new Date().toISOString() }}",
          "type": "string"
        },
        {
          "name": "user_request",
          "value": "{{ $json.query }}",
          "type": "string"
        },
        {
          "name": "response_time_ms",
          "value": "={{ $executionTime }}",
          "type": "number"
        },
        {
          "name": "success",
          "value": "={{ $json.session_id ? true : false }}",
          "type": "boolean"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.set",
  "name": "Track Usage",
  "position": [800, 300]
}
```

### 5.2 Performance Monitoring
Monitor response times and success rates:

```json
{
  "parameters": {
    "resource": "sheet",
    "operation": "appendOrUpdate",
    "documentId": "your-google-sheet-id",
    "sheetName": "axiom8_metrics",
    "columnToMatchOn": "A",
    "valueToMatchOn": "={{ new Date().toDateString() }}",
    "fieldsUi": {
      "values": [
        {
          "column": "timestamp",
          "value": "{{ $json.timestamp }}"
        },
        {
          "column": "response_time",
          "value": "{{ $json.response_time_ms }}"
        },
        {
          "column": "success",
          "value": "{{ $json.success }}"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.googleSheets",
  "name": "Log Metrics",
  "position": [1000, 300]
}
```

## 🔧 Step 6: Configuration & Optimization

### 6.1 Timeout Configuration
Set appropriate timeouts for complex workflows:

```json
{
  "parameters": {
    "options": {
      "timeout": 120000,  // 2 minutes for complex workflows
      "retry": {
        "count": 2,
        "interval": 5000
      }
    }
  },
  "type": "n8n-nodes-base.httpRequest",
  "name": "Generate Complex Workflow"
}
```

### 6.2 Caching Strategy
Cache frequently requested workflows:

```json
{
  "parameters": {
    "operation": "get",
    "key": "workflow_{{ $json.user_request | hash }}"
  },
  "type": "n8n-nodes-base.redis",
  "name": "Check Cache",
  "position": [400, 300]
}
```

### 6.3 Load Balancing
Distribute requests across multiple Axiom8 instances:

```json
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "name": "api_endpoint",
          "value": "={{ ['http://axiom8-api-1:8000', 'http://axiom8-api-2:8000'][Math.floor(Math.random() * 2)] }}",
          "type": "string"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.set",
  "name": "Select Endpoint"
}
```

## 🚨 Step 7: Troubleshooting

### Common Issues & Solutions

**1. Connection Timeout**
```json
// Solution: Increase timeout and add retry logic
{
  "parameters": {
    "options": {
      "timeout": 180000,  // 3 minutes
      "retry": {
        "count": 3,
        "interval": 10000
      }
    }
  }
}
```

**2. Invalid Response Format**
```json
// Solution: Add response validation
{
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "{{ $json.session_id }}",
          "operation": "exists"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.if",
  "name": "Validate Response"
}
```

**3. Rate Limiting**
```json
// Solution: Add rate limiting and queuing
{
  "parameters": {
    "amount": 2,
    "unit": "seconds"
  },
  "type": "n8n-nodes-base.wait",
  "name": "Rate Limit"
}
```

## 📈 Step 8: Scaling & Production

### 8.1 Production Checklist
- ✅ **Error handling** implemented
- ✅ **Timeout configurations** set
- ✅ **Retry logic** added
- ✅ **Monitoring** in place
- ✅ **Rate limiting** configured
- ✅ **Caching** strategy implemented
- ✅ **Load testing** completed

### 8.2 Performance Optimization
- **Parallel processing** for multiple requests
- **Connection pooling** for HTTP requests
- **Response caching** for common workflows
- **Async processing** for long-running generations

### 8.3 Scaling Strategies
- **Horizontal scaling**: Multiple Axiom8 instances
- **Load balancing**: Distribute requests evenly
- **Queue management**: Handle high-volume requests
- **Resource monitoring**: Track CPU, memory, and response times

## 🎯 Next Steps

1. **Implement basic integration** using single-shot pattern
2. **Test with simple workflows** to verify functionality
3. **Add conversational mode** for complex requirements
4. **Implement monitoring** and error handling
5. **Scale based on usage** patterns and performance metrics

---

**Your n8n workflows can now generate other n8n workflows automatically!** 🚀