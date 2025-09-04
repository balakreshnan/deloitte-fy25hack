# stadfops.py Architecture Blueprint

## Executive Summary

The Azure Data Factory Operations Agent (`stadfops.py`) represents an enterprise-grade evolution of the base ADF Agent, specifically designed for production operations and real-time monitoring of Azure Data Factory environments. This architecture blueprint outlines the technical design, operational enhancements, and production deployment patterns.

## Architectural Philosophy

### Design Principles

1. **Operations-First Design**: Built specifically for production monitoring and incident response
2. **Direct Integration**: Native Azure Data Factory API integration for real-time data access
3. **Production Resilience**: Enhanced error handling, timeout management, and graceful degradation
4. **Security by Design**: Enterprise authentication patterns and compliance-ready architecture
5. **Extensible Framework**: Modular design supporting future operational tool additions

## System Architecture

### Layered Architecture Overview

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Enhanced Streamlit UI]
        CSS[Operational CSS Styling]
        State[Session State Management]
        Input[Chat Interface]
    end
    
    subgraph "Application Layer"
        Main[ui_main Function]
        Agent[adf_agent Orchestrator]
        CSS_Inject[_inject_css Function]
        Logger[Enhanced Logging System]
    end
    
    subgraph "Service Layer"
        Functions[Function Tool Engine]
        Pipeline[adf_pipeline_runs]
        Activity[adf_pipeline_activity_runs]
        MCP[MCP Integration]
    end
    
    subgraph "Integration Layer"
        Azure[Azure AI Projects Client]
        OpenAI[Azure OpenAI Service]
        ADF_API[Azure Data Factory APIs]
        Auth[Azure Authentication]
    end
    
    subgraph "Infrastructure Layer"
        Management[Azure Management APIs]
        DataFactory[Azure Data Factory Service]
        Identity[Managed Identity Service]
        Networking[Azure Networking]
    end
    
    UI --> Main
    Main --> Agent
    Agent --> Functions
    Agent --> MCP
    Functions --> Pipeline
    Functions --> Activity
    Pipeline --> ADF_API
    Activity --> ADF_API
    Azure --> OpenAI
    ADF_API --> Management
    Management --> DataFactory
    Auth --> Identity
```

### Component Interaction Model

```mermaid
graph LR
    subgraph "Frontend Components"
        StreamlitUI[Streamlit UI Framework]
        SessionMgmt[Session Management]
        UIComponents[UI Components]
    end
    
    subgraph "Core Processing"
        Orchestrator[Agent Orchestrator]
        FunctionEngine[Function Tool Engine]
        ResponseProcessor[Response Processor]
    end
    
    subgraph "Azure Services"
        AIProjects[Azure AI Projects]
        OpenAIService[Azure OpenAI]
        DataFactoryAPI[Data Factory APIs]
    end
    
    subgraph "External Services"
        MCPServer[MCP Server]
        LearnDocs[Microsoft Learn]
    end
    
    StreamlitUI <--> Orchestrator
    SessionMgmt <--> Orchestrator
    Orchestrator <--> FunctionEngine
    Orchestrator <--> AIProjects
    FunctionEngine <--> DataFactoryAPI
    AIProjects <--> OpenAIService
    Orchestrator <--> MCPServer
    MCPServer <--> LearnDocs
    ResponseProcessor <--> Orchestrator
```

## Core Components Deep Dive

### 1. Function Tool Engine

The Function Tool Engine represents a significant architectural advancement over the basic version, providing direct operational capabilities.

```mermaid
classDiagram
    class FunctionToolEngine {
        +FunctionTool functions
        +initialize(user_functions)
        +process_tool_calls(calls)
        +handle_execution(call)
    }
    
    class PipelineOperations {
        +adf_pipeline_runs(pipeline_name)
        +authenticate_azure()
        +query_pipeline_api()
        +format_response()
    }
    
    class ActivityOperations {
        +adf_pipeline_activity_runs(run_id)
        +authenticate_azure()
        +query_activity_api()
        +format_detailed_response()
    }
    
    class ErrorHandler {
        +handle_auth_errors()
        +handle_api_errors()
        +handle_network_errors()
        +format_error_response()
    }
    
    FunctionToolEngine --> PipelineOperations
    FunctionToolEngine --> ActivityOperations
    FunctionToolEngine --> ErrorHandler
