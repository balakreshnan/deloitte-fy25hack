# User Interaction Flows

## Overview

This document details the user interaction flows for both Streamlit and Gradio implementations of the Azure Data Factory Agent, including Mermaid diagrams showing user journeys, system interactions, and MCP integration patterns.

## Common User Flows

### 1. First-Time User Onboarding

```mermaid
journey
    title First-Time User Journey
    section Discovery
      User learns about ADF Agent: 3: User
      User accesses application: 4: User
      User sees welcome interface: 5: User
    section First Interaction
      User reads interface instructions: 4: User
      User enters first query: 3: User
      System processes query: 2: System
      User receives response: 5: User
    section Learning
      User explores detailed information: 4: User
      User tries different query types: 4: User
      User understands capabilities: 5: User
    section Adoption
      User bookmarks application: 5: User
      User shares with team: 4: User
      User integrates into workflow: 5: User
```

### 2. Daily Usage Pattern

```mermaid
graph TD
    Start[User Starts Workday] --> Check[Check ADF Status]
    Check --> Query1["Ask: 'What pipelines ran overnight?'"]
    Query1 --> Review1[Review Pipeline Summary]
    Review1 --> Drill{Need More Details?}
    Drill -->|Yes| Query2["Ask: 'Show details for failed pipeline X'"]
    Drill -->|No| Monitor[Continue Monitoring]
    Query2 --> Review2[Review Error Details]
    Review2 --> Action[Take Corrective Action]
    Action --> Verify["Ask: 'Check status of pipeline X now'"]
    Verify --> Complete[Mark Issue Resolved]
    Monitor --> Periodic[Periodic Check-ins]
    Complete --> Periodic
    Periodic --> End[End of Day]
```

## Streamlit-Specific User Flows

### 1. Professional Dashboard Workflow

```mermaid
sequenceDiagram
    participant User as Business User
    participant ST as Streamlit UI
    participant Session as Session State
    participant Agent as ADF Agent
    participant Azure as Azure Services
    
    User->>ST: Navigate to dashboard
    ST->>Session: Initialize session state
    Session-->>ST: Empty history []
    ST-->>User: Show professional dashboard
    
    Note over User,Azure: Morning Pipeline Check
    
    User->>ST: "What's the status of overnight ETL jobs?"
    ST->>ST: Show spinner with progress
    ST->>Agent: adf_agent(query)
    Agent->>Azure: Query pipeline status
    Azure-->>Agent: Pipeline data
    Agent-->>ST: Structured response
    ST->>Session: Append to history
    ST->>ST: Update summary panel (left)
    ST->>ST: Update details panel (right)
    ST-->>User: Professional formatted results
    
    Note over User,Azure: Drill-down Analysis
    
    User->>ST: "Show me details about the failed customer pipeline"
    ST->>ST: Show loading indicator
    ST->>Agent: adf_agent(specific_query)
    Agent->>Azure: Query specific pipeline
    Azure-->>Agent: Detailed error info
    Agent-->>ST: Error analysis
    ST->>Session: Add to conversation history
    ST->>ST: Update both panels
    ST-->>User: Comprehensive error details
    
    Note over User,Azure: History Management
    
    User->>ST: Click "Clear History"
    ST->>Session: Reset history to []
    ST->>ST: Clear both panels
    ST-->>User: Fresh dashboard state
```

### 2. Multi-Panel Information Flow

```mermaid
graph TB
    subgraph "User Actions"
        Query[User Query]
        Clear[Clear History]
        Navigate[Navigate Interface]
    end
    
    subgraph "Streamlit Processing"
        Input[Chat Input]
        State[Session State]
        Agent[Agent Call]
    end
    
    subgraph "Display Panels"
        Summary[Summary Panel]
        Details[Details Panel]
        Metrics[Token Metrics]
    end
    
    subgraph "Visual Elements"
        Badges[Metric Badges]
        HTML[Rich HTML]
        Scroll[Scrollable Content]
    end
    
    Query --> Input
    Input --> Agent
    Agent --> State
    State --> Summary
    State --> Details
    Summary --> Metrics
    Details --> HTML
    Metrics --> Badges
    HTML --> Scroll
    Clear --> State
    Navigate --> Summary
    Navigate --> Details
```

## Gradio-Specific User Flows

### 1. Conversational Chat Experience

