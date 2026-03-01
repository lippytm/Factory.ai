# Factory.ai
For connections workflows to GitHub, ChatGPT, AllBots.com, etc 

## Overview

Factory.ai provides a lightweight Python library and CLI for creating and managing connection workflows to popular AI and developer services:

- **GitHub** — personal access token / OAuth token authentication
- **OpenAI / ChatGPT** — API key authentication
- **AllBots.com** — API key authentication

## Installation

```bash
pip install -e .
```

## Quickstart

### Python API

```python
from factory_ai import ConnectionWorkflow

wf = ConnectionWorkflow()

# Create a GitHub connection
gh = wf.create("github", token="ghp_your_token_here")

# Create an OpenAI / ChatGPT connection
ai = wf.create("openai", api_key="sk-your_key_here")
# or using the chatgpt alias:
ai = wf.create("chatgpt", api_key="sk-your_key_here")

# Create an AllBots.com connection
bots = wf.create("allbots", api_key="your_allbots_key")

# List all saved connections
for entry in wf.list_connections():
    print(entry)

# Remove a connection
wf.remove("github")
```

### CLI

```bash
# List supported services
factory-ai services

# Create connections
factory-ai create github token=ghp_your_token_here
factory-ai create openai api_key=sk-your_key_here
factory-ai create allbots api_key=your_allbots_key

# Use a custom name
factory-ai create github --name work-github token=ghp_your_token_here

# List saved connections
factory-ai list

# Remove a connection
factory-ai remove work-github
```

## Project Structure

```
src/factory_ai/
├── __init__.py          # Public API exports
├── workflow.py          # ConnectionWorkflow orchestrator
├── config.py            # Connection metadata persistence
├── cli.py               # Command-line interface
└── connections/
    ├── base.py          # Abstract BaseConnection
    ├── github.py        # GitHub connection workflow
    ├── openai.py        # OpenAI/ChatGPT connection workflow
    └── allbots.py       # AllBots.com connection workflow

tests/
├── test_connections.py  # Tests for individual connection classes
└── test_workflow.py     # Tests for workflow and config manager
```

## Running Tests

```bash
pip install pytest
pytest
```
