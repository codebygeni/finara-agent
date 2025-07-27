from fastapi import FastAPI
import uvicorn

# FastAPI app for health check
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
import asyncio
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from finara_agent.agent import get_finara_coordinator
from google.genai import types

load_dotenv()

# Reduce logging verbosity
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_adk").setLevel(logging.ERROR)

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    OKGREEN = "\033[92m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    ENDC = RESET
    WARNING = YELLOW
    HEADER = MAGENTA

# ===== Initial Session State =====
initial_state = {
    # Essential User Profile
    "user_id": "1",
    "phone_number": "6666666666",
    "user_email": "Sushrut@123gmail.com",
    "user_name": "Sushrut",
    "age": "21",
    "city": "Mumbai",
    "maritial_status":"Unmarried",
    "dependents":"None",
    "is_authenticated": False,  # Start as not authenticated
    "career_stage": "early_career",
    "preferred_language": "Hindi",
    
    # MCP Session Management (Essential)
    "mcp_session_id": None,  # No static session
    "session_login_url": None,
    "available_tools": [],
    "tool_execution_history": [],
    "use_existing_mcp_session": False,
    
    # Agent State (Simplified)
    "current_agent": "finara_coordinator",
    "last_active_subagent": None,
    "last_agent_response": None,
    
    # Conversation Management
    "conversation_context": [],
    "interaction_history": [],
    
    # System Health (Essential)
    "error_count": 0,
    "last_error": None,
    "system_status": "ready",  # Start as ready, not authenticated
}

def display_welcome_message():
    """Display a comprehensive welcome message with system capabilities."""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🏦  WELCOME TO FINARA - YOUR AI FINANCIAL ASSISTANT  🏦{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}")
    print("I can help you with comprehensive financial analysis across:")
    print("  💰 Net Worth Analysis & Asset Allocation")
    print("  💳 Credit Cards & Credit Health Management") 
    print("  📊 Mutual Fund Portfolio & SIP Tracking")
    print("  📈 Stock Holdings & Equity Performance")
    print("  🏛️  EPF/Provident Fund & Retirement Planning")
    print("  💸 Spending Insights & Transaction Analytics")
    print(f"{Colors.ENDC}")
    print(f"{Colors.YELLOW}Examples you can try:{Colors.ENDC}")
    print(f"  • 'What's my net worth?'")
    print(f"  • 'Show me my mutual fund performance'")
    print(f"  • 'How much did I spend on food last month?'")
    print(f"  • 'What's my credit score?'")
    print(f"  • 'How is my EPF doing?'")
    print(f"  • 'Show me my stock portfolio'")
    print(f"\n{Colors.BOLD}Type 'help' for more options or 'exit' to quit.{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")

def display_help():
    """Display detailed help information."""
    print(f"\n{Colors.HEADER}🔍 FINARA HELP - AVAILABLE COMMANDS{Colors.ENDC}")
    print(f"{Colors.CYAN}")
    print("FINANCIAL ANALYSIS COMMANDS:")
    print("  net worth     - Complete financial overview")
    print("  assets        - Asset breakdown and allocation")
    print("  investments   - Investment performance summary")
    print("  mutual funds  - MF portfolio analysis")
    print("  stocks        - Equity holdings review")
    print("  credit        - Credit score and card analysis")
    print("  spending      - Expense tracking and insights")
    print("  epf           - EPF balance and retirement planning")
    print()
    print("SYSTEM COMMANDS:")
    print("  help          - Show this help message")
    print("  status        - Show system and session status")
    print("  clear         - Clear conversation history")
    print("  logged in     - Mark yourself as logged in after web login")
    print("  refresh       - Reset session and get new login URL")
    print("  exit/quit     - Exit the application")
    print(f"{Colors.ENDC}")

