# Engineer Manager Template

An engineering-coordination bot built on Factory.ai components.

## What It Does

- Triage engineering requests, incidents, and delivery-status questions.
- Coordinate prioritization, delegation, and escalation workflows.
- Track technical context between turns for active initiatives.
- Route people-management or blocker signals into explicit actions.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Add or adjust engineering-management request phrases. |
| `components.memory.ttl_seconds` | Change how long delivery context is retained. |
| `components.decision.rules` | Customize prioritization, escalation, and status logic. |
| `integrations.allbots.queue` | Set the AllBots.com queue for engineering-management work. |
| `deployment.replicas` | Number of concurrent engineering-manager instances. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/engineer_manager \
  --name "EngineerManagerBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/engineer_manager \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
