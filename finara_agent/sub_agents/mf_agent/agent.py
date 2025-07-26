from google.adk.agents import Agent
from . import prompt
from finara_agent.tools.tool_router import call_tool_by_name
from finara_agent.tools.tool_list_metadata import dynamic_mcp_tool
from finara_agent.tools.get_session_id import get_session_id
 

MODEL = "gemini-2.5-pro"

def get_mf_agent(session):
    instruction = f"{prompt.MF_AGENT_PROMPT}\n"
    return Agent(
        model=MODEL,
        name="mf_agent",
        description="Mutual Fund analysis agent",
        output_key="mf_agent_output",
        instruction=instruction,
        tools=[call_tool_by_name,dynamic_mcp_tool,get_session_id]
    )