```mermaid
sequenceDiagram
    participant User as End User
    participant GR as Gradio UI
    participant State as Gradio State
    participant Chat as chat_fn
    participant Format as Formatting
    participant Agent as ADF Agent
    
    User->>GR: Access modern chat interface
    GR->>State: Initialize gr.State({})
    State-->>GR: Empty state and history
    GR-->>User: Show chat-ready interface
    
    Note over User,Agent: Interactive Conversation
    
    User->>GR: Type "How many pipelines are running?"
    GR->>Chat: chat_fn(message, history, state)
    Chat->>Chat: Add message to history
    Chat->>Agent: adf_agent(message)
    
    Note over Agent: Processing with Azure AI + MCP
    
    Agent-->>Chat: Structured response
    Chat->>Format: format_summary(response)
    Chat->>Format: format_details(response)
    Format-->>Chat: HTML formatted content
    Chat-->>GR: (history, summary_html, details_html, state)
    GR->>GR: Update summary panel
    GR->>GR: Update details panel
    GR-->>User: Real-time formatted response
    
    Note over User,Agent: Follow-up Questions
    
    User->>GR: "Tell me more about pipeline failures"
    GR->>Chat: chat_fn(follow_up, updated_history, state)
    Chat->>Agent: adf_agent(follow_up)
    Agent-->>Chat: Detailed failure analysis
    Chat->>Format: Format comprehensive details
    Format-->>Chat: Rich HTML with tables/badges
    Chat-->>GR: Updated components
    GR-->>User: Enhanced detail view
    
    Note over User,Agent: Session Management
    
    User->>GR: Click "Clear" button
    GR->>Chat: clear_cb()
    Chat-->>GR: ([], empty_summary, empty_details, {})
    GR->>GR: Reset all panels
    GR-->>User: Fresh chat interface
```

### 2. Real-time Response Formatting

```mermaid
graph TD
    subgraph "User Interaction"
        Type[Type Message]
        Send[Send/Enter]
        Clear[Clear Button]
    end
    
    subgraph "Processing Flow"
        Validate[Input Validation]
        History[Update History]
        Agent[Agent Processing]
        Response[Get Response]
    end
    
    subgraph "Formatting Pipeline"
        Extract[Extract Data]
        Summary[Format Summary]
        Details[Format Details]
        HTML[Generate HTML]
    end
    
    subgraph "UI Updates"
        SummaryPanel[Update Summary Panel]
        DetailsPanel[Update Details Panel]
        StateUpdate[Update State]
        Display[Display Results]
    end
    
    Type --> Send
    Send --> Validate
    Validate --> History
    History --> Agent
    Agent --> Response
    Response --> Extract
    Extract --> Summary
    Extract --> Details
    Summary --> HTML
    Details --> HTML
    HTML --> SummaryPanel
    HTML --> DetailsPanel
    SummaryPanel --> StateUpdate
    DetailsPanel --> StateUpdate
    StateUpdate --> Display
    Clear --> History
```

## MCP Integration User Flows

### 1. Tool Discovery and Execution

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Agent
    participant MCP as MCP Server
    participant Tools as External Tools
    participant ADF as Azure Data Factory
    
    User->>UI: "Show me the latest pipeline execution details"
    UI->>Agent: Process natural language query
    
    Note over Agent,MCP: MCP Tool Integration
    
    Agent->>MCP: Initialize MCP connection
    MCP-->>Agent: Available tools list
    Agent->>Agent: Create AI agent with MCP tools
    Agent->>Agent: Analyze query and select tools
    
    Note over Agent,Tools: Tool Execution Flow
    
    Agent->>MCP: Request tool execution approval
    MCP->>Tools: Execute ADF query tools
    Tools->>ADF: API calls to Data Factory
    ADF-->>Tools: Pipeline execution data
    Tools-->>MCP: Tool execution results
    MCP-->>Agent: Formatted tool outputs
    
    Note over Agent,UI: Response Generation
    
    Agent->>Agent: Process tool outputs with AI
    Agent->>Agent: Generate human-readable response
    Agent-->>UI: Structured response with tool details
    UI-->>User: Formatted results with execution trace
    
    Note over User,ADF: Transparency and Debugging
    
    User->>UI: View detailed execution steps
    UI-->>User: Show tool calls, approvals, outputs
    User->>UI: "Why did the pipeline fail?"
    UI->>Agent: Follow-up query with context
    Agent->>MCP: Execute diagnostic tools
    MCP-->>Agent: Detailed error analysis
    Agent-->>UI: Comprehensive failure explanation
    UI-->>User: Root cause analysis with recommendations
