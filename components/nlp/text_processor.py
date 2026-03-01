"""
NLP text processing utilities for Factory.ai bots.

Provides tokenisation, intent detection, and entity extraction helpers
that can be composed into any bot template.
"""

from __future__ import annotations

import re
from typing import Any


def tokenize(text: str) -> list[str]:
    """Return a simple whitespace-split token list for *text*."""
    return text.strip().split()


def detect_intent(text: str, intents: dict[str, list[str]]) -> str | None:
    """Return the first intent key whose keyword list has a match in *text*.

    Parameters
    ----------
    text:
        Raw user input.
    intents:
        Mapping of intent name → list of trigger keywords.

    Returns
    -------
    str | None
        Matched intent name, or ``None`` if no match found.
    """
    lower = text.lower()
    for intent, keywords in intents.items():
        if any(kw.lower() in lower for kw in keywords):
            return intent
    return None


def extract_entities(text: str, entity_patterns: dict[str, str]) -> dict[str, Any]:
    """Extract named entities from *text* using simple regex matching.

    Parameters
    ----------
    text:
        Raw user input.
    entity_patterns:
        Mapping of entity name → regex pattern to search for.

    Returns
    -------
    dict[str, Any]
        Extracted entity values keyed by entity name.
    """
    results: dict[str, Any] = {}
    for entity, pattern in entity_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[entity] = match.group(0)
    return results
