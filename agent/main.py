def handle(request):
    user_input = request.get("input", "").lower()

    if "hello" in user_input:
        return {"output": "Hi there! I am your Finara Agent."}
    else:
        return {"output": "I can only say hello for now. Try greeting me!"}
