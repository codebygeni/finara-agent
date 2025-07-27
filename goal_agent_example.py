"""
Example of how to use the Goal Agent

This demonstrates how to trigger the goal agent with goal data and get structured analysis.
"""

# Example goal data that would be provided by external API
example_goal_data = {
    "user_info": {
        "age": 21,
        "marital_status": "Unmarried"
        ""
    },
    "goal": {
        "id": "goal_01",
        "goal_amount": "20lakh",
        "goal_description": "How long will it take for me to afford a 20lakh car in three years based on my financial portfolio. I don't wish to sell my stocks.",
        "goal_line": "Can I afford a 20lakh car by the next year",
        "goal_timeline": "3 years"
    }
}

# Example user message that would trigger the goal agent
example_user_message = """
I am 21 years old, Unmarried. This is my finance data and I have a goal:

{
    "id": "goal_01",
    "goal_amount": "20lakh",
    "goal_description": "How long will it take for me to afford a 20lakh car in three years based on my financial portfolio. I don't wish to sell my stocks.",
    "goal_line": "Can I afford a 20lakh car by the next year",
    "goal_timeline": "3 years"
}

Please analyze my current financial situation and provide a structured plan to achieve this goal.
"""