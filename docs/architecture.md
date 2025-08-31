# Architecture Overview

## System Architecture

The Azure Data Factory Agent is built on a modular, cloud-native architecture that integrates Azure AI services with Model Context Protocol (MCP) for extensible AI-powered assistance.

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        ST[Streamlit UI<br/>stadf.py]
        GR[Gradio UI<br/>gradf.py]
    end
    
    subgraph "Core Processing"
        Agent[adf_agent Function<br/>Core Logic]
        Logger[Logging System]
    end
    
    subgraph "Azure Services"
        AIP[Azure AI Projects]
        AOI[Azure OpenAI]
        AAA[Azure AI Agents]
    end
    
    subgraph "MCP Integration"
        MCP[MCP Server]
        Tools[MCP Tools]
        MS[Microsoft Learn MCP]
    end
    
    subgraph "Data Factory"
        ADF[Azure Data Factory]
        Jobs[ADF Jobs & Pipelines]
    end
    
    ST --> Agent
    GR --> Agent
    Agent --> Logger
    Agent --> AIP
    AIP --> AOI
    AIP --> AAA
    Agent --> MCP
    MCP --> Tools
    MCP --> MS
    Tools --> ADF
    ADF --> Jobs
```

## Component Architecture

### 1. User Interface Layer

```mermaid
graph LR
    subgraph "Streamlit Implementation"
        STConfig[Page Config]
        STLayout[Two-Column Layout]
        STSummary[Summary Panel]
        STDetails[Details Panel]
        STInput[Chat Input]
        STHistory[Session History]
    end
    
    subgraph "Gradio Implementation"
        GRBlocks[Gradio Blocks]
        GRPanels[Dual Panels]
        GRSummary[Summary HTML]
        GRDetails[Details HTML]
        GRChat[Chat Interface]
        GRState[State Management]
    end
```

**Streamlit Features:**
- Fixed-position chat input
- Real-time scrollable panels
- Session state management
- Professional dashboard styling

**Gradio Features:**
- Modern chat interface
- HTML-rendered panels
- State persistence
- Responsive design

### 2. Core Processing Layer

```mermaid
graph TD
    Input[User Query] --> Validate[Input Validation]
    Validate --> CreateAgent[Create AI Agent]
    CreateAgent --> CreateThread[Create Thread]
    CreateThread --> SendMessage[Send Message]
    SendMessage --> CreateRun[Create Run]
    CreateRun --> Monitor[Monitor Status]
    Monitor --> Actions{Requires Action?}
    Actions -->|Yes| Approve[Tool Approval]
    Actions -->|No| Complete[Run Complete]
    Approve --> Monitor
    Complete --> Collect[Collect Results]
    Collect --> Format[Format Response]
    Format --> Cleanup[Cleanup Resources]
    Cleanup --> Return[Return Results]
```

**Core Functions:**
- **adf_agent()**: Main orchestration function
- **Input Processing**: Query validation and preparation
- **Agent Management**: Dynamic agent creation and cleanup
- **Tool Integration**: MCP tool approval and execution
- **Response Formatting**: Structured result preparation

### 3. Azure AI Integration

```mermaid
graph TB
    subgraph "Azure AI Projects Client"
        Client[AIProjectClient]
        Cred[DefaultAzureCredential]
        Endpoint[Project Endpoint]
    end
    
    subgraph "Agents Framework"
        AgentClient[Agents Client]
        Agent[AI Agent]
        Thread[Conversation Thread]
        Run[Agent Run]
        Messages[Messages API]
        Steps[Run Steps API]
    end
    
    subgraph "OpenAI Integration"
        Model[Model Deployment]
        Instructions[Agent Instructions]
        Tools[Tool Definitions]
    end
    
    Client --> AgentClient
    AgentClient --> Agent
    Agent --> Thread
    Thread --> Run
    Thread --> Messages
    Run --> Steps
    Agent --> Model
    Agent --> Instructions
    Agent --> Tools
```

### 4. MCP Integration Architecture

```mermaid
graph TB
    subgraph "MCP Configuration"
        URL[MCP Server URL]
        Label[Server Label]
        Headers[Request Headers]
    end
    
    subgraph "MCP Tool System"
        McpTool[McpTool Instance]
        Definitions[Tool Definitions]
        Resources[Tool Resources]
        Allowed[Allowed Tools List]
    end
    
    subgraph "Tool Execution Flow"
        Detect[Tool Call Detection]
        Approve[Tool Approval]
        Execute[Tool Execution]
        Output[Tool Output]
    end
    
    URL --> McpTool
    Label --> McpTool
    Headers --> McpTool
    McpTool --> Definitions
    McpTool --> Resources
    McpTool --> Allowed
    Definitions --> Detect
    Detect --> Approve
    Approve --> Execute
    Execute --> Output
