"""Gradio UI for Azure Data Factory Agent.

This file provides a Gradio-based interface separate from the Streamlit UI in stadf.py.
It relies on the adf_agent function defined in stadf.py to perform the agent run and
display both summarized output and detailed tool call / step information.
"""

from typing import List, Tuple
import gradio as gr
from stadf import adf_agent  # reuse existing logic

INTRO_TEXT = (
    "# Azure Data Factory Agent (Gradio)\n"
    "Ask about ADF job status. Left shows summarized assistant reply + token usage. "
    "Right shows full conversation, steps, tool calls, and outputs."
)


def format_details(agent_result: dict) -> str:
    if not agent_result:
        return "<em>No details yet.</em>"
    messages = agent_result.get("messages", [])
    steps = agent_result.get("steps", [])
    token_usage = agent_result.get("token_usage") or {}

    parts: list[str] = ["<div class='details-root'>"]
    # Conversation
    parts.append("<div class='section-title'>Conversation</div>")
    if messages:
        for m in messages:
            role_raw = m.get("role", "?")
            role = role_raw.title()
            content = (m.get("content") or "").replace("<", "&lt;").replace(">", "&gt;")
            role_cls = f"msg-role-{role_raw}"
            parts.append(
                f"<div class='message {role_cls}'>"
                f"<div class='message-role'>{role}</div>"
                f"<div class='message-content'>{content}</div>"
                "</div>"
            )
    else:
        parts.append("<div class='empty'>No messages.</div>")

    # Steps & tool calls
    parts.append("<div class='section-title'>Steps & Tool Calls</div>")
    if steps:
        for s in steps:
            sid = s.get('id')
            status = s.get('status')
            parts.append(f"<div class='step-card'><div class='step-header'>Step {sid} • {status}</div>")
            # Tool calls table
            tcs = s.get('tool_calls') or []
            if tcs:
                parts.append("<table class='tool-table'><thead><tr><th>ID</th><th>Type</th><th>Name</th><th>Args</th><th>Output</th></tr></thead><tbody>")
                for tc in tcs:
                    args_repr = ''
                    if tc.get('arguments'):
                        try:
                            args_repr = str(tc.get('arguments'))
                        except Exception:
                            args_repr = '[args error]'
                    output_repr = ''
                    if tc.get('output'):
                        out = str(tc.get('output'))
                        output_repr = out if len(out) < 120 else out[:120] + '…'
                    parts.append(
                        "<tr>" \
                        f"<td><code>{tc.get('id') or ''}</code></td>" \
                        f"<td>{tc.get('type') or ''}</td>" \
                        f"<td>{tc.get('name') or ''}</td>" \
                        f"<td><pre>{args_repr}</pre></td>" \
                        f"<td><pre>{output_repr}</pre></td>" \
                        "</tr>"
                    )
                parts.append("</tbody></table>")
            # Activity tool definitions
            acts = s.get('activity_tools') or []
            if acts:
                parts.append("<div class='activity-tools'>")
                for at in acts:
                    params = ', '.join(at.get('parameters') or [])
                    parts.append(
                        f"<div class='activity-tool'><span class='fname'>{at.get('function')}</span> – {at.get('description')}" +
                        (f" <span class='params'>(params: {params})</span>" if params else "") + "</div>"
                    )
                parts.append("</div>")
            parts.append("</div>")  # step-card
    else:
        parts.append("<div class='empty'>No steps.</div>")

    # Token usage inline (optional duplicate)
    if token_usage:
        parts.append("<div class='section-title small'>Token Usage</div>")
        parts.append("<div class='token-usage'>")
        for k, v in token_usage.items():
            parts.append(f"<span class='badge'>{k}: {v}</span>")
        parts.append("</div>")

    parts.append("</div>")
    return "".join(parts)


def format_summary(agent_result: dict) -> str:
    if not agent_result:
        return "<em>No summary yet.</em>"
    raw_summary = agent_result.get("summary") or "(empty)"
    # Escape angle brackets
    summary = raw_summary.replace("<", "&lt;").replace(">", "&gt;")
    token_usage = agent_result.get("token_usage") or {}
    status = (agent_result.get("status") or "").upper()
    status_badge = f"<span class='status-badge status-{status.lower()}'>{status}</span>" if status else ""
    badges = "".join([f"<span class='badge'>{k}: {v}</span>" for k, v in token_usage.items()]) or "<span class='empty'>No token data</span>"
    sections = [
        "<div class='summary-root'>",
        f"<div class='summary-header'><span class='summary-title'>Assistant Summary</span>{status_badge}</div>",
        f"<div class='summary-text'>{summary}</div>",
        "<div class='section-title small'>Token Usage</div>",
        f"<div class='summary-usage'>{badges}</div>",
        "</div>",
    ]
    return "".join(sections)


def chat_fn(message: str, history: List[Tuple[str, str]], state: dict):
    history = history or []
    if not message:
        return history, "<em>No summary yet.</em>", "<em>No details yet.</em>", state or {}
    history.append((message, ""))
    agent_result = adf_agent(message)
    reply = agent_result.get("summary") or "(no reply)"
    history[-1] = (message, reply)
    return history, format_summary(agent_result), format_details(agent_result), agent_result