```

### 2. Multi-Tool Workflow

```mermaid
graph TB
    subgraph "User Query Processing"
        Query[Complex User Query]
        Parse[Parse Intent]
        Plan[Create Execution Plan]
    end
    
    subgraph "MCP Tool Orchestration"
        Discover[Discover Available Tools]
        Select[Select Required Tools]
        Sequence[Plan Tool Sequence]
        Execute[Execute Tools]
    end
    
    subgraph "Tool Categories"
        Status[Status Check Tools]
        History[History Query Tools]
        Config[Configuration Tools]
        Diagnostic[Diagnostic Tools]
    end
    
    subgraph "Data Sources"
        ADF[Azure Data Factory]
        Logs[Execution Logs]
        Metrics[Performance Metrics]
        Configs[Configuration Data]
    end
    
    Query --> Parse
    Parse --> Plan
    Plan --> Discover
    Discover --> Select
    Select --> Sequence
    Sequence --> Execute
    Execute --> Status
    Execute --> History
    Execute --> Config
    Execute --> Diagnostic
    Status --> ADF
    History --> Logs
    Config --> Configs
    Diagnostic --> Metrics
```

## Error Handling Flows

### 1. Agent Failure Recovery

```mermaid
graph TD
    UserQuery[User Query] --> Agent[Agent Processing]
    Agent --> Success{Success?}
    Success -->|Yes| Display[Display Results]
    Success -->|No| Error[Error Occurred]
    
    Error --> ErrorType{Error Type?}
    ErrorType -->|Authentication| Auth[Authentication Error]
    ErrorType -->|Network| Network[Network Error]
    ErrorType -->|MCP| MCP[MCP Tool Error]
    ErrorType -->|Agent| AgentError[Agent Processing Error]
    
    Auth --> AuthMsg[Display: Please check Azure credentials]
    Network --> NetworkMsg[Display: Connection issue, please retry]
    MCP --> McpMsg[Display: Tool execution failed]
    AgentError --> AgentMsg[Display: Processing error occurred]
    
    AuthMsg --> Retry[Offer Retry Option]
    NetworkMsg --> Retry
    McpMsg --> Retry
    AgentMsg --> Retry
    
    Retry --> UserChoice{User Choice?}
    UserChoice -->|Retry| Agent
    UserChoice -->|Cancel| Cancel[Cancel Operation]
    
    Cancel --> Ready[Interface Ready]
    Display --> Ready
```

### 2. MCP Tool Failure Handling

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Agent
    participant MCP
    participant Fallback
    
    User->>UI: Submit query
    UI->>Agent: Process query
    Agent->>MCP: Attempt tool execution
    MCP-->>Agent: Tool execution failed
    
    Agent->>Agent: Evaluate failure reason
    
    alt Tool Unavailable
        Agent->>Fallback: Use fallback method
        Fallback-->>Agent: Partial results
        Agent-->>UI: Response with limitations note
    else Server Error
        Agent->>Agent: Retry with exponential backoff
        Agent->>MCP: Retry tool execution
        MCP-->>Agent: Success/Failure
    else Authentication Error
        Agent-->>UI: Authentication error message
        UI-->>User: Prompt for credential check
    end
    
    UI-->>User: Display results or error guidance
```

## Performance and Scalability Flows

### 1. Concurrent User Management

```mermaid
graph TB
    subgraph "User Load"
        U1[User 1]
        U2[User 2]
        U3[User 3]
        Un[User N]
    end
    
    subgraph "Load Balancer"
        LB[Load Balancer]
        Queue[Request Queue]
    end
    
    subgraph "Application Instances"
        App1[Streamlit Instance 1]
        App2[Gradio Instance 1]
        App3[Streamlit Instance 2]
        App4[Gradio Instance 2]
    end
    
    subgraph "Shared Services"
        Azure[Azure AI Services]
        MCP[MCP Servers]
        ADF[Azure Data Factory]
    end
    
    U1 --> LB
    U2 --> LB
    U3 --> LB
    Un --> LB
    
    LB --> Queue
    Queue --> App1
    Queue --> App2
    Queue --> App3
    Queue --> App4
    
    App1 --> Azure
    App2 --> Azure
    App3 --> Azure
    App4 --> Azure
    
    App1 --> MCP
    App2 --> MCP
    App3 --> MCP
    App4 --> MCP
    
    Azure --> ADF
    MCP --> ADF
```

