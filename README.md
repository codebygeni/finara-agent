# Finara Agent

Finara Agent is a modular Python framework designed to automate financial data analysis and insights. It supports multiple sub-agents for tasks such as credit card analysis, equity tracking, EPF management, mutual funds, net worth calculation, and spending insights.

## Features

- Modular agent architecture for different financial domains
- Easy integration with external tools and APIs
- Extensible with custom agents and tools
- Docker support for deployment

## Project Structure

```
finara-agent/
│
├── main.py                  # Entry point
├── goal_agent_example.py    # Example usage
├── deploy_to_agent_engine.py
├── requirements.txt         # Python dependencies
├── Dockerfile               # Containerization
├── finara_agent/            # Core package
│   ├── agent.py
│   ├── prompt.py
│   ├── sub_agents/          # Domain-specific agents
│   └── tools/               # Utility tools
└── README.md
```

## Getting Started

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Run the main agent:**
   ```powershell
   python main.py
   ```

## Configuration

- Place your service account credentials in `service-account.json`.
- Customize agent behavior in `finara_agent/sub_agents/`.

## Contributing

Pull requests and issues are welcome. Please follow standard Python coding conventions.
