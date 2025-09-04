# stadfops.py Installation & Deployment Guide

## Quick Start Guide

### Prerequisites

Before deploying the Azure Data Factory Operations Agent (`stadfops.py`), ensure you have the following Azure resources and permissions configured:

#### Azure Resources Required
- **Azure Subscription** with appropriate permissions
- **Azure AI Projects** workspace with deployed model
- **Azure OpenAI Service** with GPT model deployment
- **Azure Data Factory** with active pipelines
- **Azure Active Directory** for authentication

#### Permissions Required
```bash
# Required Azure RBAC roles
- "Data Factory Contributor" or "Data Factory Reader"
- "Cognitive Services User" 
- "AI Projects User"
- "Reader" on the subscription (for management APIs)
```

### Environment Setup

#### 1. Clone Repository and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/balakreshnan/deloitte-fy25hack.git
cd deloitte-fy25hack

# Create virtual environment (recommended)
python -m venv stadfops-env
source stadfops-env/bin/activate  # On Windows: stadfops-env\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

#### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Azure AI Projects Configuration
PROJECT_ENDPOINT=https://your-account.services.ai.azure.com/api/projects/your-project-name
MODEL_ENDPOINT=https://your-account.services.ai.azure.com
MODEL_API_KEY=your-model-api-key
MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Azure OpenAI Configuration (alternative to MODEL_* above)
AZURE_OPENAI_ENDPOINT=https://your-openai-instance.openai.azure.com
AZURE_OPENAI_KEY=your-openai-api-key

# MCP Server Configuration
MCP_SERVER_URL=https://learn.microsoft.com/api/mcp
MCP_SERVER_LABEL=MicrosoftLearn

# Azure Data Factory Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group-name
AZURE_DATA_FACTORY_NAME=your-data-factory-name
```

#### 3. Verify Configuration

```bash
# Test Azure authentication
az login
az account show

# Verify Data Factory access
az datafactory pipeline list --factory-name your-data-factory-name --resource-group your-resource-group-name

# Test basic functionality
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Configuration loaded successfully')
print(f'Project Endpoint: {os.getenv(\"PROJECT_ENDPOINT\", \"Not set\")}')
print(f'Data Factory: {os.getenv(\"AZURE_DATA_FACTORY_NAME\", \"Not set\")}')
"
```

### Running the Application

#### Local Development

```bash
# Run the Streamlit application
streamlit run stadfops.py

# Custom configuration
streamlit run stadfops.py --server.port 8501 --server.address 0.0.0.0

# With debug logging
streamlit run stadfops.py --logger.level debug
```

#### Docker Deployment

```dockerfile
# Dockerfile for stadfops.py
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY stadfops.py .
COPY .env .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "stadfops.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

```bash
# Build and run Docker container
docker build -t stadfops:latest .
docker run -p 8501:8501 --env-file .env stadfops:latest
```

#### Azure Container Apps Deployment

```yaml
# container-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: stadfops-config
data:
  PROJECT_ENDPOINT: "https://your-account.services.ai.azure.com/api/projects/your-project"
  MODEL_DEPLOYMENT_NAME: "gpt-4o-mini"
  MCP_SERVER_URL: "https://learn.microsoft.com/api/mcp"
  MCP_SERVER_LABEL: "MicrosoftLearn"
  AZURE_SUBSCRIPTION_ID: "your-subscription-id"
  AZURE_RESOURCE_GROUP: "your-resource-group"
  AZURE_DATA_FACTORY_NAME: "your-data-factory"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stadfops-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: stadfops
  template:
    metadata:
      labels:
        app: stadfops
    spec:
      containers:
      - name: stadfops
        image: your-registry/stadfops:latest
        ports:
        - containerPort: 8501
        envFrom:
        - configMapRef:
            name: stadfops-config
        - secretRef:
            name: stadfops-secrets
```

### Security Configuration

#### Managed Identity Setup