def display_system_status(session):
    """Display current system and session status."""
    print(f"\n{Colors.HEADER}📊 SYSTEM STATUS{Colors.ENDC}")
    print(f"{Colors.CYAN}")
    print(f"User: {session.state.get('user_name', 'Unknown')}")
    print(f"Session ID: {session.id}")
    print(f"Current Agent: {session.state.get('current_agent', 'Unknown')}")
    print(f"MCP Session: {'✅ Active' if session.state.get('mcp_session_id') else '❌ Not Set'}")
    if session.state.get('mcp_session_id'):
        print(f"MCP Session ID: {session.state.get('mcp_session_id')}")
    print(f"Authenticated: {'✅ Yes' if session.state.get('is_authenticated') else '❌ No'}")
    print(f"System Status: {session.state.get('system_status', 'Unknown')}")
    print(f"Error Count: {session.state.get('error_count', 0)}")
    print(f"Interactions: {len(session.state.get('interaction_history', []))}")
    print(f"{Colors.ENDC}")

def handle_system_commands(command, session, session_service, app_name, user_id, session_id):
    """Handle system commands like help, status, clear."""
    command = command.lower().strip()
    
    if command == "help":
        display_help()
        return True
    elif command == "status":
        display_system_status(session)
        return True
    elif command == "clear":
        session.state["interaction_history"] = []
        session.state["conversation_context"] = []
        print(f"{Colors.GREEN}✅ Conversation history cleared.{Colors.ENDC}")
        return True
    elif command in ["logged in", "login done", "login complete", "logged"]:
        # FIX: Ensure state is properly updated
        session.state["is_authenticated"] = True
        session.state["system_status"] = "authenticated"
        session.state["use_existing_mcp_session"] = True
        
        # ADD: Force session state update
        print(f"{Colors.YELLOW}DEBUG - Setting auth state: is_authenticated = True{Colors.RESET}")
        
        print(f"{Colors.GREEN}✅ Login status updated. You can now access your financial data.{Colors.ENDC}")
        if session.state.get("mcp_session_id"):
            print(f"{Colors.GREEN}🔑 Using MCP Session: {session.state.get('mcp_session_id')}{Colors.ENDC}")
        
        # ADD: Verify the state was set
        print(f"{Colors.YELLOW}DEBUG - Verification: is_authenticated = {session.state.get('is_authenticated')}{Colors.RESET}")
        
        return True
    elif command.startswith("mcp-session-") or (command.startswith("mcp_") and len(command) > 20):
        # Extract MCP session ID from command
        mcp_session_id = command
        session.state["mcp_session_id"] = mcp_session_id
        session.state["is_authenticated"] = True
        session.state["system_status"] = "authenticated"
        session.state["use_existing_mcp_session"] = True
        print(f"{Colors.GREEN}✅ MCP Session ID stored: {mcp_session_id}{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ You can now access your financial data.{Colors.ENDC}")
        return True
    elif command in ["refresh", "reset", "new session"]:
        session.state["mcp_session_id"] = None
        session.state["is_authenticated"] = False
        session.state["system_status"] = "ready"
        session.state["use_existing_mcp_session"] = False
        session.state["session_login_url"] = None
        print(f"{Colors.YELLOW}🔄 Session reset. You'll get a new login URL on your next request.{Colors.ENDC}")
        return True
    elif command in ["exit", "quit", "bye"]:
        print(f"{Colors.CYAN}👋 Thank you for using Finara! Goodbye!{Colors.ENDC}")
        return "exit"
    
    return False

def update_session_state_after_execution(session, final_response):
    """Update session state after agent execution."""
    try:
        # Update last active agent
        if hasattr(final_response, 'agent_used'):
            session.state["last_active_subagent"] = final_response.agent_used
        
        # Update system status
        session.state["system_status"] = "active"
        
        # Reset error count on successful execution
        session.state["error_count"] = 0
        session.state["last_error"] = None
        
        # Update conversation context 
        context = session.state.get("conversation_context", [])
        context.append({
            "timestamp": datetime.now().isoformat(),
            "response_summary": str(final_response)[:200] + "..." if len(str(final_response)) > 200 else str(final_response)
        })
        session.state["conversation_context"] = context[-10:]  # Keep last 10
        
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not update session state: {e}{Colors.ENDC}")

