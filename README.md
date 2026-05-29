# Factory.ai

**Factory.ai** is the central bot and swarm creation engine for the [AllBots](https://allbots.com) ecosystem. It provides a modular, extensible platform for generating industry-specific bots, composing AI components, and deploying swarms of coordinated agents across cloud environments.

---

## Features

- **Personalized Templates** — Pre-built, industry-specific bot templates (customer support, automation, data pipelines, and more) that can be customized to fit your needs.
- **Modular AI Components** — Composable building blocks (NLP processors, decision engines, memory modules, integrations) that snap together to form complete bots.
- **Multi-Cloud Integration** — First-class connectors for AWS, Azure, GCP, and AllBots.com so you can deploy wherever your workload lives.
- **Cross-Chain Agent Prototype** — Quote-first MoonPay Trade integration template for AI agents that need human-approved cross-chain execution across 200+ chains/protocols.
- **Swarm Orchestration** — Coordinate multiple bots as a unified swarm with shared context and task delegation.
- **CI/CD Pipelines** — Built-in GitHub Actions workflows for automated testing, validation, one-click deployment, and full component-usage transparency logging.

---

## Repository Structure

```
Factory.ai/
├── factory/             # CLI package (`python -m factory`)
├── components/          # Reusable base modules for bot construction
│   ├── nlp/             # Natural-language processing helpers
│   ├── memory/          # Conversation and state memory adapters
│   ├── decision/        # Decision-tree and rule-engine modules
│   └── extensions/      # Optional add-on capabilities
├── templates/           # Pre-designed industry-specific bot templates
│   ├── customer_support/
│   └── automation/
├── integrations/        # Connectors to AllBots.com, cloud providers, and Web3 rails
│   ├── allbots/
│   ├── aws/
│   ├── azure/
│   ├── gcp/
│   └── moonpay_trade/
├── tests/               # Unit test suite (pytest)
├── ci_cd/               # Reusable CI/CD scripts and helpers
│   ├── scripts/
│   └── docs/
├── pyproject.toml       # Project metadata and tool configuration
├── requirements.txt     # Runtime and optional dependencies
└── .github/
    └── workflows/       # GitHub Actions workflow definitions
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or a compatible package manager
- A configured AllBots API key (set as `ALLBOTS_API_KEY` in your environment or repository secrets)

### Installation

```bash
git clone https://github.com/lippytm/Factory.ai.git
cd Factory.ai
pip install -r requirements.txt
```

### Generate a Bot from a Template

```bash
# Customer-support bot
python -m factory generate --template templates/customer_support --name "SupportBot"

# Automation bot
python -m factory generate --template templates/automation --name "AutoBot"
```

### Deploy a Bot / Swarm

Use the built-in GitHub Actions workflow for one-click deployment:

1. Go to **Actions → Deploy Bot / Swarm**.
2. Select the template and target environment.
3. Click **Run workflow**.

Or trigger via the CLI:

```bash
python -m factory deploy --template templates/customer_support --env production
```

### Compose a Swarm

```bash
python -m factory swarm \
  --bots "SupportBot,AutoBot" \
  --coordinator round-robin \
  --env production
```

### Preview a Cross-Chain Agent

```bash
python -m factory generate \
  --template templates/cross_chain_agent \
  --name "MoonPayTradeAgent"
```

The cross-chain template defaults to dry-run mode and requires human approval before live MoonPay Trade execution.

---

## CI/CD Workflows

| Workflow | File | Trigger |
|---|---|---|
| CI (Lint & Test) | `.github/workflows/ci.yml` | Push / PR to `main` |
| Validate Templates | `.github/workflows/validate_templates.yml` | Push / PR to `main` |
| Deploy Bot / Swarm | `.github/workflows/deploy.yml` | Manual (`workflow_dispatch`) |
| Transparency Log | `.github/workflows/transparency_log.yml` | After every deploy |

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository and create a feature branch: `git checkout -b feat/your-feature`.
2. Add or update code under the relevant directory (`components/`, `templates/`, `integrations/`).
3. Write or update tests in the corresponding `tests/` sub-directory (if present).
4. Ensure the **CI** check passes locally:
   ```bash
   flake8 .
   pytest
   ```
5. Open a Pull Request against `main` with a clear description of your changes.

### Adding a New Template

1. Create a new directory under `templates/<industry>/`.
2. Add a `bot.yaml` manifest (see `templates/customer_support/bot.yaml` for the schema).
3. Include a `README.md` explaining the template's purpose and configuration options.
4. The CI pipeline will automatically validate and log the new template's components.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

