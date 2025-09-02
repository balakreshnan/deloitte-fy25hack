import os, time, json
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

        # Steps (collect structured info including outputs)
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            sid = step.get('id') if isinstance(step, dict) else getattr(step, 'id', None)
            sstatus = step.get('status') if isinstance(step, dict) else getattr(step, 'status', None)
            sd = step.get("step_details", {}) if isinstance(step, dict) else getattr(step, 'step_details', {})
            tool_calls_raw = []
            if isinstance(sd, dict):
                tool_calls_raw = sd.get("tool_calls", []) or []
            elif hasattr(sd, 'tool_calls'):
                tool_calls_raw = getattr(sd, 'tool_calls') or []
            structured_tool_calls = []
            aggregated_step_outputs = []
            for call in tool_calls_raw:
                get = call.get if isinstance(call, dict) else lambda k, d=None: getattr(call, k, d)
                call_id = get('id')
                call_type = get('type')
                call_name = get('name')
                arguments = get('arguments')
                output_field = get('output')
                nested_outputs = []
                ci = get('code_interpreter')
                if ci and isinstance(ci, dict):
                    nested_outputs = ci.get('outputs') or []
                def _norm(o):
                    try:
                        if isinstance(o, (dict, list)):
                            return json.dumps(o, indent=2)[:8000]
                        return str(o)[:8000]
                    except Exception:
                        return str(o)[:8000]
                collected = []
                if output_field:
                    collected.append(_norm(output_field))
                for no in nested_outputs:
                    collected.append(_norm(no))
                if collected:
                    aggregated_step_outputs.extend(collected)
                structured_tool_calls.append({
                    "id": call_id,
                    "type": call_type,
                    "name": call_name,
                    "arguments": arguments,
                    "output": output_field,
                    "nested_outputs": nested_outputs,
                })
                log(f"Step {sid} tool_call {call_id} type={call_type}")
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
                "outputs": aggregated_step_outputs,
            })
            log(f"Step {sid} [{sstatus}] with {len(structured_tool_calls)} tool calls and {len(aggregated_step_outputs)} outputs")

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
    .panel-container {border:1px solid #d9dde2; border-radius:8px; background:#ffffff; padding:0.4rem 0.6rem 0.6rem; height:534px; overflow-y:auto; box-shadow:0 1px 2px rgba(0,0,0,0.04);}        
    .panel-container::-webkit-scrollbar {width:8px;}
    .panel-container::-webkit-scrollbar-thumb {background:#c3c9d1; border-radius:4px;}
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
            with st.container(height=534, border=True):
                if latest:
                    with st.expander("Final Assistant Response", expanded=True):
                        st.write(latest['summary'])
                    if latest.get("token_usage"):
                        tu = latest["token_usage"]
                        badges = " ".join(f"{k}: {v}" for k, v in tu.items())
                        st.caption(badges)
                    else:
                        st.caption("Token usage: N/A")
                else:
                    st.info("Ask a question below to see a summary.")

        with col2:
            st.markdown("**Details**")
            with st.container(height=534, border=True):
                if latest:
                    with st.expander("Conversation", expanded=False):
                        for m in latest.get("messages", []):
                            role = (m.get('role') or '?').title()
                            content = m.get('content') or ''
                            st.markdown(f"**{role}:** {content}")
                    with st.expander("Steps & Tool Calls", expanded=True):
                        for sidx, s in enumerate(latest.get('steps', []), start=1):
                            step_header = f"Step {s.get('id') or sidx} • {s.get('status')}"
                            with st.expander(step_header, expanded=False):
                                # Step outputs
                                step_outputs = s.get('outputs') or []
                                if step_outputs:
                                    with st.expander("Step Outputs", expanded=False):
                                        for oidx, otext in enumerate(step_outputs, start=1):
                                            st.code(otext, language="text")
                                # Tool calls
                                for tcidx, tc in enumerate(s.get('tool_calls', []) or [], start=1):
                                    tc_title = f"ToolCall {tcidx}: {tc.get('name') or tc.get('type') or 'tool'}"
                                    with st.expander(tc_title, expanded=False):
                                        meta = {k: tc.get(k) for k in ['id','type','name'] if tc.get(k)}
                                        if meta:
                                            st.caption("Metadata")
                                            st.json(meta)
                                        args_raw = tc.get('arguments')
                                        if args_raw:
                                            st.caption("Arguments")
                                            if isinstance(args_raw, (dict, list)):
                                                st.json(args_raw)
                                            else:
                                                try:
                                                    st.json(json.loads(args_raw))
                                                except Exception:
                                                    st.code(str(args_raw)[:4000])
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
                                                    st.text(text_out)
                                        nested = tc.get('nested_outputs') or []
                                        if nested:
                                            with st.expander("Nested Outputs", expanded=False):
                                                for nidx, n in enumerate(nested, start=1):
                                                    st.code(n if isinstance(n, str) else str(n), language="text")
                                atools = s.get('activity_tools') or []
                                if atools:
                                    with st.expander("Activity Tool Definitions", expanded=False):
                                        for at in atools:
                                            params = at.get('parameters') or []
                                            ptxt = f" (params: {', '.join(params)})" if params else ''
                                            st.markdown(f"- **{at.get('function')}**: {at.get('description')}{ptxt}")
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
