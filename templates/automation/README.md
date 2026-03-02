# Automation Bot Template

A general-purpose task-automation bot built on Factory.ai components.

## What It Does

- Accepts natural-language commands to run, stop, and schedule jobs.
- Reports the status of running or completed jobs.
- Dispatches work to cloud services (AWS, Azure, GCP) via integrations.
- Retains job context for 24 hours.

## Configuration

Edit `bot.yaml` to:

| Key | Description |
|---|---|
| `components.nlp.intents` | Add custom trigger phrases for your workflows. |
| `components.memory.ttl_seconds` | Change the job-context retention window. |
| `components.decision.rules` | Map intents to custom workflow actions. |
| `integrations.aws/azure/gcp` | Enable and configure cloud back-ends. |
| `deployment.replicas` | Number of concurrent bot instances. |

## Generating This Bot

```bash
python -m factory generate \
  --template templates/automation \
  --name "AutoBot" \
  --env production
```

## Deploying

```bash
python -m factory deploy \
  --template templates/automation \
  --env production
```

Or use the **Deploy Bot / Swarm** GitHub Actions workflow.
