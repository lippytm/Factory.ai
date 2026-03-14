# Customer Support Bot Template

A ready-to-deploy customer-support bot built on Factory.ai components. It handles the most common support interactions out of the box — greetings, billing queries, technical questions, and escalating to a human agent — so you can be up and running without writing any code.

---

## What It Does

| Interaction | How It Works |
|---|---|
| **Greetings / farewells** | Detects phrases like "hello" or "thanks" and sends a canned response. |
| **Billing queries** | Detects phrases like "invoice" or "refund" and opens a dedicated billing conversation flow. |
| **Technical issues** | Detects phrases like "error" or "not working" and opens a technical-support flow. |
| **Human escalation** | Detects phrases like "agent" or "manager" and immediately transfers the user to a live support agent. |
| **Session memory** | Remembers the conversation context for up to 1 hour, so users don't have to repeat themselves. |

---

## Configuration Reference

Open `bot.yaml` to customise the template. The table below lists the settings you are most likely to change:

| Setting (bot.yaml path) | Default | Description |
|---|---|---|
| `components.nlp.intents` | See file | Add, remove, or edit the trigger phrases for each intent. |
| `components.memory.ttl_seconds` | `3600` (1 hour) | How long the bot remembers a session. Set to `86400` for 24 hours. |
| `components.decision.rules` | See file | The routing rules that map each detected intent to an action. Rules are evaluated top-to-bottom — the first match wins. |
| `integrations.allbots.queue` | `"support-queue"` | The AllBots.com queue name this bot listens on. |
| `deployment.target` | `allbots` | Where to deploy: `allbots`, `aws`, `azure`, or `gcp`. |
| `deployment.replicas` | `2` | Number of simultaneous instances (increase for higher traffic). |

---

## Quick Customisation Examples

### Add a new intent

```yaml
# bot.yaml → components.nlp.intents
returns: ["return", "send back", "refund item", "exchange"]
```

Then add a matching decision rule:

```yaml
# bot.yaml → components.decision.rules
- condition: "intent == 'returns'"
  action:    "open_returns_flow"
```

### Increase session memory

```yaml
# bot.yaml → components.memory
ttl_seconds: 7200   # 2 hours
```

### Deploy to AWS instead of AllBots.com

```yaml
# bot.yaml → deployment
target: aws
```

---

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

Or use the **Deploy Bot / Swarm** GitHub Actions workflow (recommended for team environments).

---

## Further Reading

- [Full User Guide](../../docs/user_guide.md) — Detailed explanation of every setting and concept.
- [bot.yaml schema](../../docs/user_guide.md#4-understanding-botyaml) — Complete annotated reference.

