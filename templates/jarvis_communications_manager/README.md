# Jarvis Communications Manager Template

An AI assistant for engineering managers who need structured, reusable communication workflows.

## What It Does

- Drafts weekly or milestone status updates for engineering teams.
- Prepares stakeholder and leadership briefings with concise summaries.
- Produces meeting follow-ups with recaps and action items.
- Routes incident-related requests into a dedicated communications flow.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Adjust trigger phrases for your organization. |
| `components.memory.ttl_seconds` | Change how long active communication context is retained. |
| `components.decision.rules` | Customize routing for status, incidents, and follow-ups. |
| `integrations.slack/email` | Enable outbound communications integrations. |
| `deployment.environment.DEFAULT_AUDIENCE` | Set the primary communications audience. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/jarvis_communications_manager \
  --name "JarvisCommsBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/jarvis_communications_manager \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
