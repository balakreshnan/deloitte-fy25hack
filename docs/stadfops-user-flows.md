# stadfops.py User Flows & Sequence Diagrams

## Overview

This document provides comprehensive user flow diagrams and sequence diagrams for the Azure Data Factory Operations Agent (`stadfops.py`), detailing the interaction patterns, technical flows, and operational sequences that define the user experience.

## Primary User Flows

### 1. Initial User Onboarding Flow

```mermaid
flowchart TD
    Start[User Accesses stadfops.py] --> Check[System Checks Authentication]
    Check --> AuthStatus{Authentication Valid?}
    
    AuthStatus -->|No| AuthError[Display Authentication Error]
    AuthError --> AuthGuide[Show Authentication Guide]
    AuthGuide --> RetryAuth[User Re-authenticates]
    RetryAuth --> Check
    
    AuthStatus -->|Yes| LoadUI[Load Dashboard Interface]
    LoadUI --> InitSession[Initialize Session State]
    InitSession --> CheckPerms[Check ADF Permissions]
    
    CheckPerms --> PermsValid{Permissions Valid?}
    PermsValid -->|No| PermError[Display Permission Error]
    PermError --> ContactAdmin[Suggest Contacting Admin]
    
    PermsValid -->|Yes| ShowWelcome[Show Welcome Interface]
    ShowWelcome --> DisplayHelp[Display Usage Examples]
    DisplayHelp --> Ready[System Ready for Queries]
    
    Ready --> FirstQuery[User Enters First Query]
    FirstQuery --> ProcessQuery[Process User Query]
    ProcessQuery --> ShowResults[Display Results]
    ShowResults --> EndOnboarding[Onboarding Complete]
```

### 2. Operational Monitoring Workflow

```mermaid
flowchart TD
    UserQuery[User Enters Query] --> QueryType{Query Type Analysis}
    
    QueryType -->|Pipeline Status| PipelineFlow[Pipeline Status Flow]
    QueryType -->|Activity Details| ActivityFlow[Activity Details Flow]
    QueryType -->|Historical Analysis| HistoryFlow[Historical Analysis Flow]
    QueryType -->|General Help| HelpFlow[Help & Documentation Flow]
    
    subgraph PipelineFlow [Pipeline Status Workflow]
        P1[Parse Pipeline Name/Pattern]
        P2[Call adf_pipeline_runs Function]
        P3[Query Azure Data Factory API]
        P4[Process Pipeline Status Data]
        P5[Generate AI-Enhanced Response]
        P6[Display Pipeline Status Summary]
        
        P1 --> P2 --> P3 --> P4 --> P5 --> P6
    end
    
    subgraph ActivityFlow [Activity Details Workflow]
        A1[Identify Required Run ID]
        A2[Get Run ID from Pipeline Query]
        A3[Call adf_pipeline_activity_runs Function]
        A4[Query Activity Runs API]
        A5[Analyze Activity Failures]
        A6[Generate Diagnostic Response]
        A7[Display Activity Analysis]
        
        A1 --> A2 --> A3 --> A4 --> A5 --> A6 --> A7
    end
    
    subgraph HistoryFlow [Historical Analysis Workflow]
        H1[Define Time Range]
        H2[Collect Historical Data]
        H3[Perform Trend Analysis]
        H4[Generate Insights]
        H5[Display Trends & Patterns]
        
        H1 --> H2 --> H3 --> H4 --> H5
    end
    
    subgraph HelpFlow [Help & Documentation Workflow]
        Help1[Query MCP Documentation Server]
        Help2[Retrieve Relevant Documentation]
        Help3[Generate Contextual Help]
        Help4[Display Help Information]
        
        Help1 --> Help2 --> Help3 --> Help4
    end
    
    PipelineFlow --> Results[Display Results in UI]
    ActivityFlow --> Results
    HistoryFlow --> Results
    HelpFlow --> Results
    
    Results --> FollowUp{User Follow-up?}
    FollowUp -->|Yes| UserQuery
    FollowUp -->|No| SessionEnd[Session Continues/Ends]
```

### 3. Incident Response Workflow

