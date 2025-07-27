import requests
import logging
from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def get_session_id(tool_context: ToolContext) -> str:
    """
    Initializes a new MCP session by calling the 'initialize' method on the MCP server.
    Returns the 'Mcp-Session-Id' from the response headers.
    """

    # Debug: Log current session state and caller context
    logger.info("[DEBUG] get_session_id called!")
    logger.info(f"[DEBUG] Current tool_context.state: {tool_context.state}")
    import traceback
    stack = traceback.format_stack()
    logger.info("[DEBUG] Call stack:\n" + "".join(stack))

    # ✅ STEP 0: Check if session already exists
    existing_session = tool_context.state.get("mcp_session_id")
    if existing_session:
        logger.info(f"🟢 Existing MCP session found: {existing_session}. Skipping login.")
        return f"User is already logged in with session: {existing_session}"

    # 🔁 If not found, create new session
    try:
        logger.info("🔍 Creating new MCP session...")
        url = "http://localhost:8080/mcp/"
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {}
        }
        headers = {
            "Content-Type": "application/json"
        }

        logger.info("Sending MCP initialization request...")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            session_id = response.headers.get("Mcp-Session-Id")
            tool_context.state["session_id"] = session_id
            if session_id:
                logger.info(f"✅ MCP session initialized. Session ID: {session_id}")
                tool_context.state["mcp_session_id"] = session_id
                return session_id
            else:
                logger.error("❌ MCP session ID not found in headers.")
                return "Error: MCP session ID missing in response headers."
        else:
            error_msg = f"❌ MCP initialization failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    except Exception as e:
        logger.exception("❌ Exception occurred while initializing MCP session.")
        return f"Exception: {str(e)}"

 