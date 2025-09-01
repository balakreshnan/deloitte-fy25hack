import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)
from azure.ai.agents.models import CodeInterpreterTool
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
model_endpoint = os.environ["MODEL_ENDPOINT"] # Sample : https://<account_name>.services.ai.azure.com
model_api_key= os.environ["MODEL_API_KEY"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"] # Sample : gpt-4o-mini

# Get MCP server configuration from environment variables
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "MicrosoftLearn")

# Create the project client (Foundry project and credentials)
project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
)

client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2024-10-21",
)

def adf_agent(query: str) -> dict:
    """Run the agent and return structured info for UI.

    Returns dict keys:
      summary: short textual summary (final assistant reply)
      details: verbose log (steps + messages + approvals)
      messages: list of {role, content}
      token_usage: dict or None
      status: run final status
    """
    logs = []
    def log(msg):
        logs.append(msg)
        print(msg)

    mcp_tool = McpTool(
        server_label=mcp_server_label,
        server_url=mcp_server_url,
        allowed_tools=[],
    )

    final_assistant = ""
    token_usage = None
    status = "unknown"
    messages_list = []
    steps_list = []  # structured step data

    code_interpreter = CodeInterpreterTool()

    with project_client:
        agents_client = project_client.agents
        # Both mcp_tool.definitions and code_interpreter.definitions are (likely) lists.
        # Earlier code passed a list of those lists producing a nested array -> service error:
        #   (UserError) 'tools' must be an array of objects
        # Flatten them so the service receives a flat list of tool definition objects.
        def _ensure_list(v):
            return v if isinstance(v, list) else [v]
        tool_definitions = _ensure_list(mcp_tool.definitions) + _ensure_list(code_interpreter.definitions)
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="adf-mcp-agent",
            instructions="""You are a helpful agent that can use MCP tools to assist users. 
            Use the available MCP tools to answer questions and perform tasks.
            Get the implementation document for Azure Data Factory operations using MCP tools and
            execute using code interpreter tool to execute.""",
            tools=tool_definitions,
            tool_resources=code_interpreter.resources,
        )
        log(f"Registered {len(tool_definitions)} tool definitions")
        log(f"Agent: {agent.id} | MCP: {mcp_tool.server_label}")
        thread = agents_client.threads.create()
        log(f"Thread: {thread.id}")
        agents_client.messages.create(thread_id=thread.id, role="user", content=query)
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources)
        log(f"Run: {run.id}")

        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(0.8)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
            if run.status == "requires_action" and isinstance(run.required_action, SubmitToolApprovalAction):
                tool_calls = run.required_action.submit_tool_approval.tool_calls or []
                if not tool_calls:
                    log("No tool calls – cancelling run")
                    agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                    break
                approvals = []
                for tc in tool_calls:
                    if isinstance(tc, RequiredMcpToolCall):
                        log(f"Approving tool call {tc.id}")
                        approvals.append(ToolApproval(tool_call_id=tc.id, approve=True, headers=mcp_tool.headers))
                if approvals:
                    agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_approvals=approvals)
            log(f"Status: {run.status}")

        status = run.status
        if status == "failed":
            log(f"Run failed: {run.last_error}")

        # Steps (collect structured info)
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            sid = step.get('id')
            sstatus = step.get('status')
            sd = step.get("step_details", {})
            tool_calls_raw = []
            if isinstance(sd, dict):
                tool_calls_raw = sd.get("tool_calls", []) or []
            structured_tool_calls = []
            for call in tool_calls_raw:
                # Safely extract fields
                structured_tool_calls.append({
                    "id": call.get('id'),
                    "type": call.get('type'),
                    "name": call.get('name') if isinstance(call, dict) else getattr(call, 'name', None),
                    "arguments": call.get('arguments') if isinstance(call, dict) else getattr(call, 'arguments', None),
                    "output": call.get('output') if isinstance(call, dict) else getattr(call, 'output', None),
                })
                log(f"Step {sid} tool_call {call.get('id')} type={call.get('type')}")
            # Activity tools definitions (for required actions)
            activity_tools = []
            if isinstance(sd, RunStepActivityDetails):
                for activity in sd.activities:
                    for fname, fdef in activity.tools.items():
                        activity_tools.append({
                            "function": fname,
                            "description": fdef.description,
                            "parameters": list(getattr(getattr(fdef, 'parameters', None), 'properties', {}).keys()) if getattr(fdef, 'parameters', None) else [],
                        })
                        log(f"Activity tool def: {fname}")
            steps_list.append({
                "id": sid,
                "status": sstatus,
                "tool_calls": structured_tool_calls,
                "activity_tools": activity_tools,
            })
            log(f"Step {sid} [{sstatus}] with {len(structured_tool_calls)} tool calls")

        # Messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for m in messages:
            content = ""
            if m.text_messages:
                content = m.text_messages[-1].text.value
            role = m.role
            if role == "assistant":
                final_assistant = content
            messages_list.append({"role": role, "content": content})

        # Token usage (if provided by SDK)
        usage = getattr(run, "usage", None)
        if usage:
            token_usage = {
                k: getattr(usage, k) for k in ["prompt_tokens", "completion_tokens", "total_tokens"] if hasattr(usage, k)
            } or None

        # Cleanup
        try:
            agents_client.delete_agent(agent.id)
        except Exception:
            pass

    summary = final_assistant or "No assistant response."
    details = "\n".join(logs)
    return {
        "summary": summary,
        "details": details,
        "messages": messages_list,
        "steps": steps_list,
        "token_usage": token_usage,
        "status": status,
    }

