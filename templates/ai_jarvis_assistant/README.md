# AI Jarvis Assistant Template

A general-purpose executive assistant bot built on Factory.ai components.

## What It Does

- Handles greetings, follow-up requests, status checks, and briefing requests.
- Maintains short-term working context for active assistant tasks.
- Routes escalations and delegated work to downstream teams or systems.
- Supports task coordination across approved integrations.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Add or adjust assistant command phrases. |
| `components.memory.ttl_seconds` | Change how long assistant context is retained. |
| `components.decision.rules` | Customize assistant routing and escalation behavior. |
| `integrations.allbots.queue` | Set the AllBots.com queue for assistant requests. |
| `deployment.replicas` | Number of concurrent assistant instances. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/ai_jarvis_assistant \
  --name "AIJarvisAssistantBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/ai_jarvis_assistant \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