```mermaid
flowchart TD
    Alert[Pipeline Failure Alert] --> UserAccess[User Accesses stadfops.py]
    UserAccess --> EmergencyMode[Emergency Response Mode]
    
    EmergencyMode --> QuickStatus[Quick Status Check]
    QuickStatus --> CriticalQuery["Ask: 'What pipelines are failing?'"]
    
    CriticalQuery --> FailureList[Display Failed Pipelines]
    FailureList --> SelectPipeline[User Selects Critical Pipeline]
    
    SelectPipeline --> DetailedInvestigation["Ask: 'Why did [Pipeline] fail?'"]
    DetailedInvestigation --> TwoPhaseAnalysis[Two-Phase Analysis]
    
    subgraph TwoPhaseAnalysis [Detailed Analysis Process]
        Phase1[Phase 1: Get Pipeline Run Status]
        Phase2[Phase 2: Analyze Failed Activities]
        ErrorAnalysis[Comprehensive Error Analysis]
        RootCause[Root Cause Identification]
        
        Phase1 --> Phase2 --> ErrorAnalysis --> RootCause
    end
    
    TwoPhaseAnalysis --> ResolutionGuidance[Generate Resolution Guidance]
    ResolutionGuidance --> ActionPlan[Present Action Plan]
    
    ActionPlan --> UserDecision{User Decision}
    UserDecision -->|Need More Info| FollowUpQuestions[Follow-up Questions]
    UserDecision -->|Ready to Resolve| BeginResolution[Begin Resolution Process]
    UserDecision -->|Escalate| EscalationPath[Escalation Procedure]
    
    FollowUpQuestions --> DetailedInvestigation
    BeginResolution --> DocumentResolution[Document Resolution Steps]
    EscalationPath --> DocumentIncident[Document for Escalation]
    
    DocumentResolution --> IncidentClosure[Incident Resolution]
    DocumentIncident --> EscalationComplete[Escalation Complete]
```

### 4. Self-Service Analytics Workflow

```mermaid
flowchart TD
    AnalyticsRequest[User Requests Analytics] --> RequestType{Analysis Type}
    
    RequestType -->|Performance Analysis| PerfAnalysis[Performance Analysis]
    RequestType -->|Trend Analysis| TrendAnalysis[Trend Analysis]
    RequestType -->|Compliance Report| ComplianceReport[Compliance Reporting]
    RequestType -->|Cost Analysis| CostAnalysis[Cost Analysis]
    
    subgraph PerfAnalysis [Performance Analysis Flow]
        PA1[Define Performance Metrics]
        PA2[Collect Execution Data]
        PA3[Calculate Performance KPIs]
        PA4[Identify Performance Issues]
        PA5[Generate Optimization Recommendations]
        
        PA1 --> PA2 --> PA3 --> PA4 --> PA5
    end
    
    subgraph TrendAnalysis [Trend Analysis Flow]
        TA1[Define Analysis Period]
        TA2[Collect Historical Data]
        TA3[Perform Statistical Analysis]
        TA4[Identify Patterns & Anomalies]
        TA5[Generate Predictive Insights]
        
        TA1 --> TA2 --> TA3 --> TA4 --> TA5
    end
    
    subgraph ComplianceReport [Compliance Reporting Flow]
        CR1[Define Compliance Requirements]
        CR2[Collect Audit Data]
        CR3[Validate Against Standards]
        CR4[Generate Compliance Report]
        CR5[Export for Audit]
        
        CR1 --> CR2 --> CR3 --> CR4 --> CR5
    end
    
    PerfAnalysis --> DisplayResults[Display Analysis Results]
    TrendAnalysis --> DisplayResults
    ComplianceReport --> DisplayResults
    CostAnalysis --> DisplayResults
    
    DisplayResults --> ExportOptions[Provide Export Options]
    ExportOptions --> ShareResults[Share with Stakeholders]
```

## Technical Sequence Diagrams