def _inject_css():
    css = """
    <style>
    html, body, [data-testid='stAppViewContainer'] {height:100vh; overflow:hidden; background:#f5f7fa !important; color:#111;}
    .stChatInput {position:fixed; bottom:0; left:0; right:0; z-index:1000; background:#ffffff !important; padding:0.4rem 0.75rem; border-top:1px solid #d0d4d9; box-shadow:0 -2px 4px rgba(0,0,0,0.06);}        
    .block-container {padding-top:0.4rem; padding-bottom:6rem;}
    /* Scrollable panels */
    .summary-box, .details-box {border:1px solid #d9dde2; border-radius:8px; background:#ffffff; box-shadow:0 1px 2px rgba(0,0,0,0.04);}        
    .summary-box {font-size:0.9rem; line-height:1.2rem; height:520px; overflow-y:auto; padding:0.75rem; color:#111;}
    .details-box {font-size:0.7rem; line-height:1.08rem; white-space:pre-wrap; font-family: var(--font-mono, monospace); height:520px; overflow-y:auto; padding:0.75rem; color:#222;}
    .summary-box::-webkit-scrollbar, .details-box::-webkit-scrollbar {width:8px;}
    .summary-box::-webkit-scrollbar-thumb, .details-box::-webkit-scrollbar-thumb {background:#c3c9d1; border-radius:4px;}
    .metric-badge {display:inline-block; background:#eef2f6; color:#222; padding:4px 8px; margin:2px 4px 4px 0; border-radius:6px; font-size:0.65rem; border:1px solid #d0d5da;}
    [data-testid='stAppViewContainer'] > .main {overflow:hidden;}
    h3, h4, h5 {color:#111 !important;}
    .top-bar {display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;}
    .clear-btn button {background:#fff !important; color:#333 !important; border:1px solid #c9ced4 !important;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def ui_main():
    st.set_page_config(page_title="ADF Agent", layout="wide")
    _inject_css()
    st.markdown("### Azure Data Factory Agent")

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
            if latest:
                st.markdown(f"<div class='summary-box'>{latest['summary']}</div>", unsafe_allow_html=True)
            else:
                st.info("Ask a question below to see a summary.")
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
                # Build rich HTML: messages + steps
                msg_html_parts = ["<div><strong>Conversation</strong><br>"]
                for m in latest.get("messages", []):
                    role = m.get('role','?').title()
                    content = (m.get('content') or '').replace('<','&lt;').replace('>','&gt;')
                    msg_html_parts.append(f"<div style='margin-bottom:4px;'><span style='color:#555;'>{role}:</span> {content}</div>")
                msg_html_parts.append("</div>")
                steps_html_parts = ["<div style='margin-top:0.75rem;'><strong>Steps & Tool Calls</strong><br>"]
                for s in latest.get("steps", []):
                    steps_html_parts.append(f"<div style='margin:4px 0; padding:4px 6px; background:#fafbfc; border:1px solid #e2e6ea; border-radius:4px;'>"
                                            f"<div style='font-size:0.65rem; letter-spacing:0.5px; color:#333;'><strong>Step {s['id']}</strong> • {s['status']}</div>")
                    # Tool calls
                    if s.get('tool_calls'):
                        for tc in s['tool_calls']:
                            steps_html_parts.append(
                                "<div style='margin-left:6px; font-size:0.6rem; padding:2px 0;'>"
                                f"<code>{tc.get('id') or 'tool'}</code> "
                                f"<span style='color:#555;'>{tc.get('type')}</span> "
                                f"<strong>{(tc.get('name') or '')}</strong>" \
                                f"{ ' args=' + str(tc.get('arguments')) if tc.get('arguments') else ''}" \
                                f"{ ' → ' + str(tc.get('output'))[:120] + ('…' if tc.get('output') and len(str(tc.get('output'))) > 120 else '') if tc.get('output') else ''}" \
                                "</div>"
                            )
                    # Activity tool definitions
                    if s.get('activity_tools'):
                        for at in s['activity_tools']:
                            steps_html_parts.append(
                                "<div style='margin-left:6px; font-size:0.6rem; padding:2px 0; color:#666;'>"
                                f"Def: <strong>{at['function']}</strong> – {at['description']}" +
                                (f" params: {', '.join(at['parameters'])}" if at['parameters'] else "") + "</div>"
                            )
                    steps_html_parts.append("</div>")
                steps_html_parts.append("</div>")
                combined_html = "<div class='details-box'>" + "".join(msg_html_parts + steps_html_parts) + "</div>"
                st.markdown(combined_html, unsafe_allow_html=True)
            else:
                st.caption("Details will appear here, including steps, tool calls, tool outputs, and full conversation.")

    # Chat input fixed at bottom
    user_query = st.chat_input("Ask about Azure Data Factory job status...")
    if user_query:
        with st.spinner("Running agent...", show_time=True):
            result = adf_agent(user_query)
        st.session_state.history.append(result)
        st.rerun()

if __name__ == "__main__":
    # query="How do i look up Azure data factory job status?"
    # result = adf_agent(query)
    # print("Results:", result)
    ui_main()
