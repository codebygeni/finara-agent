from google.adk.agents import ParallelAgent
import logging
 
from . import prompt
from finara_agent.sub_agents.credit_card_agent.agent import get_credit_card_agent
from finara_agent.sub_agents.epf_agent.agent import get_epf_agent
from finara_agent.sub_agents.equity_agent.agent import get_equity_agent
from finara_agent.sub_agents.mf_agent.agent import get_mf_agent
from finara_agent.sub_agents.net_worth_agent.agent import get_net_worth_agent
from finara_agent.sub_agents.spending_insights_agent.agent import get_spending_insights_agent
 
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)
 
def get_fall_back_queries_agent(session):
    logger.info("Initializing fallback agent with parallel sub-agents...")
    sub_agents = []
 
    agents_to_init = {
        "credit_card": get_credit_card_agent(session),
        "epf": get_epf_agent(session),
        "equity": get_equity_agent(session),
        "mf": get_mf_agent(session),
        "net_worth": get_net_worth_agent(session),
        "spending_insights": get_spending_insights_agent(session)
    }
 
    for name, agent_instance in agents_to_init.items():
        try:
            sub_agents.append(agent_instance)
            logger.info(f"Successfully initialized {name} agent: {agent_instance.name}")
        except Exception as e:
            logger.error(f"Failed to initialize {name} agent: {e}")
 
    if not sub_agents:
        logger.warning("No sub-agents were successfully initialized for the fallback agent.")
        # Depending on your system, you might want to raise an error or return None/a special agent here.
 
    logger.info("Fallback sub-agents: %s", [agent.name for agent in sub_agents])
 
    return ParallelAgent(
        name="get_fall_back_queries_agent",
        description="Handles fallback queries using parallel financial agents.",
        sub_agents=sub_agents
    )
 