```

### 2. Azure Data Factory Integration

```mermaid
sequenceDiagram
    participant FT as Function Tool
    participant Auth as Azure Auth
    participant API as Management API
    participant ADF as Data Factory
    
    Note over FT,ADF: Pipeline Query Flow
    FT->>Auth: Get Azure AD Token
    Auth-->>FT: Bearer Token
    FT->>API: POST queryPipelineRuns
    API->>ADF: Query Pipeline Data
    ADF-->>API: Pipeline Run Results
    API-->>FT: Formatted Response
    
    Note over FT,ADF: Activity Query Flow
    FT->>Auth: Get Azure AD Token (reuse)
    FT->>API: POST queryActivityRuns
    API->>ADF: Query Activity Data
    ADF-->>API: Activity Run Details
    API-->>FT: Detailed Response
```

### 3. Enhanced UI Architecture

```mermaid
graph TD
    subgraph "UI Component Hierarchy"
        App[Streamlit App]
        Config[Page Configuration]
        CSS[Custom CSS Injection]
        Layout[Two-Column Layout]
        
        subgraph "Left Panel"
            SummaryContainer[Summary Container]
            QueryDisplay[Query Display]
            ResponseDisplay[Response Display]
            TokenMetrics[Token Usage Metrics]
        end
        
        subgraph "Right Panel"
            DetailsContainer[Details Container]
            ConversationHistory[Conversation History]
            StepsExpander[Steps & Tool Calls]
            OutputsExpander[Tool Outputs]
            DebugLogs[Debug Logs]
        end
        
        subgraph "Input System"
            ChatInput[Fixed Chat Input]
            SessionState[Session State]
            HistoryManagement[History Management]
        end
    end
    
    App --> Config
    App --> CSS
    App --> Layout
    Layout --> SummaryContainer
    Layout --> DetailsContainer
    SummaryContainer --> QueryDisplay
    SummaryContainer --> ResponseDisplay
    SummaryContainer --> TokenMetrics
    DetailsContainer --> ConversationHistory
    DetailsContainer --> StepsExpander
    DetailsContainer --> OutputsExpander
    DetailsContainer --> DebugLogs
    App --> ChatInput
    ChatInput --> SessionState
    SessionState --> HistoryManagement
```

## Data Flow Architecture

### Request Processing Pipeline

```mermaid
flowchart TD
    UserInput[User Input] --> Validation[Input Validation]
    Validation --> AgentInit[Agent Initialization]
    
    AgentInit --> ToolSetup[Tool Setup]
    ToolSetup --> FunctionTools[Function Tools Registration]
    ToolSetup --> MCPTools[MCP Tools Registration]
    
    FunctionTools --> PipelineFunc[adf_pipeline_runs]
    FunctionTools --> ActivityFunc[adf_pipeline_activity_runs]
    
    AgentInit --> ThreadCreation[Thread Creation]
    ThreadCreation --> MessageSend[Send User Message]
    MessageSend --> RunCreation[Create Agent Run]
    
    RunCreation --> RunMonitoring[Run Status Monitoring]
    RunMonitoring --> RequiresAction{Requires Action?}
    
    RequiresAction -->|Yes| ToolApproval[Tool Approval Process]
    RequiresAction -->|No| Completion[Run Completion]
    
    ToolApproval --> ToolExecution[Tool Execution]
    ToolExecution --> OutputSubmission[Submit Tool Outputs]
    OutputSubmission --> RunMonitoring
    
    Completion --> ResultCollection[Collect Results]
    ResultCollection --> ResponseFormatting[Format Response]
    ResponseFormatting --> UIUpdate[Update UI]
    UIUpdate --> UserDisplay[Display to User]
