# ───────────────────────────
# agent/agent_main.py
# ───────────────────────────
from google.adk import Agent
from firebase_admin import credentials, initialize_app, firestore
import firebase_admin

cred = credentials.ApplicationDefault()
initialize_app(cred)
db = firestore.client()

def get_user_profile(user_id: str):
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() if doc.exists else {"error": "User not found"}

def build_agent(user_id: str):
    def tool_fn(_):
        return str(get_user_profile(user_id))

    return Agent(
        name="finara_agent",
        model="models/gemini-1.5-pro",
        instruction="Answer financial questions using user profile.",
        tools=[
            {
                "name": "getUserProfile",
                "description": "Fetch user profile from Firestore",
                "function": tool_fn,
            }
        ]
    )