with gr.Blocks(css="""
body, html {height:100vh; margin:0; padding:0; font-family: 'Segoe UI', Arial, sans-serif;}
#root {height:100vh; display:flex; flex-direction:column;}
.panels-wrapper {flex:1 1 auto; padding:8px 12px 128px 12px; box-sizing:border-box;}
.panels {display:flex; gap:12px; height:100%;}
.panel {flex:1 1 50%; border:1px solid #d9dde2; border-radius:10px; background:#fff; box-shadow:0 2px 4px rgba(0,0,0,0.06); padding:14px 14px 10px 14px; height:600px; overflow-y:auto; overflow-x:hidden;}
.panel::-webkit-scrollbar {width:10px;} .panel::-webkit-scrollbar-thumb {background:#c8ced5; border-radius:6px;}
.bottom {position:fixed; bottom:0; left:0; right:0; border-top:1px solid #d9dde2; background:#ffffff; padding:10px 14px 14px 14px; display:flex; gap:10px; align-items:flex-end; box-shadow:0 -3px 8px rgba(0,0,0,0.08);} 
#chatbox {flex:1; min-height:70px;}
.gradio-container {max-width:100% !important;}
@media (max-height:820px){ .panel {font-size:13px;} }
/* Custom styling */
.section-title {margin:12px 0 6px; font-weight:600; font-size:13px; letter-spacing:.5px; text-transform:uppercase; color:#333;}
.section-title.small {margin-top:16px;}
.message {border:1px solid #e3e7ea; border-radius:8px; padding:8px 10px; margin:6px 0; background:#fdfdfd; display:flex; flex-direction:column; gap:4px;}
.message-role {font-size:11px; font-weight:600; letter-spacing:.5px; text-transform:uppercase; color:#555;}
.msg-role-user {background:#eef6ff;}
.msg-role-assistant {background:#f4f9f2;}
.message-content {font-size:13px; line-height:1.25; white-space:pre-wrap;}
.step-card {border:1px solid #e2e6ea; border-radius:8px; padding:8px 10px; margin:10px 0; background:#fafbfc;}
.step-header {font-size:12px; font-weight:600; letter-spacing:.5px; color:#222; margin-bottom:4px;}
.tool-table {width:100%; border-collapse:collapse; margin:4px 0 6px; font-size:11px;}
.tool-table th {background:#f1f3f5; text-align:left; padding:4px 6px; border-bottom:1px solid #d9dde2; font-weight:600; font-size:11px;}
.tool-table td {border-bottom:1px solid #eceff1; padding:4px 6px; vertical-align:top;}
.tool-table tr:last-child td {border-bottom:none;}
.tool-table pre {margin:0; white-space:pre-wrap; word-break:break-word; font-family:monospace;}
.activity-tools {margin:4px 0;}
.activity-tool {font-size:11px; padding:2px 4px; border-left:3px solid #c3ccd5; background:#fff; margin:2px 0;}
.activity-tool .fname {font-weight:600;}
.badge {display:inline-block; background:#eef2f6; color:#222; padding:4px 8px; margin:2px 4px 2px 0; border-radius:20px; font-size:11px; border:1px solid #d0d5da;}
.empty {color:#777; font-style:italic;}
.token-usage {margin-top:4px;}
.summary-root {display:flex; flex-direction:column; gap:8px;}
.summary-header {display:flex; align-items:center; gap:10px;}
.summary-title {font-size:15px; font-weight:600; letter-spacing:.5px;}
.status-badge {display:inline-block; padding:4px 8px; border-radius:14px; font-size:10px; letter-spacing:.75px; font-weight:600; background:#eef2f6; border:1px solid #d0d5da; color:#333;}
.status-badge.status-failed {background:#ffecec; border-color:#f5b5b5; color:#b30000;}
.status-badge.status-completed, .status-badge.status-succeeded {background:#edf9f2; border-color:#b7e4c7; color:#176c35;}
.summary-text {font-size:14px; line-height:1.35; white-space:pre-wrap;}
.summary-usage {display:flex; flex-wrap:wrap;}
.details-root {font-size:13px; line-height:1.3;}
""", elem_id="root", title="ADF Agent Gradio") as demo:
    gr.Markdown(INTRO_TEXT)
    state = gr.State({})
    history = gr.State([])
    # Use a single Row instead of Box (for older Gradio versions without gr.Box)
    with gr.Row(elem_classes=["panels-wrapper", "panels"], equal_height=True):
        with gr.Column(scale=1, min_width=400):
            summary_html = gr.HTML(value="<em>No summary yet.</em>", elem_id="summary", elem_classes=["panel"])
        with gr.Column(scale=1, min_width=400):
            detail_html = gr.HTML(value="<em>No details yet.</em>", elem_id="details", elem_classes=["panel"])
    with gr.Row(elem_classes=["bottom"]):
        chat_in = gr.Textbox(label="Ask", placeholder="Ask about ADF job status…", lines=2, elem_id="chatbox")
        send_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear")

    chat_in.submit(chat_fn, inputs=[chat_in, history, state], outputs=[history, summary_html, detail_html, state])
    send_btn.click(chat_fn, inputs=[chat_in, history, state], outputs=[history, summary_html, detail_html, state])

    def clear_cb():
        return [], "<em>No summary yet.</em>", "<em>No details yet.</em>", {}
    clear_btn.click(clear_cb, outputs=[history, summary_html, detail_html, state])

    # Autofocus the textbox on load (Gradio uses 'js' not '_js')
    demo.load(None, None, None, js="document.getElementById('chatbox') && document.getElementById('chatbox').focus();")

if __name__ == "__main__":
    demo.queue().launch()