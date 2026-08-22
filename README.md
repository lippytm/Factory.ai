# Factory.ai

**Factory.ai** is the central bot, component, workflow, and swarm creation engine for the lippytm ecosystem. It provides a modular platform for generating industry-specific bots, composing AI components, coordinating bounded agents, validating templates, and preparing deployable workflows across cloud environments.

---

## Prompt #11 Encyclopedia Content Factory

Factory.ai now contains the architecture specification for:

> **P-011-EEBDS-001 — Encyclopedia Educational Entertainment and Business of Businesses Delivery System**

Its purpose is to transform a valid Prompt #11 Character–Ecosystem Innovation Unit into controlled educational, story, Build Mode, Life/Business Sciences, media, business, NFT-provenance, and Quality Evidence outputs.

Core files:

- [`docs/P011-EEBDS-001-content-factory-spec.md`](docs/P011-EEBDS-001-content-factory-spec.md)
- [`templates/encyclopedia_delivery/bot.yaml`](templates/encyclopedia_delivery/bot.yaml)

The proposed pipeline covers:

1. intake and schema validation;
2. privacy routing;
3. source and truth mapping;
4. character and fiction-boundary review;
5. ecosystem mapping;
6. IF, MAYBE, WHY NOT, and DON'T DO THAT analysis;
7. curriculum design;
8. original story and worldbuilding;
9. safe Build Mode design;
10. Business of Businesses experimentation;
11. context-preserving media adaptation;
12. independent ChatGPT, Gemini/NotebookLM, and Claude/Fabric Hermes production;
13. requirements, tests, defects, RiskGate, and Quality Evidence assembly;
14. mandatory human review;
15. approved packaging, monitoring, correction, retirement, and archival stewardship.

This is an **architecture and template specification**. It does not claim that the agents, services, or routes are already deployed in production. Factory.ai cannot autonomously approve publication, commercial launch, minting, financial actions, identity cloning, voice or likeness use, medical or legal conclusions, or franchise certification.

---

## Features

- **Personalized Templates** — Pre-built, industry-specific templates that can be customized for customer support, automation, educational delivery, data pipelines, and additional workflows.
- **Modular AI Components** — Composable NLP, decision, memory, validation, quality, and integration building blocks.
- **Multi-Cloud Integration** — Connector patterns for AWS, Azure, GCP, AllBots.com, and compatible environments.
- **Swarm Orchestration** — Coordinate multiple bounded agents with explicit roles, permissions, data classes, work packets, and human review.
- **CI/CD Pipelines** — Automated testing, validation, deployment preparation, and component-usage transparency logging.
- **Content Factory Specifications** — Reusable Prompt #11 production stages for Encyclopedia characters, ecosystems, learning, stories, media, businesses, and QA.

---

## Repository Structure

```text
Factory.ai/
├── factory/                       # CLI package (`python -m factory`)
├── components/                    # Reusable base modules
│   ├── nlp/
│   ├── memory/
│   ├── decision/
│   └── extensions/
├── docs/
│   └── P011-EEBDS-001-content-factory-spec.md
├── templates/
│   ├── customer_support/
│   ├── automation/
│   └── encyclopedia_delivery/
│       └── bot.yaml
├── integrations/
│   ├── allbots/
│   ├── aws/
│   ├── azure/
│   └── gcp/
├── tests/
├── ci_cd/
├── pyproject.toml
├── requirements.txt
└── .github/workflows/
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or a compatible package manager
- Required provider credentials stored as secrets rather than committed to the repository

### Installation

```bash
git clone https://github.com/lippytm/Factory.ai.git
cd Factory.ai
pip install -r requirements.txt
```

### Generate a Bot from an Existing Implemented Template

```bash
python -m factory generate --template templates/customer_support --name "SupportBot"
python -m factory generate --template templates/automation --name "AutoBot"
```

The `encyclopedia_delivery` template added by the Prompt #11 integration is currently a workflow architecture manifest. It requires implementation, tests, security review, and HumanApprovalGate before deployment.

### Deploy a Bot or Swarm

Use approved GitHub Actions workflows or the implemented CLI only after reviewing configuration, permissions, secrets, test results, and target-environment controls.

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

Do not treat an orchestration command as authorization to publish, broadcast confidential data, spend money, mint an NFT, or pass HumanApprovalGate.

---

## Encyclopedia Factory Input Contract

A production run must begin with a valid Encyclopedia Entry Passport containing:

- entry or CEIU ID and version;
- privacy class;
- character and Character Passport references;
- ecosystems and domains;
- truth labels;
- Quantum Questions;
- learning objectives;
- story premise;
- Build Mode requirements;
- business hypothesis;
- requested media;
- model-line assignment;
- certification and RiskGate;
- human approval status and scope.

Invalid, incomplete, misrouted, or Red RiskGate work packets must be rejected or quarantined.

---

## CI/CD Workflows

| Workflow | File | Trigger |
|---|---|---|
| CI (Lint and Test) | `.github/workflows/ci.yml` | Push or PR to `main` |
| Validate Templates | `.github/workflows/validate_templates.yml` | Push or PR to `main` |
| Deploy Bot or Swarm | `.github/workflows/deploy.yml` | Manual |
| Transparency Log | `.github/workflows/transparency_log.yml` | After approved deploy |

Any future EEBDS workflow must validate schemas, permissions, privacy routing, truth labels, model-line separation, release gates, and human approval before a deployment step.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Add or update code, documentation, or templates in the appropriate directory.
3. Write or update tests.
4. Keep credentials, private keys, personal records, and restricted evidence out of commits.
5. Document agent permissions, prohibited actions, data classes, and human-approval requirements.
6. Run lint and tests locally where supported.
7. Open a pull request describing requirements, tests, risks, limitations, and rollback procedures.

### Adding a New Template

1. Create `templates/<template_name>/`.
2. Add a validated manifest.
3. Include a README explaining purpose, inputs, outputs, permissions, limitations, security, privacy, tests, and deployment status.
4. Add or update automated tests.
5. Do not describe an architecture-only manifest as implemented production code.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details. Third-party characters, brands, media, data, and dependencies may require separate permissions or licenses.
