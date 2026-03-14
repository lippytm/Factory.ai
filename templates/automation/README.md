# Automation Bot Template

A general-purpose task-automation bot built on Factory.ai components. It accepts natural-language commands to run, stop, check, and schedule background jobs — letting your team trigger and monitor automated workflows without needing to write scripts or learn CLI syntax.

---

## What It Does

| Interaction | How It Works |
|---|---|
| **Run a job** | Detects phrases like "run" or "execute" and dispatches the job to your configured cloud back-end. |
| **Stop a job** | Detects phrases like "cancel" or "abort" and halts the running job. |
| **Check status** | Detects phrases like "status" or "list" and reports the current state of all jobs. |
| **Schedule a job** | Detects phrases like "every hour" or "at midnight" and creates a recurring schedule. |
| **Job context memory** | Retains job context for 24 hours, so follow-up commands relate to the same job automatically. |

---

## Configuration Reference

Open `bot.yaml` to customise the template. The table below lists the settings you are most likely to change:

| Setting (bot.yaml path) | Default | Description |
|---|---|---|
| `components.nlp.intents` | See file | Add, remove, or edit the trigger phrases for each command. |
| `components.memory.ttl_seconds` | `86400` (24 hours) | How long the bot remembers job context. |
| `components.decision.rules` | See file | Maps each intent to an action. Rules are evaluated top-to-bottom — the first match wins. |
| `integrations.aws/azure/gcp.enabled` | `false` | Set to `true` to activate the corresponding cloud back-end. |
| `deployment.target` | `allbots` | Where to deploy: `allbots`, `aws`, `azure`, or `gcp`. |
| `deployment.replicas` | `1` | Number of simultaneous instances. |
| `deployment.environment.MAX_CONCURRENT_JOBS` | `"10"` | Maximum number of jobs the bot runs at the same time. |

---

## Quick Customisation Examples

### Add a custom command

```yaml
# bot.yaml → components.nlp.intents
restart_service: ["restart", "reboot", "bounce", "reload"]
```

Then add a matching decision rule:

```yaml
# bot.yaml → components.decision.rules
- condition: "intent == 'restart_service'"
  action:    "restart_service_handler"
```

### Enable AWS as the deployment back-end

```yaml
# bot.yaml → integrations
aws:
  enabled: true

# bot.yaml → deployment
target: aws
```

Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as environment variables or GitHub Actions secrets.

### Allow more concurrent jobs

```yaml
# bot.yaml → deployment.environment
MAX_CONCURRENT_JOBS: "25"
```

---

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

Or use the **Deploy Bot / Swarm** GitHub Actions workflow (recommended for team environments).

---

## Further Reading

- [Full User Guide](../../docs/user_guide.md) — Detailed explanation of every setting and concept.
- [bot.yaml schema](../../docs/user_guide.md#4-understanding-botyaml) — Complete annotated reference.

