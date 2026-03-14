# Factory.ai

**Factory.ai** is a platform for building and deploying AI-powered bots. Instead of coding a bot from scratch, you pick a ready-made template (for example, a customer-support bot or an automation bot), customise it for your needs, and deploy it to a cloud platform — all without reinventing common plumbing like natural-language understanding, memory, or decision logic.

> **New here?** Jump straight to [Quick Start](#quick-start) to have a bot running in minutes, or read [Key Concepts](#key-concepts) if you'd like to understand the big picture first.

---

## Table of Contents

1. [Key Concepts](#key-concepts)
2. [Features](#features)
3. [Repository Structure](#repository-structure)
4. [Quick Start](#quick-start)
5. [Step-by-Step Guides](#step-by-step-guides)
   - [Generate a Bot from a Template](#1-generate-a-bot-from-a-template)
   - [Customise Your Bot](#2-customise-your-bot)
   - [Deploy a Bot](#3-deploy-a-bot)
   - [Compose and Deploy a Swarm](#4-compose-and-deploy-a-swarm)
6. [CI/CD Workflows](#cicd-workflows)
7. [Contributing](#contributing)
8. [License](#license)

---

## Key Concepts

| Term | Plain-English Meaning |
|---|---|
| **Bot** | A single automated agent that understands messages, remembers context, and takes actions (e.g. answer a question, run a job). |
| **Template** | A pre-built, ready-to-customise bot blueprint (like a `customer_support` template or an `automation` template). Think of it like a starter kit. |
| **Component** | A reusable building block wired into every bot — NLP for understanding text, Memory for storing conversation state, and Decision for routing to the right action. |
| **Integration** | A connector that lets your bot talk to an external service such as AllBots.com, AWS, Azure, or GCP. |
| **Swarm** | A group of bots working together. A coordinator (round-robin, priority, or least-loaded) decides which bot in the swarm handles each task. |
| **bot.yaml** | A plain-text configuration file that describes everything about your bot: its name, components, integrations, and deployment settings. You edit this file to customise a template. |

---

## Features

- **Ready-Made Templates** — Start with a pre-built bot for customer support, automation, and more. Each template is fully documented and immediately deployable.
- **Modular Components** — Every bot is assembled from swappable building blocks: an NLP processor (understands user input), a memory adapter (remembers the conversation), and a decision/rule engine (routes to the right action).
- **Multi-Cloud Deployment** — Deploy to [AllBots.com](https://allbots.com), AWS Lambda, Azure Functions, or GCP Cloud Functions by changing a single line in `bot.yaml`.
- **Swarm Orchestration** — Run multiple bots as a team, automatically load-balancing or prioritising work across them.
- **Built-In CI/CD** — GitHub Actions workflows validate your configuration on every pull request and offer one-click deployment without any manual steps.

---

## Repository Structure

```
Factory.ai/
├── components/          # Reusable building blocks for every bot
│   ├── nlp/             #   → Understands and tokenises user messages
│   ├── memory/          #   → Stores conversation state between turns
│   ├── decision/        #   → Applies rules to decide what action to take
│   └── extensions/      #   → Optional add-ons you can enable per template
├── templates/           # Ready-to-use bot blueprints
│   ├── customer_support/#   → Handles greetings, billing, tech support, escalation
│   └── automation/      #   → Accepts commands to run, stop, and schedule jobs
├── integrations/        # Connectors to external platforms
│   ├── allbots/         #   → AllBots.com API client
│   ├── aws/             #   → AWS Lambda deployment helper
│   ├── azure/           #   → Azure Functions deployment helper
│   └── gcp/             #   → GCP Cloud Functions deployment helper
├── ci_cd/               # CI/CD helper scripts
│   ├── scripts/         #   → validate_templates.py, log_components.py
│   └── docs/            #   → Documentation for CI/CD scripts
└── .github/
    └── workflows/       # GitHub Actions definitions (validate, deploy, log)
```

---

## Quick Start

> **Prerequisites:** Python 3.10+, `pip`, and a free [AllBots.com](https://allbots.com) API key.

```bash
# 1. Clone the repository
git clone https://github.com/lippytm/Factory.ai.git
cd Factory.ai

# 2. Install dependencies
pip install pyyaml        # required for validation scripts

# 3. Validate that the built-in templates are correctly configured
python ci_cd/scripts/validate_templates.py
# Expected output: "All templates are valid."

# 4. Generate a customer-support bot
python -m factory generate --template templates/customer_support --name "SupportBot"

# 5. Deploy it
python -m factory deploy --template templates/customer_support --env production
```

That's it — your bot is live! Read on for more detail on each step.

---

## Step-by-Step Guides

### 1. Generate a Bot from a Template

Templates live in the `templates/` directory. Each template has a `bot.yaml` manifest and a `README.md` that explains its settings.

```bash
# Customer-support bot (handles greetings, billing, tech queries, escalation)
python -m factory generate \
  --template templates/customer_support \
  --name "SupportBot"

# Automation bot (runs/stops/schedules jobs via natural-language commands)
python -m factory generate \
  --template templates/automation \
  --name "AutoBot"
```

### 2. Customise Your Bot

Open the template's `bot.yaml` file and edit it to match your needs. Here are the most commonly changed settings:

```yaml
# templates/customer_support/bot.yaml (excerpt)

components:
  nlp:
    intents:
      # Add your own trigger phrases for any intent:
      billing: ["invoice", "charge", "payment", "refund", "bill"]

  memory:
    ttl_seconds: 3600   # How long (in seconds) the bot remembers the conversation.
                        # 3600 = 1 hour. Set to 86400 for 24 hours.

  decision:
    rules:
      # Each rule maps an intent to an action.
      # Add your own rules here:
      - condition: "intent == 'billing'"
        action:    "open_billing_flow"

deployment:
  target: allbots       # Where to deploy: allbots | aws | azure | gcp
  replicas: 2           # How many simultaneous instances to run
```

> See the full schema reference in [docs/user_guide.md](docs/user_guide.md).

### 3. Deploy a Bot

**Option A — One-click via GitHub Actions (recommended):**

1. Go to the **Actions** tab in this repository.
2. Select the **Deploy Bot / Swarm** workflow.
3. Click **Run workflow**, fill in the template name, bot name, and target environment, then click **Run workflow** again.

**Option B — CLI:**

```bash
python -m factory deploy \
  --template templates/customer_support \
  --env production
```

### 4. Compose and Deploy a Swarm

A swarm lets you run several bots together. The `--coordinator` flag controls how incoming tasks are routed:

| Strategy | Behaviour |
|---|---|
| `round-robin` | Sends each new task to the next bot in turn (even distribution). |
| `priority` | Always sends to the highest-priority bot first. |
| `least-loaded` | Sends to whichever bot currently has the fewest active tasks. |

```bash
python -m factory swarm \
  --bots "SupportBot,AutoBot" \
  --coordinator round-robin \
  --env production
```

---

## CI/CD Workflows

Three GitHub Actions workflows are included out of the box:

| Workflow | When it runs | What it does |
|---|---|---|
| **Validate Templates** | Every push / PR touching `templates/` | Checks every `bot.yaml` for required fields and correct structure. Fails the PR if a template is misconfigured. |
| **Deploy Bot / Swarm** | Manually triggered | Builds and deploys a bot or swarm to the chosen environment. |
| **Transparency Log** | Automatically after every deploy | Generates a structured JSON report listing every component used, for auditing and governance. |

To run the validation check locally before opening a pull request:

```bash
python ci_cd/scripts/validate_templates.py
```

---

## Contributing

Contributions are welcome! Here is the workflow:

1. **Fork** this repository and create a feature branch:
   ```bash
   git checkout -b feat/your-feature
   ```
2. Make your changes under the relevant directory (`components/`, `templates/`, `integrations/`).
3. Validate your changes locally:
   ```bash
   python ci_cd/scripts/validate_templates.py
   ```
4. Open a Pull Request against `main` with a clear description of what you changed and why.

### Adding a New Template

1. Create a directory under `templates/<your_industry>/`.
2. Copy an existing `bot.yaml` as a starting point and update it for your use case.
3. Add a `README.md` (see `templates/customer_support/README.md` as a model) explaining what the bot does and how to configure it.
4. The **Validate Templates** CI check will run automatically when you open a pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

