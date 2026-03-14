# Factory.ai User Guide

Welcome to Factory.ai! This guide walks you through everything you need to know to build, customise, and deploy AI bots — even if you've never used the platform before.

---

## Table of Contents

1. [What Is Factory.ai?](#1-what-is-factoryai)
2. [How It Works — The Big Picture](#2-how-it-works--the-big-picture)
3. [Setting Up Your Environment](#3-setting-up-your-environment)
4. [Understanding bot.yaml](#4-understanding-botyaml)
5. [Working With Templates](#5-working-with-templates)
6. [Components In Depth](#6-components-in-depth)
7. [Integrations](#7-integrations)
8. [Deploying a Bot](#8-deploying-a-bot)
9. [Building a Swarm](#9-building-a-swarm)
10. [CI/CD and Automation](#10-cicd-and-automation)
11. [Glossary](#11-glossary)
12. [Frequently Asked Questions](#12-frequently-asked-questions)

---

## 1. What Is Factory.ai?

Factory.ai is a **bot-creation and deployment platform**. It gives you:

- **Pre-built templates** — Ready-to-go bots for common use cases (customer support, task automation, etc.). You customise them rather than building from zero.
- **Reusable components** — Standardised modules for understanding language (NLP), remembering conversations (Memory), and routing to the right action (Decision). You don't have to write this logic yourself.
- **One-command deployment** — Point Factory.ai at a template and a target cloud, and it handles the rest.
- **Swarm management** — Run multiple bots as a coordinated team, with automatic load-balancing.

### Who Is It For?

- **Developers** who want to ship an AI bot quickly without writing all the common infrastructure code.
- **Teams** who want a consistent, auditable way to build and deploy bots across projects.
- **Operations engineers** who need one-click deployments and automated compliance logs.

---

## 2. How It Works — The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Factory.ai                              │
│                                                                 │
│   Templates          Components           Integrations          │
│  ┌──────────┐       ┌──────────┐         ┌──────────────────┐  │
│  │ customer │  ───► │   NLP    │ ──────► │   AllBots.com    │  │
│  │ _support │       │  Memory  │         │   AWS Lambda     │  │
│  │          │       │ Decision │         │   Azure Funcs    │  │
│  ├──────────┤       └──────────┘         │   GCP Cloud Fn   │  │
│  │automation│                            └──────────────────┘  │
│  └──────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
    bot.yaml (your config)
          │
          ▼
    python -m factory generate / deploy / swarm
```

The workflow in three steps:

1. **Pick a template** — Choose the template that most closely matches your use case.
2. **Edit `bot.yaml`** — Customise the template's intents, rules, and deployment settings.
3. **Deploy** — Run one command (or click one button in GitHub Actions) and your bot is live.

---

## 3. Setting Up Your Environment

### Requirements

| Requirement | Version | Why |
|---|---|---|
| Python | 3.10+ | Runtime for all Factory.ai scripts |
| pip | Any | Installing Python packages |
| PyYAML | ≥6.0 | Parsing `bot.yaml` manifests |
| AllBots API key | — | Deploying to AllBots.com (optional for local testing) |

### Installation

```bash
# Clone the repository
git clone https://github.com/lippytm/Factory.ai.git
cd Factory.ai

# Install the only required dependency
pip install pyyaml

# Optional: install cloud SDK dependencies
pip install boto3        # for AWS deployments
pip install azure-functions  # for Azure deployments
```

### Setting Your API Key

Store your AllBots API key as an environment variable — never hard-code it in a file:

```bash
# Linux / macOS
export ALLBOTS_API_KEY="your-key-here"

# Windows (Command Prompt)
set ALLBOTS_API_KEY=your-key-here

# Windows (PowerShell)
$env:ALLBOTS_API_KEY = "your-key-here"
```

For GitHub Actions deployments, store the key as a [repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) named `ALLBOTS_API_KEY`.

---

## 4. Understanding bot.yaml

Every bot is defined by a single `bot.yaml` file. Here is a fully annotated example:

```yaml
# ── Identity ──────────────────────────────────────────────────────────────────
name: CustomerSupportBot          # Display name for the bot
version: "1.0.0"                  # Semantic version (update when you make changes)
description: >
  What this bot does, in plain English.

# ── Components ────────────────────────────────────────────────────────────────
components:

  nlp:
    module: components.nlp.text_processor   # Don't change this
    intents:
      # Each key is an intent name; the list contains trigger phrases.
      # When a user's message matches any phrase, the intent fires.
      greeting:  ["hello", "hi", "hey"]
      farewell:  ["bye", "goodbye", "see you"]

  memory:
    module: components.memory.state_store   # Don't change this
    ttl_seconds: 3600     # How long the bot remembers the conversation.
                          # 3600 = 1 hour. Use 86400 for 24 hours.

  decision:
    module: components.decision.rule_engine  # Don't change this
    rules:
      # Rules are evaluated top-to-bottom. The first matching rule wins.
      # 'condition' uses Python-like expressions over the detected intent.
      # 'action' is the name of the handler function to call.
      - condition: "intent == 'greeting'"
        action:    "send_welcome_message"
      - condition: "intent == 'farewell'"
        action:    "send_farewell_message"

# ── Extensions ────────────────────────────────────────────────────────────────
extensions: []    # List optional add-on module names here

# ── Integrations ──────────────────────────────────────────────────────────────
integrations:
  allbots:
    enabled: true
    queue: "support-queue"    # The AllBots.com queue to publish messages to
  aws:
    enabled: false            # Set to true to enable AWS deployment
  azure:
    enabled: false
  gcp:
    enabled: false

# ── Deployment ────────────────────────────────────────────────────────────────
deployment:
  target: allbots     # Where to deploy: allbots | aws | azure | gcp
  replicas: 2         # Number of simultaneous instances
  environment:
    LOG_LEVEL: "INFO" # Pass any environment variables your bot needs here
```

### Required Fields

The CI validation script checks that every `bot.yaml` contains at minimum:

| Field | Example value |
|---|---|
| `name` | `"CustomerSupportBot"` |
| `version` | `"1.0.0"` |
| `description` | `"Handles customer queries…"` |
| `components` | *(object — see above)* |
| `deployment` | *(object — see above)* |

---

## 5. Working With Templates

### Available Templates

| Template | Location | Use Case |
|---|---|---|
| Customer Support | `templates/customer_support/` | Greetings, billing queries, tech support, human escalation |
| Automation | `templates/automation/` | Running, stopping, scheduling, and monitoring background jobs |

### Using a Template

```bash
# Generate a bot from the customer-support template
python -m factory generate \
  --template templates/customer_support \
  --name "SupportBot"

# Generate a bot from the automation template
python -m factory generate \
  --template templates/automation \
  --name "AutoBot"
```

### Adding a New Template

1. Create a directory: `templates/<your_industry>/`
2. Copy `templates/customer_support/bot.yaml` into it and edit the relevant fields.
3. Add a `README.md` explaining what the bot does (use `templates/customer_support/README.md` as a model).
4. Run `python ci_cd/scripts/validate_templates.py` to check your manifest.
5. Open a pull request — the CI pipeline validates automatically.

---

## 6. Components In Depth

### NLP — Understanding User Messages

File: `components/nlp/text_processor.py`

The NLP component reads a raw user message and returns:
- **Tokens** — individual words/phrases split from the message
- **Intent** — which of your defined intents (if any) best matches
- **Entities** — key values extracted from the message (e.g. a date or product name)

You configure it by listing **intents** and their trigger phrases in `bot.yaml`:

```yaml
intents:
  order_status: ["where is my order", "track my package", "order status"]
  cancel_order: ["cancel my order", "I want to cancel", "cancel"]
```

### Memory — Remembering the Conversation

File: `components/memory/state_store.py`

The Memory component keeps a short-term key/value store for each conversation session. This lets the bot remember what was said earlier in the same chat.

- `ttl_seconds` — How long (in seconds) a session is kept alive after the last message. When the session expires, the bot starts fresh.

### Decision — Routing to the Right Action

File: `components/decision/rule_engine.py`

The Decision component evaluates a list of rules in order and calls the action associated with the first rule whose condition matches.

```yaml
rules:
  - condition: "intent == 'cancel_order'"
    action:    "start_cancellation_flow"
  - condition: "intent == 'order_status'"
    action:    "look_up_order"
```

Rules use a simple expression syntax:
- `intent == 'name'` — exact match
- `intent in ('name1', 'name2')` — match any of a list
- `entity['product'] == 'widget'` — match on an extracted entity

---

## 7. Integrations

### AllBots.com (default)

```yaml
integrations:
  allbots:
    enabled: true
    queue: "my-queue-name"   # The queue your bot listens on
```

Set the `ALLBOTS_API_KEY` environment variable to authenticate.

### AWS Lambda

```yaml
integrations:
  aws:
    enabled: true

deployment:
  target: aws
```

Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables, or use an IAM role in GitHub Actions.

### Azure Functions

```yaml
integrations:
  azure:
    enabled: true

deployment:
  target: azure
```

Set `AZURE_SUBSCRIPTION_ID` and related credentials as environment variables.

### GCP Cloud Functions

```yaml
integrations:
  gcp:
    enabled: true

deployment:
  target: gcp
```

Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service-account JSON file.

---

## 8. Deploying a Bot

### Option A — GitHub Actions (recommended)

1. Push your `bot.yaml` changes to a branch and open a pull request.
2. Once the **Validate Templates** check passes, merge to `main`.
3. Go to **Actions → Deploy Bot / Swarm → Run workflow**.
4. Fill in:
   - **Template** — e.g. `templates/customer_support`
   - **Bot name** — e.g. `SupportBot`
   - **Environment** — `production` or `staging`
5. Click **Run workflow**. The deployment log appears in real time.

After every successful deploy, the **Transparency Log** workflow runs automatically and saves a JSON report of all components used as a workflow artifact.

### Option B — CLI

```bash
python -m factory deploy \
  --template templates/customer_support \
  --name "SupportBot" \
  --env production
```

---

## 9. Building a Swarm

A swarm is a group of bots that share incoming work. You specify a **coordinator strategy** to control how tasks are distributed:

| Strategy | When to use |
|---|---|
| `round-robin` | You want even load distribution across all bots. |
| `priority` | Some bots are more capable and should get first pick of tasks. |
| `least-loaded` | You want to minimise latency by always using the least-busy bot. |

```bash
python -m factory swarm \
  --bots "SupportBot,AutoBot,BillingBot" \
  --coordinator least-loaded \
  --env production
```

---

## 10. CI/CD and Automation

### Validate Templates Locally

```bash
python ci_cd/scripts/validate_templates.py
# Prints "All templates are valid." on success, or a descriptive error on failure.
```

### Generate a Transparency Log Locally

```bash
# Print to stdout
python ci_cd/scripts/log_components.py

# Save to a file
python ci_cd/scripts/log_components.py --output component_log.json
```

The JSON output lists every component used by every template:

```json
[
  {
    "template": "customer_support",
    "components": {
      "nlp": "components.nlp.text_processor",
      "memory": "components.memory.state_store",
      "decision": "components.decision.rule_engine"
    }
  }
]
```

---

## 11. Glossary

| Term | Definition |
|---|---|
| **Action** | The handler function called when a decision rule matches (e.g. `"transfer_to_human_agent"`). |
| **Bot** | A single deployed agent that receives messages, processes them through NLP → Memory → Decision, and triggers an action. |
| **Component** | A self-contained module (NLP, Memory, Decision) that performs one part of a bot's job. |
| **Condition** | A Python-like expression in a decision rule that is evaluated against the current conversation context. |
| **Coordinator** | The strategy used by a swarm to pick which bot handles each incoming task. |
| **Entity** | A structured piece of information extracted from a message (e.g. a date, a product name, or an order number). |
| **Intent** | The goal or meaning behind a user's message, matched by trigger phrases you define in `bot.yaml`. |
| **Manifest** | Another word for `bot.yaml` — the file that defines all settings for a bot. |
| **Replica** | One running instance of a bot. Setting `replicas: 2` runs two identical instances for redundancy and throughput. |
| **Swarm** | Two or more bots working together under a shared coordinator. |
| **Template** | A pre-built, ready-to-customise bot blueprint stored under `templates/`. |
| **TTL (Time To Live)** | How long (in seconds) a memory session is kept before expiring. |
| **Transparency Log** | A structured JSON record of which components each deployed template uses, generated automatically after every deploy. |

---

## 12. Frequently Asked Questions

**Q: Do I need to write any Python code to build a bot?**  
A: Not for most use cases. Editing `bot.yaml` is enough to define intents, rules, and deployment settings. Python code is only needed if you want to add a custom component or extension.

**Q: What's the difference between a template and a bot?**  
A: A **template** is the blueprint (the `bot.yaml` file and its documentation). A **bot** is a named, deployed instance created from that template using `python -m factory generate`.

**Q: Can I use more than one cloud provider at once?**  
A: Each bot deploys to a single `target` at a time. However, different bots in a swarm can each target a different cloud.

**Q: How do I update a bot after it's deployed?**  
A: Edit `bot.yaml`, commit and push your changes, then re-run the **Deploy Bot / Swarm** GitHub Actions workflow (or run `python -m factory deploy` again).

**Q: Where are credentials stored?**  
A: Credentials are **never** stored in `bot.yaml` or committed to the repository. They are read at runtime from environment variables (`ALLBOTS_API_KEY`, `AWS_ACCESS_KEY_ID`, etc.) or GitHub Actions secrets.

**Q: The validation script says my template is invalid. What do I do?**  
A: The error message will name the missing or incorrect field. Check that your `bot.yaml` contains all required fields: `name`, `version`, `description`, `components`, and `deployment`.

**Q: How do I add a new intent to an existing bot?**  
A: Open the template's `bot.yaml`, add a new key under `components.nlp.intents`, list its trigger phrases, and add a matching rule under `components.decision.rules`. Then redeploy.
