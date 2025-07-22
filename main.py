# ───────────────────────────
# main.py
# ───────────────────────────
from flask import Flask, request, jsonify
from agent.agent_main import build_agent

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_query():
    data = request.get_json(silent=True)
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    user_id = data.get("user_id", "demo_user_001")
    query = data["query"]

    try:
        agent = build_agent(user_id)
        response = agent.run(query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)