from google.adk.agents import Agent
from . import prompt
from finara_agent.tools.tool_router import call_tool_by_name
from finara_agent.tools.tool_list_metadata import dynamic_mcp_tool
from finara_agent.tools.get_session_id import get_session_id
 
MODEL = "gemini-2.5-pro"

def get_net_worth_agent(session):
    instruction = f"{prompt.NET_WORTH_AGENT_PROMPT}\n"
    return Agent(
        model=MODEL,
        name="net_worth_agent",
       description=(
        "Helps users with financial queries by invoking sub-agents for trading, tax, news, or fetching financial data."
    ),
        output_key="net_worth_agent_output",
        instruction=instruction,
        tools=[call_tool_by_name,dynamic_mcp_tool,get_session_id]
)