def handle_execution_error(session, error, user_query):
    """Handle and log execution errors with proper categorization."""
    session.state["error_count"] = session.state.get("error_count", 0) + 1
    session.state["last_error"] = {
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "query": user_query,
        "error_type": type(error).__name__
    }
    session.state["system_status"] = "error"
    
    error_str = str(error).lower()
    
    if "authentication" in error_str or "session" in error_str:
        print(f"{Colors.YELLOW}🔐 Authentication Issue Detected{Colors.ENDC}")
        print(f"{Colors.CYAN}It looks like you need to log in to access your financial data.{Colors.ENDC}")
        print(f"{Colors.CYAN}The system will guide you through the login process on your next request.{Colors.ENDC}")
    elif "timeout" in error_str or "connection" in error_str:
        print(f"{Colors.YELLOW}🌐 Connection Issue Detected{Colors.ENDC}")
        print(f"{Colors.CYAN}There seems to be a connectivity issue. Please try again in a moment.{Colors.ENDC}")
    elif "tool" in error_str:
        print(f"{Colors.YELLOW}🔧 Tool Execution Issue{Colors.ENDC}")
        print(f"{Colors.CYAN}There was an issue executing the financial tool. Please try rephrasing your request.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ An unexpected error occurred: {error}{Colors.ENDC}")
        if session.state["error_count"] >= 3:
            print(f"{Colors.YELLOW}⚠️  Multiple errors detected. Type 'status' to check system health.{Colors.ENDC}")

def display_agent_outputs(state):
    """Display agent outputs from state """
    # Only show if there are actual outputs and they're different from what was just displayed
    outputs_found = False
    for key, value in state.items():
        if key.endswith('_output') and value:
            outputs_found = True
            break
    
    if not outputs_found:
        print(f"{Colors.YELLOW}No additional outputs to display.{Colors.RESET}")

async def process_agent_response(event):
    """Process and display agent response events """
    final_response = None
    
    # Check for final response
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Simplified response display
            print(f"\n{Colors.CYAN}🤖 {final_response}{Colors.RESET}\n")
        else:
            print(f"{Colors.YELLOW}⚠️ No response content received{Colors.RESET}")

    return final_response