```bash
# Create managed identity
az identity create --resource-group your-resource-group --name stadfops-identity

# Assign Data Factory permissions
az role assignment create \
  --assignee-object-id $(az identity show --resource-group your-resource-group --name stadfops-identity --query principalId -o tsv) \
  --assignee-principal-type ServicePrincipal \
  --role "Data Factory Reader" \
  --scope /subscriptions/your-subscription-id/resourceGroups/your-resource-group/providers/Microsoft.DataFactory/factories/your-data-factory

# Assign AI Services permissions
az role assignment create \
  --assignee-object-id $(az identity show --resource-group your-resource-group --name stadfops-identity --query principalId -o tsv) \
  --assignee-principal-type ServicePrincipal \
  --role "Cognitive Services User" \
  --scope /subscriptions/your-subscription-id
```

#### Environment Variables for Production

```bash
# Production environment variables
export AZURE_CLIENT_ID=your-managed-identity-client-id
export AZURE_TENANT_ID=your-tenant-id
export AZURE_SUBSCRIPTION_ID=your-subscription-id

# Remove API keys when using managed identity
unset MODEL_API_KEY
unset AZURE_OPENAI_KEY
```

### Monitoring & Logging

#### Application Insights Integration

```python
# Add to stadfops.py for monitoring
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Application Insights
configure_azure_monitor(
    connection_string="your-app-insights-connection-string"
)

# Add structured logging
logger = logging.getLogger(__name__)
logger.info("stadfops.py application started")
```

#### Health Check Endpoint

```python
# Add health check function to stadfops.py
def health_check():
    """Simple health check for monitoring"""
    try:
        # Test Azure authentication
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default")
        
        # Test project client connection
        from azure.ai.projects import AIProjectClient
        client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential
        )
        
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow().isoformat()}
```

### Troubleshooting Common Issues

#### Authentication Issues

```bash
# Debug authentication
az account show
az login --scope https://management.azure.com/

# Test specific resource access
az datafactory show --name your-data-factory --resource-group your-resource-group
```

#### Permission Issues

```bash
# Check current role assignments
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Verify Data Factory access
az datafactory pipeline list --factory-name your-data-factory --resource-group your-resource-group
```

#### Network Connectivity

```bash
# Test Azure endpoints
curl -I https://management.azure.com/
curl -I https://your-account.services.ai.azure.com/

# Test from application environment
python -c "
import requests
response = requests.get('https://management.azure.com/')
print(f'Azure Management API: {response.status_code}')
"
```

### Performance Optimization

#### Streamlit Configuration

```toml
# .streamlit/config.toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableWebsocketCompression = true

[client]
showErrorDetails = false
toolbarMode = "minimal"

[browser]
gatherUsageStats = false
```

#### Memory Optimization

```python
# Add to stadfops.py for memory management
import gc
import psutil

def monitor_memory():
    """Monitor memory usage"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        "rss": memory_info.rss / 1024 / 1024,  # MB
        "vms": memory_info.vms / 1024 / 1024   # MB
    }

# Add garbage collection after heavy operations
def cleanup_session():
    """Clean up session resources"""
    if len(st.session_state.history) > 50:  # Limit history size
        st.session_state.history = st.session_state.history[-25:]
    gc.collect()
```

### Scaling Considerations

#### Horizontal Scaling

```yaml
# Azure Container Apps scaling configuration
scale:
  minReplicas: 2
  maxReplicas: 10
  rules:
  - name: http-scaling
    http:
      metadata:
        concurrentRequests: "10"
```

#### Load Balancing

```nginx
# Nginx configuration for load balancing
upstream stadfops_backend {
    server stadfops-1:8501;
    server stadfops-2:8501;
    server stadfops-3:8501;
}

server {
    listen 80;
    location / {
        proxy_pass http://stadfops_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

This installation and deployment guide provides comprehensive instructions for deploying the Azure Data Factory Operations Agent in various environments, from local development to enterprise production deployments.