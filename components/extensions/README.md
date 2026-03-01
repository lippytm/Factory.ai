# Extensions

This directory contains optional add-on modules that augment the base
Factory.ai bot components.  Extensions are self-contained packages that
can be enabled per-template via the `bot.yaml` manifest.

## Creating an Extension

1. Create a new sub-directory: `components/extensions/<extension_name>/`.
2. Add an `__init__.py` that exposes the extension's public API.
3. Reference the extension in your template's `bot.yaml` under the
   `extensions:` key.

## Available Extensions

| Extension | Description |
|---|---|
| *(none yet — add yours!)* | |