### 2. Response Caching Strategy

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Cache
    participant Agent
    participant Azure
    
    User->>UI: Submit query
    UI->>Cache: Check cache for similar query
    
    alt Cache Hit
        Cache-->>UI: Return cached response
        UI-->>User: Display cached results (with timestamp)
    else Cache Miss
        Cache-->>UI: No cached result
        UI->>Agent: Process query
        Agent->>Azure: Call Azure services
        Azure-->>Agent: Fresh data
        Agent-->>UI: New response
        UI->>Cache: Store response in cache
        UI-->>User: Display fresh results
    end
    
    Note over Cache: Cache TTL expires after 5 minutes for status queries
    
    User->>UI: Submit same query later
    UI->>Cache: Check cache
    Cache-->>UI: Expired cache entry
    UI->>Agent: Process fresh query
```

## Mobile and Accessibility Flows

### 1. Mobile User Experience

```mermaid
journey
    title Mobile User Journey
    section Mobile Access
      User opens app on mobile: 3: User
      Interface adapts to screen size: 4: System
      User sees condensed layout: 4: User
    section Interaction
      User taps on input field: 5: User
      Virtual keyboard appears: 3: System
      User types query: 4: User
      User submits query: 5: User
    section Results
      System processes query: 3: System
      Results display in mobile format: 4: System
      User scrolls through details: 4: User
      User uses touch gestures: 5: User
    section Navigation
      User swipes between panels: 4: User
      User taps to expand details: 5: User
      User shares results: 4: User
```

### 2. Accessibility Compliance Flow

```mermaid
graph TD
    subgraph "Accessibility Features"
        Screen[Screen Reader Support]
        Keyboard[Keyboard Navigation]
        Color[Color Contrast]
        Text[Text Scaling]
    end
    
    subgraph "ARIA Implementation"
        Labels[ARIA Labels]
        Roles[ARIA Roles]
        States[ARIA States]
        Properties[ARIA Properties]
    end
    
    subgraph "User Interactions"
        Tab[Tab Navigation]
        Enter[Enter Key Actions]
        Space[Space Bar Actions]
        Arrow[Arrow Key Navigation]
    end
    
    subgraph "Responsive Design"
        Mobile[Mobile Optimization]
        Tablet[Tablet Layout]
        Desktop[Desktop Experience]
        Print[Print Friendly]
    end
    
    Screen --> Labels
    Keyboard --> Tab
    Color --> Mobile
    Text --> Desktop
    Labels --> Tab
    Roles --> Enter
    States --> Space
    Properties --> Arrow
```

## Integration Testing Flows

### 1. End-to-End Testing Scenario

```mermaid
sequenceDiagram
    participant Test as Test Suite
    participant UI as Interface
    participant Agent as ADF Agent
    participant Azure as Azure Services
    participant Verify as Verification
    
    Note over Test,Verify: Automated E2E Test Flow
    
    Test->>UI: Initialize test environment
    Test->>UI: Submit test query: "Show pipeline status"
    UI->>Agent: Process test query
    Agent->>Azure: Execute test API calls
    Azure-->>Agent: Return test data
    Agent-->>UI: Format test response
    UI-->>Test: Return formatted results
    
    Test->>Verify: Validate response structure
    Test->>Verify: Check UI component updates
    Test->>Verify: Verify token usage metrics
    Test->>Verify: Confirm error handling
    
    Verify-->>Test: All validations passed
    
    Note over Test,Verify: Performance Testing
    
    Test->>UI: Submit 10 concurrent queries
    UI->>Agent: Process multiple queries
    Agent->>Azure: Execute concurrent calls
    Azure-->>Agent: Return responses
    Agent-->>UI: Format all responses
    UI-->>Test: All responses completed
    
    Test->>Verify: Check response times < 5s
    Test->>Verify: Verify no memory leaks
    Test->>Verify: Confirm UI stability
    
    Verify-->>Test: Performance criteria met
```

This comprehensive user flow documentation provides detailed insights into how users interact with both implementations of the Azure Data Factory Agent, including the sophisticated MCP integration patterns and real-world usage scenarios.