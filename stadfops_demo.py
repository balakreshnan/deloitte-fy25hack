import datetime
import os, time, json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple mock functions for demonstration
def adf_pipeline_runs(pipelinename: str = "processELT") -> str:
    """Mock function to simulate Azure Data Factory pipeline runs query"""
    # Return mock data for demonstration
    mock_data = {
        "pipelineName": pipelinename,
        "runId": "abc123-def456-789",
        "status": "Failed" if "failed" in pipelinename.lower() else "Succeeded",
        "runStart": "2024-01-15T09:30:00Z",
        "runEnd": "2024-01-15T09:45:00Z",
        "message": "Pipeline execution completed with errors" if "failed" in pipelinename.lower() else "Pipeline execution completed successfully"
    }
    return json.dumps(mock_data, indent=2)

def adf_pipeline_activity_runs(pipeline_run_id: str = "abc123-def456-789") -> str:
    """Mock function to simulate Azure Data Factory activity runs query"""
    # Return mock activity data for demonstration
    mock_activities = [
        {
            "activityName": "CopyCustomerData",
            "activityType": "Copy",
            "status": "Succeeded",
            "activityRunStart": "2024-01-15T09:30:00Z",
            "activityRunEnd": "2024-01-15T09:35:00Z"
        },
        {
            "activityName": "TransformData",
            "activityType": "ExecuteDataFlow",
            "status": "Failed" if "failed" in pipeline_run_id.lower() else "Succeeded",
            "activityRunStart": "2024-01-15T09:35:00Z",
            "activityRunEnd": "2024-01-15T09:45:00Z",
            "error": {
                "errorCode": "2200",
                "message": "Data transformation failed due to schema mismatch"
            } if "failed" in pipeline_run_id.lower() else None
        }
    ]
    return json.dumps(mock_activities, indent=2)

def adf_agent(query: str) -> dict:
    """Mock agent function for demonstration purposes"""
    logs = []
    def log(msg):
        logs.append(msg)
        print(msg)
    
    log(f"Processing query: {query}")
    
    # Simple keyword-based response generation for demonstration
    if "failed" in query.lower() or "error" in query.lower():
        pipeline_data = adf_pipeline_runs("CustomerETL-Failed")
        activity_data = adf_pipeline_activity_runs("failed-run-123")
        summary = f"Analysis shows pipeline failure in CustomerETL. The TransformData activity failed due to schema mismatch. Error code 2200 indicates data transformation issues."
    elif "status" in query.lower() or "running" in query.lower():
        pipeline_data = adf_pipeline_runs("CustomerETL")
        activity_data = adf_pipeline_activity_runs("abc123-def456-789")
        summary = f"Pipeline CustomerETL completed successfully. All activities executed without errors."
    else:
        pipeline_data = adf_pipeline_runs("GeneralPipeline")
        activity_data = ""
        summary = f"Here's the information about your Azure Data Factory pipelines. You can ask about specific pipeline status, failures, or activity details."
    
    # Mock tool calls for demonstration
    tool_calls = [
        {
            "id": "call_123",
            "type": "function",
            "name": "adf_pipeline_runs",
            "arguments": {"pipelinename": "CustomerETL"},
            "output": pipeline_data
        }
    ]
    
    if activity_data:
        tool_calls.append({
            "id": "call_456",
            "type": "function", 
            "name": "adf_pipeline_activity_runs",
            "arguments": {"pipeline_run_id": "abc123-def456-789"},
            "output": activity_data
        })
    
    log("Mock agent processing completed")
    
    return {
        "summary": summary,
        "details": "\n".join(logs),
        "messages": [
            {"role": "user", "content": query},
            {"role": "assistant", "content": summary}
        ],
        "steps": [
            {
                "id": "step_1",
                "status": "completed",
                "tool_calls": tool_calls,
                "outputs": [pipeline_data, activity_data] if activity_data else [pipeline_data]
            }
        ],
        "token_usage": {
            "prompt_tokens": 150,
            "completion_tokens": 200,
            "total_tokens": 350
        },
        "status": "completed",
        "query": query,
    }

