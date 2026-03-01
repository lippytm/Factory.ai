# Customer Support Bot Template

A ready-to-deploy customer-support bot built on Factory.ai components.

## What It Does

- Greets and bids farewell to users with canned responses.
- Routes billing and technical queries to dedicated conversation flows.
- Transfers users to human agents on request.
- Persists session state for up to 1 hour between turns.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Add or modify intent keywords. |
| `components.memory.ttl_seconds` | Change the session expiry window. |
| `components.decision.rules` | Reorder or add routing rules. |
| `integrations.allbots.queue` | Set the AllBots.com support queue name. |
| `deployment.replicas` | Number of concurrent bot instances. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/customer_support \
  --name "SupportBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/customer_support \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