async def call_agent_async(runner, user_id, session_id, query, session_with_auth_state):
    """Call the agent asynchronously with the user's query - with conversation context."""
    
    # Use the session that has the authentication state instead of getting a fresh one
    session = session_with_auth_state

    # *** ADD THIS: Ensure the runner's session has the latest state ***
    try:
        # Update the runner's session with our current state
        runner_session = await runner.session_service.get_session(
            app_name=runner.app_name, user_id=user_id, session_id=session_id
        )
        # Sync critical state to the runner's session
        runner_session.state.update({
            "mcp_session_id": session.state.get("mcp_session_id"),
            "is_authenticated": session.state.get("is_authenticated"),
            "use_existing_mcp_session": session.state.get("use_existing_mcp_session"),
            "authenticated_mcp_session": session.state.get("mcp_session_id")  # Additional key for tool
        })
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not sync session state: {e}{Colors.RESET}")
    
    # Build conversation context for the agent 
    interaction_history = session.state.get("interaction_history", [])
    context_messages = []
    
    # Check authentication status
    is_authenticated = session.state.get("is_authenticated", False)
    mcp_session_id = session.state.get("mcp_session_id")
    
    print(f"{Colors.YELLOW}DEBUG - Auth Status: {is_authenticated}, MCP Session: {mcp_session_id}{Colors.RESET}")

    if is_authenticated and mcp_session_id and mcp_session_id != "None" and mcp_session_id:
        context_messages.append("🚨 MANDATORY SYSTEM OVERRIDE 🚨")
        context_messages.append(f"AUTHENTICATED_SESSION_ID: {mcp_session_id}")
        context_messages.append("CRITICAL: User is already logged in with valid MCP session")
        context_messages.append("INSTRUCTION: DO NOT CREATE NEW SESSION")
        context_messages.append("INSTRUCTION: USE EXISTING SESSION FOR ALL TOOLS")
        context_messages.append("INSTRUCTION: BYPASS get_session_id TOOL COMPLETELY")
        context_messages.append("ACTION: PROCEED DIRECTLY TO FINANCIAL DATA RETRIEVAL")
        context_messages.append(f"SESSION_TO_USE: {mcp_session_id}")
        context_messages.append("SYSTEM_STATUS: AUTHENTICATED")
        context_messages.append("")
    else:
        # ADD: Explicit login flow instruction
        context_messages.append("🔑 USER NOT AUTHENTICATED")
        context_messages.append("MANDATORY: Call get_session_id tool FIRST")
        context_messages.append("STEP 1: Initialize MCP session")
        context_messages.append("STEP 2: Provide login URL to user") 
        context_messages.append("STEP 3: Wait for user confirmation")
        context_messages.append("DO NOT attempt to fetch financial data without valid session")
        context_messages.append("")
    
    if interaction_history:
        context_messages.append("=== CONVERSATION HISTORY ===")
        for interaction in interaction_history[-5:]:  # Last 5 interactions
            if interaction.get("type") == "user_query":
                user_query_text = interaction.get('query', '')
                context_messages.append(f"User: {user_query_text}")
                # Explicitly highlight authentication messages
                if any(phrase in user_query_text.lower() for phrase in ['logged in', 'login done', 'login complete']):
                    context_messages.append("^^ USER CONFIRMED LOGIN COMPLETION ^^")
            elif interaction.get("type") == "agent_response":
                response = interaction.get('response', '')[:150]  # Truncate long responses
                context_messages.append(f"Assistant: {response}...")
        context_messages.append("=== END HISTORY ===")
        context_messages.append("")  # Empty line
    
    # Combine context and current query
    if context_messages:
        full_message = "\n".join(context_messages) + f"Current Query: {query}"
    else:
        full_message = query
    
    # DEBUG: Print what we're sending to the agent
    print(f"{Colors.YELLOW}DEBUG - Sending to agent:{Colors.RESET}")
    print(f"{Colors.YELLOW}{full_message[:500]}...{Colors.RESET}")
    
    content = types.Content(role="user", parts=[types.Part(text=full_message)])
    print(f"{Colors.BLUE}🤖 Processing: {query}{Colors.RESET}")
    
    final_response_text = None
    active_agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Only capture agent name, no excessive logging
            if event.author:
                active_agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")

    # Simplified session update
    if final_response_text and active_agent_name:
        try:
            session = await runner.session_service.get_session(
                app_name=runner.app_name, user_id=user_id, session_id=session_id
            )
            
            # Store response without excessive logging
            agent_output_key = f"{active_agent_name}_output"
            session.state[agent_output_key] = final_response_text
            session.state["last_active_subagent"] = active_agent_name
            session.state["last_agent_response"] = final_response_text
            
            # Add to history
            interaction_history = session.state.get("interaction_history", [])
            interaction_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "agent_response",
                "agent": active_agent_name,
                "response": final_response_text
            })
            session.state["interaction_history"] = interaction_history
            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not update session: {e}{Colors.RESET}")

    return final_response_text

