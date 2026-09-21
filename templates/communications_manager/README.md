# Communications Manager Template

A communications-operations bot built on Factory.ai components.

## What It Does

- Triage inbound communication requests and assign the right response path.
- Draft announcements, responses, and briefing notes from approved prompts.
- Escalate sensitive or crisis-related items for human review.
- Preserve communication context between turns for active workstreams.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Add or adjust communications request phrases. |
| `components.memory.ttl_seconds` | Change how long communication context is retained. |
| `components.decision.rules` | Customize drafting, approval, and escalation logic. |
| `integrations.allbots.queue` | Set the AllBots.com queue for communications work. |
| `deployment.replicas` | Number of concurrent communications-manager instances. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/communications_manager \
  --name "CommunicationsManagerBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/communications_manager \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
