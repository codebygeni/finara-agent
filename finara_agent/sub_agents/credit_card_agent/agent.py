from google.adk.agents import Agent
from . import prompt
from finara_agent.tools.tool_router import call_tool_by_name
from finara_agent.tools.tool_list_metadata import dynamic_mcp_tool
from finara_agent.tools.get_session_id import get_session_id

MODEL = "gemini-2.5-pro"

def get_credit_card_agent(session):
    instruction = f"{prompt.CREDIT_CARD_AGENT_PROMPT}\n"
    return Agent(
        model=MODEL,
        name="credit_card_agent",
        description="Credit Card analysis agent",
        output_key="credit_card_agent_output",
        instruction=instruction,
        tools=[call_tool_by_name,dynamic_mcp_tool,get_session_id]
    )