### 1. Complete Query Processing Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Agent as adf_agent()
    participant Azure as Azure AI Projects
    participant Functions as Function Tools
    participant ADF as Azure Data Factory API
    participant MCP as MCP Server
    participant Auth as Azure Authentication
    
    Note over User,Auth: Complete Query Processing Flow
    
    User->>UI: Enter query "Show me failed CustomerETL activities"
    UI->>UI: Update session state
    UI->>UI: Show processing spinner
    
    UI->>Agent: adf_agent(user_query)
    
    Note over Agent: Agent Initialization
    Agent->>Auth: Initialize DefaultAzureCredential
    Auth-->>Agent: Authentication token
    
    Agent->>Azure: Initialize AI Projects Client
    Azure-->>Agent: Client instance
    
    Agent->>Agent: Setup Function Tools (adf_pipeline_runs, adf_pipeline_activity_runs)
    Agent->>Agent: Setup MCP Tools (Microsoft Learn)
    
    Note over Agent,Azure: AI Agent Creation
    Agent->>Azure: Create AI Agent with tools
    Azure-->>Agent: Agent ID and configuration
    
    Agent->>Azure: Create conversation thread
    Azure-->>Agent: Thread ID
    
    Agent->>Azure: Send user message to thread
    Azure-->>Agent: Message confirmation
    
    Agent->>Azure: Create agent run
    Azure-->>Agent: Run ID and initial status
    
    Note over Agent,Azure: Run Monitoring & Tool Execution
    loop Run Status Monitoring
        Agent->>Azure: Check run status
        Azure-->>Agent: Status update
        
        alt Status: requires_action
            Azure-->>Agent: Tool calls required
            
            Note over Agent: Function Tool Execution
            Agent->>Functions: adf_pipeline_runs("CustomerETL")
            Functions->>Auth: Get Azure token
            Auth-->>Functions: Bearer token
            Functions->>ADF: POST queryPipelineRuns
            ADF-->>Functions: Pipeline run data with runId
            Functions-->>Agent: Formatted JSON response
            
            Agent->>Functions: adf_pipeline_activity_runs(runId)
            Functions->>ADF: POST queryActivityRuns
            ADF-->>Functions: Activity run details
            Functions-->>Agent: Activity failure analysis
            
            Agent->>Azure: Submit tool outputs
            Azure-->>Agent: Tool outputs accepted
            
        else Status: completed
            Note over Azure: AI Processing Complete
        end
    end
    
    Note over Agent,Azure: Results Collection
    Agent->>Azure: Get final assistant response
    Azure-->>Agent: AI-generated response
    
    Agent->>Azure: Get conversation messages
    Azure-->>Agent: Full conversation history
    
    Agent->>Azure: Get run steps and tool calls
    Azure-->>Agent: Detailed execution logs
    
    Agent->>Azure: Get token usage statistics
    Azure-->>Agent: Usage metrics
    
    Note over Agent: Cleanup and Response Formatting
    Agent->>Azure: Delete agent (cleanup)
    Azure-->>Agent: Cleanup confirmation
    
    Agent->>Agent: Format structured response
    Agent-->>UI: Complete response object
    
    UI->>UI: Update session state with results
    UI->>UI: Format response for display
    UI-->>User: Display comprehensive results
```

### 2. Error Handling Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Agent as adf_agent()
    participant Functions as Function Tools
    participant ADF as Azure Data Factory API
    participant Auth as Azure Authentication
    
    User->>UI: Enter query
    UI->>Agent: adf_agent(query)
    
    Agent->>Functions: adf_pipeline_runs("NonExistentPipeline")
    Functions->>Auth: Request authentication token
    
    alt Authentication Success
        Auth-->>Functions: Valid token
        Functions->>ADF: Query pipeline runs
        
        alt ADF API Success
            ADF-->>Functions: Pipeline data or empty result
            Functions-->>Agent: Formatted response
            
        else ADF API Error
            ADF-->>Functions: Error response (400/404/500)
            Functions->>Functions: Process error response
            Functions-->>Agent: Error description with guidance
        end
        
    else Authentication Failure
        Auth-->>Functions: Authentication error
        Functions->>Functions: Handle auth error
        Functions-->>Agent: Authentication guidance
    end
    
    Agent->>Agent: Process tool response
    
    alt Tool Response Success
        Agent-->>UI: Successful response
        UI-->>User: Display results
        
    else Tool Response Error
        Agent-->>UI: Error response with guidance
        UI->>UI: Format error for display
        UI-->>User: Display error with help information
    end
```