```

## Data Flow Architecture

### Request Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Core
    participant Azure
    participant MCP
    participant ADF
    
    User->>UI: Enter Query
    UI->>Core: adf_agent(query)
    Core->>Azure: Create Agent
    Azure-->>Core: Agent ID
    Core->>Azure: Create Thread
    Azure-->>Core: Thread ID
    Core->>Azure: Send Message
    Core->>Azure: Create Run
    
    loop Run Monitoring
        Core->>Azure: Check Status
        Azure-->>Core: Status Update
        alt Requires Action
            Azure-->>Core: Tool Calls
            Core->>Core: Approve Tools
            Core->>Azure: Submit Approvals
            Azure->>MCP: Execute Tools
            MCP->>ADF: Query Data Factory
            ADF-->>MCP: Job Status
            MCP-->>Azure: Tool Output
        end
    end
    
    Azure-->>Core: Final Response
    Core->>Core: Format Results
    Core->>Azure: Cleanup Agent
    Core-->>UI: Structured Response
    UI-->>User: Display Results
```

### Response Data Structure

```mermaid
graph TB
    Response[Agent Response] --> Summary[Summary Text]
    Response --> Details[Execution Details]
    Response --> Messages[Conversation Messages]
    Response --> Steps[Execution Steps]
    Response --> Usage[Token Usage]
    Response --> Status[Run Status]
    
    Messages --> UserMsg[User Messages]
    Messages --> AssistantMsg[Assistant Messages]
    
    Steps --> StepID[Step ID]
    Steps --> StepStatus[Step Status]
    Steps --> ToolCalls[Tool Calls]
    Steps --> ActivityTools[Activity Tools]
    
    ToolCalls --> CallID[Call ID]
    ToolCalls --> CallType[Call Type]
    ToolCalls --> CallArgs[Arguments]
    ToolCalls --> CallOutput[Output]
```

## Security Architecture

### Authentication & Authorization

```mermaid
graph TB
    subgraph "Authentication"
        DefaultCred[DefaultAzureCredential]
        EnvVars[Environment Variables]
        ManagedID[Managed Identity]
    end
    
    subgraph "Azure Services Auth"
        AIProjects[AI Projects]
        OpenAI[Azure OpenAI]
        KeyVault[Key Vault]
    end
    
    subgraph "MCP Security"
        McpHeaders[MCP Headers]
        ServerAuth[Server Authentication]
    end
    
    DefaultCred --> AIProjects
    DefaultCred --> OpenAI
    DefaultCred --> KeyVault
    EnvVars --> McpHeaders
    McpHeaders --> ServerAuth
```

### Environment Configuration

| Variable | Purpose | Example |
|----------|---------|---------|
| `PROJECT_ENDPOINT` | Azure AI Projects endpoint | `https://account.services.ai.azure.com/api/projects/project-name` |
| `MODEL_ENDPOINT` | Azure OpenAI endpoint | `https://account.services.ai.azure.com` |
| `MODEL_API_KEY` | Azure OpenAI API key | Secure key from Azure |
| `MODEL_DEPLOYMENT_NAME` | Model deployment name | `gpt-4o-mini` |
| `MCP_SERVER_URL` | MCP server URL | `https://learn.microsoft.com/api/mcp` |
| `MCP_SERVER_LABEL` | MCP server label | `MicrosoftLearn` |

## Scalability Considerations

### Performance Optimizations

1. **Agent Lifecycle Management**
   - Dynamic agent creation and cleanup
   - Resource management for concurrent requests
   - Connection pooling for Azure services

2. **MCP Tool Caching**
   - Tool definition caching
   - Response caching for common queries
   - Connection reuse for MCP servers

3. **UI Responsiveness**
   - Async processing patterns
   - Progressive response display
   - Efficient state management

### Deployment Patterns

```mermaid
graph TB
    subgraph "Development"
        DevLocal[Local Development]
        DevEnv[Development Environment]
    end
    
    subgraph "Staging"
        StageApp[Staging Application]
        StageAzure[Staging Azure Resources]
    end
    
    subgraph "Production"
        ProdApp[Production Application]
        ProdAzure[Production Azure Resources]
        LoadBalancer[Load Balancer]
        AutoScale[Auto Scaling]
    end
    
    DevLocal --> DevEnv
    DevEnv --> StageApp
    StageApp --> ProdApp
    ProdApp --> LoadBalancer
    LoadBalancer --> AutoScale
```

This architecture provides a robust, scalable foundation for AI-powered Azure Data Factory assistance with dual UI implementations and comprehensive MCP integration.