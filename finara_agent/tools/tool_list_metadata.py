import requests
import json
import logging
from google.adk.tools import FunctionTool, ToolContext

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def dynamic_mcp_tool(tool_name: str, tool_context: ToolContext) -> str:
    logger.info(f"Calling tool: {tool_name} with context type: {type(tool_context).__name__}")
    url = "http://localhost:8080/mcp/stream"

    headers = {
        "Content-Type": "application/json",
        "Mcp-Session-Id": "mcp-session-58fd765f-5ba3-4219-9cef-002aa723c2e4",
    }

    body = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1,
        "params": {
            "name": tool_name,
            "args": {}  
        }
    }

    # Print the request for debugging
    logger.debug("Sending request to MCP Server")
    logger.debug(f"URL: {url}")
    logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
    logger.debug(f"Body: {json.dumps(body, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        logger.debug("Received response from MCP Server")
        logger.debug(f"Status Code: {response.status_code}")
        logger.debug(f"Response JSON: {json.dumps(response.json(), indent=2)}")

        return json.dumps(response.json(), indent=2)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return f"Request failed: {str(e)}"


 