async def execute_user_query(session, session_service, app_name, user_id, session_id, user_query):
    """Execute user query with proper error handling and state management."""
    try:
        # ADD: Debug current session state before proceeding
        print(f"{Colors.YELLOW}DEBUG - Session state before query: is_authenticated = {session.state.get('is_authenticated')}{Colors.RESET}")
        
        # Add query to interaction history
        interaction_history = session.state.get("interaction_history", [])
        interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_query",
            "query": user_query
        })
        session.state["interaction_history"] = interaction_history

        # *** ADD THIS: Create coordinator with current session state ***
        coordinator = get_finara_coordinator(session)
        
        # Get fresh session data for coordinator
        # fresh_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Create runner with up-to-date coordinator
        runner = Runner(
            agent=coordinator,
            app_name=app_name,
            session_service=session_service,
        )
    
        # *** ADD THIS: Ensure runner's session is synced before execution ***
        try:
            runner_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            runner_session.state.update(session.state)  # Sync all state
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not sync runner session: {e}{Colors.RESET}")
        
        # Don't set any static session - let the proper login flow work
        if session.state.get("mcp_session_id"):
            existing_session = session.state.get("mcp_session_id")
            print(f"{Colors.GREEN}🔑 Using existing MCP session: {existing_session}{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}🔑 No MCP session found. Login flow will be triggered.{Colors.ENDC}")

        # Execute the agent
        final_response = await call_agent_async(runner, user_id, session_id, user_query, session)
        
        # Check if response contains login URL and extract MCP session ID
        if final_response and "mockWebPage?sessionId=" in final_response:
            match = re.search(r'sessionId=([^)\s&]+)', final_response)
            if match:
                mcp_session_id = match.group(1)
                session.state["mcp_session_id"] = mcp_session_id
                session.state["session_login_url"] = f"http://localhost:8080/mockWebPage?sessionId={mcp_session_id}"
                print(f"{Colors.GREEN}📝 Stored MCP Session ID: {mcp_session_id}{Colors.ENDC}")
                print(f"{Colors.YELLOW}💡 Tip: After logging in, type 'logged in' or paste the session ID to continue.{Colors.ENDC}")
        
        # Update session state after successful execution
        update_session_state_after_execution(session, final_response)
        
        # Display results
        print(f"\n{Colors.GREEN}✅ Analysis Complete{Colors.ENDC}")
        display_agent_outputs(session.state)
        
        return True
        
    except Exception as e:
        handle_execution_error(session, e, user_query)
        
        # Print detailed error for debugging if needed
        if session.state.get("error_count", 0) >= 2:
            print(f"\n{Colors.YELLOW}Debug Information:{Colors.ENDC}")
            print(f"{Colors.YELLOW}Error Type: {type(e).__name__}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Error Details: {str(e)[:200]}...{Colors.ENDC}")
        
        return False

async def main():
    """Enhanced main async function to run the Finara agent system."""
    # Define App constants
    APP_NAME = "Finara"
    USER_ID = initial_state["user_id"]

    print(f"{Colors.GREEN}🚀 Initializing Finara Financial Assistant...{Colors.ENDC}")
    
    try:
        # Create session service and session properly with await
        session_service = InMemorySessionService()
        
        # Create a new session and set its initial state (await the async call)
        # Removed await
        session =  session_service.create_session(app_name=APP_NAME, user_id=USER_ID, state=initial_state)
        SESSION_ID = session.id
        
        print(f"{Colors.GREEN}✅ Session created with ID: {SESSION_ID}{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to initialize session: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please check your ADK setup and try again.{Colors.ENDC}")
        return
    
    # Display welcome message
    display_welcome_message()

    # Main interaction loop
    while True:
        try:
            user_query = input(f"\n{Colors.BOLD}💬 You: {Colors.ENDC}").strip()
            
            if not user_query:
                continue
                
            # Handle system commands
            command_result = handle_system_commands(user_query, session, session_service, APP_NAME, USER_ID, SESSION_ID)
            if command_result == "exit":
                break
            elif command_result:
                continue
            
            # Execute user query
            success = await execute_user_query(session, session_service, APP_NAME, USER_ID, SESSION_ID, user_query)
            
            if not success and session.state.get("error_count", 0) >= 5:
                print(f"{Colors.RED}❌ Too many errors encountered. Please restart the application.{Colors.ENDC}")
                break
                
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Session interrupted. Goodbye!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Critical system error: {e}{Colors.ENDC}")
            session.state["system_status"] = "critical_error"
            break

    # Cleanup and final status
    print(f"\n{Colors.HEADER}📊 FINAL SESSION SUMMARY{Colors.ENDC}")
    print(f"{Colors.CYAN}Total Interactions: {len(session.state.get('interaction_history', []))}{Colors.ENDC}")
    print(f"{Colors.CYAN}Errors Encountered: {session.state.get('error_count', 0)}{Colors.ENDC}")
    print(f"{Colors.GREEN}Thank you for using Finara! 🏦✨{Colors.ENDC}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
        port = int(os.environ.get('PORT', 8080))
        uvicorn.run("main:app", host="0.0.0.0", port=port)
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error starting Finara: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please check your environment setup and try again.{Colors.ENDC}")