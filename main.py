# ───────────────────────────
# main.py
# ───────────────────────────
from flask import Flask, request, jsonify
from agent.agent_main import build_agent

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_query():
    data = request.json
    user_id = data.get("user_id", "demo_user_001")
    query = data.get("query")
    agent = build_agent(user_id)
    response = agent.run(query)
    return jsonify({"response": response})