### 3. Multi-Tool Orchestration Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent as adf_agent()
    participant Azure as Azure AI
    participant Functions as Function Tools
    participant MCP as MCP Server
    participant Learn as Microsoft Learn
    participant ADF as Data Factory API
    
    Note over User,ADF: Complex Query Requiring Multiple Tools
    
    User->>Agent: "How do I troubleshoot the CustomerETL pipeline failure?"
    
    Agent->>Azure: Create agent run with query
    Azure->>Azure: Analyze query intent
    Azure-->>Agent: Requires both Function and MCP tools
    
    Note over Agent,ADF: Phase 1: Get Current Status
    Agent->>Functions: adf_pipeline_runs("CustomerETL")
    Functions->>ADF: Query pipeline status
    ADF-->>Functions: Pipeline failure status
    Functions-->>Agent: Pipeline failed with error code
    
    Note over Agent,ADF: Phase 2: Get Detailed Diagnostics
    Agent->>Functions: adf_pipeline_activity_runs(runId)
    Functions->>ADF: Query activity details
    ADF-->>Functions: Activity failure details
    Functions-->>Agent: Specific activity errors
    
    Note over Agent,Learn: Phase 3: Get Documentation
    Agent->>MCP: Request tool execution approval
    Agent->>MCP: Query troubleshooting documentation
    MCP->>Learn: Search for error code documentation
    Learn-->>MCP: Troubleshooting guide content
    MCP-->>Agent: Formatted documentation
    
    Note over Azure: AI Processing & Response Generation
    Azure->>Azure: Combine data sources
    Azure->>Azure: Generate comprehensive response
    Azure-->>Agent: Integrated troubleshooting guide
    
    Agent-->>User: Complete troubleshooting response with:
    Note over Agent: - Current failure status
    Note over Agent: - Specific error details  
    Note over Agent: - Official documentation
    Note over Agent: - Recommended resolution steps
```

### 4. Session State Management Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Session as Session State
    participant Agent as adf_agent()
    participant Storage as Browser Storage
    
    Note over User,Storage: Session Lifecycle Management
    
    User->>UI: First access to application
    UI->>Session: Initialize session_state
    Session->>Session: Create empty history []
    Session->>Storage: Store session data
    
    User->>UI: Enter first query
    UI->>Agent: Process query
    Agent-->>UI: Return response object
    
    UI->>Session: Append response to history
    Session->>Session: Update session_state.history
    Session->>Storage: Persist updated state
    
    UI->>UI: Display results in panels
    UI->>UI: Update summary panel
    UI->>UI: Update details panel
    
    loop Additional Queries
        User->>UI: Enter follow-up query
        UI->>Agent: Process with context
        Agent-->>UI: Context-aware response
        UI->>Session: Append to history
        Session->>Storage: Persist state
        UI->>UI: Update display
    end
    
    alt User Clears History
        User->>UI: Click "Clear History" button
        UI->>Session: Reset history to []
        Session->>Storage: Clear stored data
        UI->>UI: Reset panels to empty state
        UI-->>User: Fresh session ready
        
    else Session Timeout
        Storage->>Session: Session timeout detected
        Session->>UI: Clear session data
        UI->>UI: Reset to initial state
        UI-->>User: Session expired message
    end
```

### 5. Real-Time Monitoring Sequence

```mermaid
sequenceDiagram
    participant Ops as Operations Engineer
    participant Dashboard as stadfops.py
    participant Monitor as Monitoring System
    participant Agent as adf_agent()
    participant ADF as Data Factory
    
    Note over Ops,ADF: Continuous Operations Monitoring
    
    Ops->>Dashboard: Access operational dashboard
    Dashboard->>Agent: Initialize monitoring session
    
    loop Continuous Monitoring
        Monitor->>Dashboard: Pipeline status change detected
        Dashboard->>Agent: Query updated pipeline status
        Agent->>ADF: Get current pipeline states
        ADF-->>Agent: Real-time status data
        Agent-->>Dashboard: Formatted status update
        Dashboard->>Dashboard: Update dashboard display
        
        alt Critical Failure Detected
            Dashboard->>Dashboard: Highlight critical alert
            Dashboard->>Ops: Display urgent notification
            Ops->>Dashboard: Investigate failure
            Dashboard->>Agent: Deep dive analysis request
            Agent->>ADF: Get detailed failure information
            ADF-->>Agent: Comprehensive failure data
            Agent-->>Dashboard: Analysis with recommendations
            Dashboard-->>Ops: Present investigation results
            
        else Normal Operations
            Dashboard->>Dashboard: Update status indicators
            Dashboard->>Dashboard: Refresh metrics
        end
    end
    
    Note over Ops,ADF: Proactive Issue Prevention
    Agent->>Agent: Analyze performance trends
    Agent->>Agent: Detect potential issues
    
    alt Potential Issue Detected
        Agent-->>Dashboard: Predictive alert
        Dashboard-->>Ops: Proactive notification
        Ops->>Dashboard: Request prevention guidance
        Dashboard->>Agent: Generate prevention plan
        Agent-->>Dashboard: Prevention recommendations
        Dashboard-->>Ops: Present prevention strategy
    end
```

