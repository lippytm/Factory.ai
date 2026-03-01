# CI/CD Scripts

This directory contains helper scripts used by the Factory.ai GitHub Actions
workflows.

| Script | Purpose |
|---|---|
| `validate_templates.py` | Validate every `bot.yaml` manifest in `templates/`. Exits non-zero on failure. |
| `log_components.py` | Emit a structured JSON report of components used by each template (transparency log). |

## Running Locally

```bash
# Validate all templates
python ci_cd/scripts/validate_templates.py

# Print component transparency log
python ci_cd/scripts/log_components.py

# Write component log to a file
python ci_cd/scripts/log_components.py --output component_log.json
```

Both scripts require **PyYAML**:

```bash
pip install pyyaml
```
