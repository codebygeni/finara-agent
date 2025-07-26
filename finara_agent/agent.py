"""Financial coordinator: provide comprehensive financial insights and management"""
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.sessions import InMemorySessionService, Session
import vertexai
from vertexai import agent_engines
from . import prompt
from .sub_agents.credit_card_agent.agent import get_credit_card_agent
from .sub_agents.epf_agent.agent import get_epf_agent
from .sub_agents.equity_agent.agent import get_equity_agent
from .sub_agents.mf_agent.agent import get_mf_agent
from .sub_agents.net_worth_agent.agent import get_net_worth_agent
from .sub_agents.spending_insights_agent.agent import get_spending_insights_agent
from .sub_agents.fall_back_agent.agent import get_fall_back_queries_agent
from finara_agent.tools.get_session_id import get_session_id
from dotenv import load_dotenv

MODEL = "gemini-2.0-flash"
 
def get_finara_coordinator(session):
    return Agent(
        name="finara_coordinator",
        model=MODEL,
        description=(
            "first always check authentication status and session id, if it is not present call 'get_session_id' tool. "
            "Guide users through comprehensive financial management by orchestrating a series of expert subagents. "
            "Help them analyze investments, track spending, monitor credit, optimize taxes, plan for retirement, and more. "
            "Route to get_fall_back_queries_agent if query is broad, exploratory, or related to general financial advice, "
            "government queries, or unrelated financial topics like 'how to apply for a PAN card' or 'can I get a loan of 50 lakhs'."
        ),
        instruction=prompt.FINARA_ROOT_PROMPT,
        output_key="finara_coordinator_output",
        tools=[
            AgentTool(agent=get_credit_card_agent(session)),
            AgentTool(agent=get_epf_agent(session)),
            AgentTool(agent=get_equity_agent(session)),
            AgentTool(agent=get_mf_agent(session)),
            AgentTool(agent=get_net_worth_agent(session)),
            AgentTool(agent=get_spending_insights_agent(session)),
            AgentTool(agent=get_fall_back_queries_agent(session)),
            get_session_id,
        ],
    )
session_service = InMemorySessionService()
session = session_service.create_session(user_id="21", app_name=os.getenv("APP_NAME", "finara_coordinator"))

finara_agent_instance = get_finara_coordinator(session)

load_dotenv()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket="gs://geni-project_cloudbuild",
)

remote_app = agent_engines.create(
    display_name=os.getenv("APP_NAME", "finara_coordinator"),
    agent_engine=finara_agent_instance,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "cloudpickle==3.1.1"
    ]
)
 
 