```

### Data Transformation Flow

```mermaid
graph LR
    subgraph "Input Processing"
        UserQuery[User Query]
        QueryParsing[Query Parsing]
        IntentAnalysis[Intent Analysis]
    end
    
    subgraph "Data Retrieval"
        ADFAPICalls[ADF API Calls]
        PipelineData[Pipeline Data]
        ActivityData[Activity Data]
    end
    
    subgraph "Data Processing"
        DataFiltering[Data Filtering]
        DataAggregation[Data Aggregation]
        DataFormatting[Data Formatting]
    end
    
    subgraph "Response Generation"
        AIProcessing[AI Processing]
        ResponseGeneration[Response Generation]
        UIFormatting[UI Formatting]
    end
    
    UserQuery --> QueryParsing
    QueryParsing --> IntentAnalysis
    IntentAnalysis --> ADFAPICalls
    ADFAPICalls --> PipelineData
    ADFAPICalls --> ActivityData
    PipelineData --> DataFiltering
    ActivityData --> DataFiltering
    DataFiltering --> DataAggregation
    DataAggregation --> DataFormatting
    DataFormatting --> AIProcessing
    AIProcessing --> ResponseGeneration
    ResponseGeneration --> UIFormatting
```

## Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant App as stadfops.py
    participant Cred as DefaultAzureCredential
    participant AAD as Azure Active Directory
    participant RBAC as Azure RBAC
    participant ADF as Data Factory APIs
    
    Note over App,ADF: Authentication Flow
    App->>Cred: Initialize Credential Chain
    Cred->>AAD: Attempt Authentication
    Note over Cred: Try: Managed Identity, CLI, Environment
    AAD-->>Cred: Access Token
    
    Note over App,ADF: Authorization Flow
    App->>ADF: API Request with Token
    ADF->>RBAC: Validate Permissions
    RBAC-->>ADF: Permission Check Result
    ADF-->>App: API Response or Access Denied
```

### Security Boundaries

```mermaid
graph TB
    subgraph "Client Tier"
        Browser[User Browser]
        StreamlitApp[Streamlit Application]
    end
    
    subgraph "Application Tier"
        AppServer[Application Server]
        SessionMgmt[Session Management]
        Auth[Authentication Layer]
    end
    
    subgraph "Service Tier"
        AIProjects[Azure AI Projects]
        OpenAI[Azure OpenAI]
        DataFactory[Azure Data Factory]
    end
    
    subgraph "Security Controls"
        AAD[Azure Active Directory]
        RBAC[Role-Based Access Control]
        Network[Network Security Groups]
        Encryption[Encryption in Transit]
    end
    
    Browser -.->|HTTPS| StreamlitApp
    StreamlitApp -.->|Secure Connection| AppServer
    AppServer --> Auth
    Auth --> AAD
    AppServer --> AIProjects
    AppServer --> DataFactory
    AAD --> RBAC
    Network -.-> AppServer
    Encryption -.-> AppServer
```

## Scalability & Performance

### Performance Architecture

```mermaid
graph TD
    subgraph "Frontend Performance"
        AsyncUI[Async UI Updates]
        StateOpt[State Optimization]
        CSSOptim[CSS Optimization]
    end
    
    subgraph "Application Performance"
        ConnectionPool[Connection Pooling]
        RequestCache[Request Caching]
        ErrorCache[Error Response Caching]
    end
    
    subgraph "Service Performance"
        APIOptim[API Call Optimization]
        BatchRequests[Batch Requests]
        TimeoutMgmt[Timeout Management]
    end
    
    subgraph "Infrastructure Performance"
        ResourceMgmt[Resource Management]
        MemoryOpt[Memory Optimization]
        NetworkOpt[Network Optimization]
    end
    
    AsyncUI --> ConnectionPool
    StateOpt --> RequestCache
    CSSOptim --> ResourceMgmt
    ConnectionPool --> APIOptim
    RequestCache --> BatchRequests
    ErrorCache --> TimeoutMgmt
    APIOptim --> ResourceMgmt
    BatchRequests --> MemoryOpt
    TimeoutMgmt --> NetworkOpt
```

