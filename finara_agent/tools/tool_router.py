import requests
import logging
from google.adk.tools import FunctionTool, ToolContext
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def call_tool_by_name(tool_name: str, tool_context: ToolContext, args: dict) -> str:
    """
    Dynamically calls an MCP tool based on the provided tool name using the session ID from tool_context.
    """
    logger.info(f"🔐 fetched tool name: {tool_name}")

    # PRIORITY ORDER FOR SESSION ID:
    # 1. Look for mcp_session_id in tool_context.state (main session state)
    # 2. Look for session_id in tool_context.state (fallback)
    # 3. Error if none found

    session_id = tool_context.state.get("mcp_session_id")
    if session_id:
        logger.info(f"🔐 Using mcp_session_id from context: {session_id}")
    else:
        if session_id:
            logger.info(f"🔐 Using session_id from context: {session_id}")
    
    logger.info(f"🔐 Final Retrieved session ID: {session_id}")
    
    if not session_id:
        logger.error("❌ Session ID missing. Please initialize the session first.")
        return {"error": "Session ID not found. Please initialize the session."}
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "args": args if args else {}
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": session_id
        }

        logger.info(f"📡 Sending request to MCP:\nHeaders: {headers}\nPayload: {json.dumps(payload, indent=2)}")

        response = requests.post("http://localhost:8080/mcp/stream", headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json().get("result")
            logger.info("✅ Successfully received data from MCP.")
            return result  # returning as-is, per your requirement
        else:
            logger.error(f" MCP returned {response.status_code}: {response.text}")
            return {"error": f"{response.status_code} - {response.text}"}

    except Exception as e:
        logger.exception("💥 Exception during MCP call.")
        return {"error": str(e)}

