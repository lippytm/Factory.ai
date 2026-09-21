# Jarvis Communications Manager Template

An AI assistant for engineering managers who need structured, reusable communication workflows.

## What It Does

- Drafts weekly or milestone status updates for engineering teams.
- Prepares stakeholder and leadership briefings with concise summaries.
- Produces meeting follow-ups with recaps and action items.
- Routes incident-related requests into a dedicated communications flow.

## Configuration

Edit `bot.yaml` to adjust:

- `components.nlp.intents` for organization-specific trigger phrases.
- `components.memory.ttl_seconds` for active communication context retention.
- `components.decision.rules` for status, incident, and follow-up routing.
- `integrations.slack` and `integrations.email` for outbound communications workflows.
- `deployment.environment.DEFAULT_AUDIENCE` for the primary audience.

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
