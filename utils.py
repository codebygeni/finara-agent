import json
from typing import Dict, Any
from datetime import datetime
from google.genai import types

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    OKGREEN = "\033[92m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Additional color shortcuts
    ENDC = RESET
    WARNING = YELLOW
    HEADER = MAGENTA

def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    """Add an entry to the interaction history in state.

    Args:
        session_service: The session service instance
        app_name: The application name
        user_id: The user ID
        session_id: The session ID
        entry: A dictionary containing the interaction data
            - requires 'action' key (e.g., 'user_query', 'agent_response')
            - other keys are flexible depending on the action type
    """
    try:
        # Try to get session with session_id only first (InMemorySessionService style)
        try:
            session = session_service.get_session(session_id)
        except:
            # Fallback to full parameters if needed
            session = session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

        # Get current interaction history
        interaction_history = session.state.get("interaction_history", [])
        
        # Debug: Print session info
        print(f"{Colors.MAGENTA}DEBUG: Session {session.id}, updating interaction_history{Colors.RESET}")
        print(f"{Colors.MAGENTA}DEBUG: Current history length: {len(interaction_history)}{Colors.RESET}")

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        # Update state directly
        session.state["interaction_history"] = interaction_history
        
        print(f"{Colors.CYAN}Added to interaction history: {entry['action']}{Colors.RESET}")
        print(f"{Colors.CYAN}Total interaction history entries: {len(interaction_history)}{Colors.RESET}")

    except Exception as e:
        print(f"Error updating interaction history: {e}")
        import traceback
        traceback.print_exc()

def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    """Add a user query to the interaction history."""
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )

def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    """Add an agent response to the interaction history."""
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )

def display_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way."""
    try:
        # Get session with full parameters to ensure consistency
        try:
            session = session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
        except:
            # Fallback to session_id only if the above fails
            session = session_service.get_session(session_id)

        # Format the output with clear sections
        print(f"\n{'-' * 10} {label} {'-' * 10}")
        
        # Debug: Print session info
        print(f"{Colors.MAGENTA}DEBUG: Display session {session.id}{Colors.RESET}")

        # Show user name
        user_name = session.state.get("user_name", "Unknown")
        print(f"User: {user_name}")

        # Show API data keys only
        api_data = session.state.get("api_data", {})
        print("API Data loaded:")
        for key in api_data.keys():
            print(f"  - {key}")

        # Show agent switches
        agent_data_keys = [k for k in session.state.keys() if k.endswith("_agent_data")]
        if agent_data_keys:
            print("Agent switches:")
            for key in agent_data_keys:
                agent_name = key.replace("_agent_data", "")
                print(f"  - {agent_name}")

        # Show interaction history
        interaction_history = session.state.get("interaction_history", [])
        print("Interaction History:")
        if interaction_history:
            for idx, interaction in enumerate(interaction_history, 1):
                if isinstance(interaction, dict):
                    action = interaction.get("action", "interaction")
                    timestamp = interaction.get("timestamp", "unknown time")
                    if action == "user_query":
                        query = interaction.get("query", "")
                        print(f'  {idx}. User query at {timestamp}: "{query}"')
                    elif action == "agent_response":
                        agent = interaction.get("agent", "unknown")
                        response = interaction.get("response", "")
                        print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                    else:
                        print(f"  {idx}. {action} at {timestamp}")
                else:
                    print(f"  {idx}. {interaction}")
        else:
            print("  None")

        # Show agent outputs
        agent_outputs = [k for k in session.state.keys() if k.endswith("_output")]
        if agent_outputs:
            print("Agent Outputs:")
            for key in agent_outputs:
                print(f"  - {key}")
        else:
            print("Agent Outputs: None")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")
        import traceback
        traceback.print_exc()

def display_agent_outputs(session_state):
    """Display all agent outputs from the session state."""
    agent_keys = [
        "finara_coordinator_output",
        "credit_card_agent_output",
        "epf_agent_output",
        "equity_agent_output",
        "loan_agent_output",
        "mf_agent_output",
        "net_worth_agent_output",
        "spending_insights_agent_output",
    ]
    print("\n--- Agent Outputs ---")
    for key in agent_keys:
        output = session_state.get(key)
        if output:
            print(f"{key}: {output}")
    print("---------------------\n")

# Async function to process agent responses from the runner
async def process_agent_response(event):
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")
                has_specific_part = True

    # Check for final response after specific parts
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )

    return final_response

async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None
    active_agent_name = None

    # Display state before processing the message
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                active_agent_name = event.author
                print(f"{Colors.YELLOW}Active Agent: {active_agent_name}{Colors.RESET}")

            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")

    # Update the correct agent output in the session state
    if final_response_text and active_agent_name:
        session = runner.session_service.get_session(
            app_name=runner.app_name, user_id=user_id, session_id=session_id
        )
        
        # Map agent names to their output keys
        agent_output_key = f"{active_agent_name}_output"
        session.state[agent_output_key] = final_response_text
        session.state["last_active_subagent"] = active_agent_name
        
        print(f"{Colors.GREEN}Updated {agent_output_key} with response{Colors.RESET}")

        # Add the agent response to interaction history
        add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            active_agent_name,
            final_response_text,
        )

    # Display state after processing the message
    display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )

    print(f"{Colors.YELLOW}{'-' * 30}{Colors.RESET}")
    return final_response_text