## User Experience Patterns

### 1. Progressive Disclosure Pattern

```mermaid
flowchart TD
    InitialQuery[User Query] --> BasicResponse[Basic Response Display]
    BasicResponse --> UserReview{User Reviews Response}
    
    UserReview -->|Satisfied| EndFlow[End of Flow]
    UserReview -->|Needs More Detail| RequestDetail[Request More Details]
    
    RequestDetail --> ExpandedView[Show Expanded Information]
    ExpandedView --> TechnicalDetails[Technical Details Available]
    
    TechnicalDetails --> ExpertMode{Expert Mode?}
    ExpertMode -->|Yes| FullDiagnostics[Show Full Diagnostics]
    ExpertMode -->|No| GuidedAnalysis[Show Guided Analysis]
    
    FullDiagnostics --> EndFlow
    GuidedAnalysis --> FollowUpOptions[Present Follow-up Options]
    FollowUpOptions --> EndFlow
```

### 2. Context-Aware Assistance Pattern

```mermaid
flowchart TD
    UserQuery[User Query] --> ContextAnalysis[Analyze Query Context]
    ContextAnalysis --> HistoryCheck[Check Session History]
    
    HistoryCheck --> HasContext{Previous Context?}
    HasContext -->|Yes| ContextualResponse[Generate Contextual Response]
    HasContext -->|No| StandardResponse[Generate Standard Response]
    
    ContextualResponse --> ReferenceHistory[Reference Previous Queries]
    ReferenceHistory --> EnhancedResponse[Enhanced Response with Context]
    
    StandardResponse --> NewContext[Establish New Context]
    NewContext --> BaselineResponse[Baseline Response]
    
    EnhancedResponse --> ContinuityOptions[Provide Continuity Options]
    BaselineResponse --> ContextOptions[Establish Context Options]
    
    ContinuityOptions --> NextQuery[Ready for Next Query]
    ContextOptions --> NextQuery
```

### 3. Error Recovery Pattern

```mermaid
flowchart TD
    Error[Error Detected] --> ErrorType{Error Classification}
    
    ErrorType -->|Authentication| AuthRecovery[Authentication Recovery]
    ErrorType -->|Permission| PermRecovery[Permission Recovery]
    ErrorType -->|Network| NetworkRecovery[Network Recovery]
    ErrorType -->|Data| DataRecovery[Data Recovery]
    
    AuthRecovery --> AuthSteps[Display Auth Steps]
    PermRecovery --> PermSteps[Display Permission Steps]
    NetworkRecovery --> NetworkSteps[Display Network Steps]
    DataRecovery --> DataSteps[Display Data Steps]
    
    AuthSteps --> RetryOption[Provide Retry Option]
    PermSteps --> ContactOption[Provide Contact Option]
    NetworkSteps --> DiagnosticOption[Provide Diagnostic Option]
    DataSteps --> AlternativeOption[Provide Alternative Option]
    
    RetryOption --> UserAction[User Takes Action]
    ContactOption --> UserAction
    DiagnosticOption --> UserAction
    AlternativeOption --> UserAction
    
    UserAction --> SuccessCheck{Recovery Successful?}
    SuccessCheck -->|Yes| NormalOperation[Resume Normal Operation]
    SuccessCheck -->|No| EscalationPath[Escalation Path]
```

These comprehensive user flows and sequence diagrams provide a detailed blueprint for understanding how users interact with the Azure Data Factory Operations Agent and how the system processes and responds to operational requirements.