def _inject_css():
    css = """
    <style>
    html, body, [data-testid='stAppViewContainer'] {height:100vh; overflow:hidden; background:#f5f7fa !important; color:#111;}
    .stChatInput {position:fixed; bottom:0; left:0; right:0; z-index:1000; background:#ffffff !important; padding:0.4rem 0.75rem; border-top:1px solid #d0d4d9; box-shadow:0 -2px 4px rgba(0,0,0,0.06);}        
    .block-container {padding-top:0.4rem; padding-bottom:6rem;}
    /* Scrollable panels */
    .summary-box, .details-scroll {border:1px solid #d9dde2; border-radius:8px; background:#ffffff; box-shadow:0 1px 2px rgba(0,0,0,0.04);}        
    .summary-box {font-size:0.9rem; line-height:1.2rem; height:520px; overflow-y:auto; padding:0.75rem; color:#111;}
    .details-scroll {height:520px; overflow-y:auto; padding:0.55rem 0.6rem 0.8rem 0.6rem;}
    .details-conv {font-size:0.7rem; line-height:1.05rem; font-family: var(--font-mono, monospace); margin-bottom:0.5rem;}
    .details-conv .msg {margin-bottom:4px;}
    .details-conv .role {color:#555;}
    .summary-box::-webkit-scrollbar, .details-scroll::-webkit-scrollbar {width:8px;}
    .summary-box::-webkit-scrollbar-thumb, .details-scroll::-webkit-scrollbar-thumb {background:#c3c9d1; border-radius:4px;}
    .metric-badge {display:inline-block; background:#eef2f6; color:#222; padding:4px 8px; margin:2px 4px 4px 0; border-radius:6px; font-size:0.65rem; border:1px solid #d0d5da;}
    [data-testid='stAppViewContainer'] > .main {overflow:hidden;}
    h3, h4, h5 {color:#111 !important;}
    .top-bar {display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;}
    .clear-btn button {background:#fff !important; color:#333 !important; border:1px solid #c9ced4 !important;}
    .demo-notice {background:#fff3cd; border:1px solid #ffeaa7; color:#856404; padding:10px; border-radius:6px; margin-bottom:20px;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def ui_main():
    st.set_page_config(page_title="ADF Operations Agent", layout="wide")
    _inject_css()
    
    st.markdown("### Azure Data Factory Operations Agent")
    
    # Demo notice
    st.markdown("""
    <div class="demo-notice">
    <strong>📋 Demo Mode:</strong> This is a demonstration of the stadfops.py interface with mock data. 
    In production, this connects to real Azure Data Factory APIs for live operational monitoring.
    </div>
    """, unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    # Optional top bar actions
    bar_col1, bar_col2 = st.columns([0.8, 0.2])
    with bar_col2:
        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    container = st.container(height=600)
    with container:
        col1, col2 = st.columns(2, gap="medium")
        latest = st.session_state.history[-1] if st.session_state.history else None

        with col1:
            st.markdown("**Summary**")
            with st.container(height=520, border=True):
                if latest:
                    user_q = latest.get('query','')
                    summary_html = f"<strong>Question:</strong> {user_q}<hr style='margin:6px 0;'>" + (latest['summary'] or '')
                    st.markdown(f"<div class='summary-box'>{summary_html}</div>", unsafe_allow_html=True)
                else:
                    st.info("Ask a question below to see operational analysis.")
                    
                # Example queries
                st.markdown("**💡 Try these example queries:**")
                st.code("""• "What's the status of CustomerETL pipeline?"
• "Why did the pipeline fail?"  
• "Show me activity details for the last run"
• "What pipelines are currently running?"
• "Tell me about data factory operations"
""")
                    
                if latest and latest.get("token_usage"):
                    tu = latest["token_usage"]
                    badges = "".join(
                        f"<span class='metric-badge'>{k}: {v}</span>" for k, v in tu.items()
                    )
                    st.markdown(badges, unsafe_allow_html=True)
                elif latest:
                    st.caption("Token usage: N/A")

        with col2:
            st.markdown("**Details**")
            if latest:
                # Scrollable container to hold expanders
                with st.container(height=520, border=True):
                    # Final assistant response
                    with st.expander("Final Assistant Response", expanded=True):
                        st.write(latest.get('summary') or '')

                    # Conversation messages
                    with st.expander("Conversation Messages", expanded=False):
                        for m in latest.get('messages', []):
                            role = (m.get('role') or '?').title()
                            content = m.get('content') or ''
                            st.markdown(f"**{role}:** {content}")

                    # Steps & tool calls
                    with st.expander("Steps & Tool Calls", expanded=True):
                        for sidx, s in enumerate(latest.get('steps', []), start=1):
                            step_header = f"Step {s.get('id') or sidx} • {s.get('status')}"
                            with st.expander(step_header, expanded=False):
                                # Step level aggregated outputs
                                step_outputs = s.get('outputs') or []
                                if step_outputs:
                                    with st.expander("Step Outputs", expanded=False):
                                        for oidx, otext in enumerate(step_outputs, start=1):
                                            st.code(otext, language="json")
                                # Tool calls
                                for tcidx, tc in enumerate(s.get('tool_calls', []) or [], start=1):
                                    tc_title = f"ToolCall {tcidx}: {tc.get('name') or tc.get('type') or 'tool'}"
                                    with st.expander(tc_title, expanded=False):
                                        meta = {k: tc.get(k) for k in ['id','type','name'] if tc.get(k)}
                                        if meta:
                                            st.caption("Metadata")
                                            st.json(meta)
                                        # Arguments
                                        args_raw = tc.get('arguments')
                                        if args_raw:
                                            st.caption("Arguments")
                                            if isinstance(args_raw, (dict, list)):
                                                st.json(args_raw)
                                            else:
                                                try:
                                                    parsed = json.loads(args_raw)
                                                    st.json(parsed)
                                                except Exception:
                                                    st.code(str(args_raw)[:4000])
                                        # Output
                                        out_raw = tc.get('output')
                                        if out_raw is not None:
                                            st.caption("Output")
                                            if isinstance(out_raw, (dict, list)):
                                                st.json(out_raw)
                                            else:
                                                text_out = str(out_raw)
                                                if len(text_out) > 6000:
                                                    st.text(text_out[:6000] + '... [truncated]')
                                                else:
                                                    st.code(text_out, language="json")
                    # Debug logs
                    with st.expander("Debug Logs", expanded=False):
                        dbg = latest.get('details') or ''
                        if dbg:
                            st.code(dbg[-15000:], language='text')
                        else:
                            st.caption("No debug logs available.")
            else:
                st.caption("**Operational details will appear here:**")
                st.caption("• Pipeline execution steps")
                st.caption("• Azure Data Factory API calls")  
                st.caption("• Tool outputs and diagnostics")
                st.caption("• Full conversation history")
                st.caption("• Debug logs and troubleshooting info")

    # Chat input fixed at bottom
    user_query = st.chat_input("Ask about Azure Data Factory operations...")
    if user_query:
        with st.spinner("Processing operational query...", show_time=True):
            result = adf_agent(user_query)
        st.session_state.history.append(result)
        st.rerun()

if __name__ == "__main__":
    ui_main()