### Deployment Patterns

```mermaid
graph TB
    subgraph "Development Environment"
        DevLocal[Local Development]
        DevAzure[Development Azure Resources]
        DevTesting[Development Testing]
    end
    
    subgraph "Staging Environment"
        StageApp[Staging Application]
        StageAzure[Staging Azure Resources]
        StageValidation[Staging Validation]
    end
    
    subgraph "Production Environment"
        ProdApp[Production Application]
        ProdAzure[Production Azure Resources]
        ProdMonitoring[Production Monitoring]
        LoadBalancer[Load Balancer]
        AutoScale[Auto Scaling]
    end
    
    DevLocal --> StageApp
    DevAzure --> StageAzure
    DevTesting --> StageValidation
    StageApp --> ProdApp
    StageAzure --> ProdAzure
    StageValidation --> ProdMonitoring
    ProdApp --> LoadBalancer
    LoadBalancer --> AutoScale
```

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose | Version |
|-------|------------|---------|---------|
| **Frontend** | Streamlit | Web UI Framework | Latest |
| **Backend** | Python | Application Logic | 3.8+ |
| **AI/ML** | Azure OpenAI | Language Model | GPT-4 |
| **Integration** | Azure AI Projects | Agent Framework | Latest |
| **Data Source** | Azure Data Factory | Data Pipeline Platform | Latest |
| **Authentication** | Azure AD | Identity Management | Latest |
| **Deployment** | Docker/Azure | Container Platform | Latest |

### Dependencies

```mermaid
graph TD
    subgraph "Python Dependencies"
        Streamlit[streamlit]
        AzureAI[azure-ai-projects]
        AzureIdentity[azure-identity]
        OpenAI[openai]
        Requests[requests]
        DotEnv[python-dotenv]
    end
    
    subgraph "Azure Services"
        AIProjects[Azure AI Projects]
        OpenAIService[Azure OpenAI]
        DataFactory[Azure Data Factory]
        ActiveDirectory[Azure Active Directory]
    end
    
    subgraph "External Services"
        MCPServer[MCP Server]
        LearnAPI[Microsoft Learn API]
    end
    
    Streamlit --> AzureAI
    AzureAI --> AzureIdentity
    AzureAI --> OpenAI
    AzureIdentity --> ActiveDirectory
    OpenAI --> OpenAIService
    Requests --> DataFactory
    AzureAI --> AIProjects
```

## Operational Considerations

### Monitoring & Observability

```mermaid
graph LR
    subgraph "Application Monitoring"
        AppLogs[Application Logs]
        PerfMetrics[Performance Metrics]
        ErrorTracking[Error Tracking]
    end
    
    subgraph "Azure Monitoring"
        AzureMonitor[Azure Monitor]
        AppInsights[Application Insights]
        LogAnalytics[Log Analytics]
    end
    
    subgraph "Business Monitoring"
        UsageMetrics[Usage Metrics]
        UserSatisfaction[User Satisfaction]
        CostTracking[Cost Tracking]
    end
    
    AppLogs --> AzureMonitor
    PerfMetrics --> AppInsights
    ErrorTracking --> LogAnalytics
    AzureMonitor --> UsageMetrics
    AppInsights --> UserSatisfaction
    LogAnalytics --> CostTracking
```

### Maintenance & Updates

```mermaid
timeline
    title Maintenance Timeline
    
    section Daily
        Health Checks    : Monitor system health
                        : Check error rates
                        : Validate authentication
    
    section Weekly
        Performance Review : Analyze response times
                          : Review usage patterns
                          : Update documentation
    
    section Monthly
        Security Updates  : Update dependencies
                         : Security assessments
                         : Access reviews
    
    section Quarterly
        Architecture Review : Evaluate scaling needs
                           : Technology updates
                           : Strategic planning
```

This architecture blueprint provides the technical foundation for understanding, deploying, and maintaining the Azure Data Factory Operations Agent in enterprise environments.