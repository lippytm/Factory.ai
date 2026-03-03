"""
Brain Kit – pre-assembled AI brain for Factory.ai bots.

A :class:`BrainKit` bundles the three core cognitive components —
:mod:`components.nlp.text_processor`, :mod:`components.memory.state_store`,
and :mod:`components.decision.rule_engine` — into a single, ready-to-use
"brain" that any bot template can attach to.

Brain Kits are a cross-repository standard in the lippytm ecosystem: every
repository that builds on Factory.ai can declare a ``brain_kit`` section in
its ``bot.yaml`` manifest and receive a fully wired brain at runtime.

Example usage::

    from components.brain_kit import BrainKit

    brain = BrainKit(
        intents={
            "greeting": ["hello", "hi"],
            "farewell": ["bye", "goodbye"],
        }
    )
    result = brain.process("Hello there!")
    print(result)  # {"intent": "greeting", "entities": {}, "action": None}
"""

from __future__ import annotations

from typing import Any

from components.decision.rule_engine import Rule, RuleEngine
from components.memory.state_store import StateStore
from components.nlp.text_processor import detect_intent, extract_entities, tokenize


class BrainKit:
    """Pre-assembled cognitive brain for a Factory.ai bot.

    Parameters
    ----------
    intents:
        Mapping of intent name → list of trigger keywords, forwarded to
        :func:`~components.nlp.text_processor.detect_intent`.
    entity_patterns:
        Mapping of entity name → regex pattern, forwarded to
        :func:`~components.nlp.text_processor.extract_entities`.
    rules:
        Ordered list of :data:`~components.decision.rule_engine.Rule` pairs
        passed to :class:`~components.decision.rule_engine.RuleEngine`.
    initial_state:
        Optional seed values for the :class:`~components.memory.state_store.StateStore`.
    """

    def __init__(
        self,
        intents: dict[str, list[str]] | None = None,
        entity_patterns: dict[str, str] | None = None,
        rules: list[Rule] | None = None,
        initial_state: dict[str, Any] | None = None,
    ) -> None:
        self.intents: dict[str, list[str]] = intents or {}
        self.entity_patterns: dict[str, str] = entity_patterns or {}
        self.memory = StateStore(initial=initial_state)
        self.decision = RuleEngine(rules=rules)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, text: str) -> dict[str, Any]:
        """Run *text* through the full NLP → memory → decision pipeline.

        Parameters
        ----------
        text:
            Raw user or event input.

        Returns
        -------
        dict[str, Any]
            A result dict with keys:

            * ``"tokens"`` – list of whitespace-split tokens.
            * ``"intent"`` – matched intent name, or ``None``.
            * ``"entities"`` – dict of extracted entity values.
            * ``"action"`` – return value of the first matching rule, or
              ``None`` if no rule fired.
        """
        tokens = tokenize(text)
        intent = detect_intent(text, self.intents)
        entities = extract_entities(text, self.entity_patterns)

        # Persist current turn context in memory for downstream rules.
        self.memory.set("last_text", text)
        self.memory.set("last_intent", intent)
        self.memory.set("last_entities", entities)

        context: dict[str, Any] = {
            "text": text,
            "tokens": tokens,
            "intent": intent,
            "entities": entities,
            "memory": self.memory,
        }
        action = self.decision.evaluate(context)

        return {
            "tokens": tokens,
            "intent": intent,
            "entities": entities,
            "action": action,
        }

    def reset(self) -> None:
        """Clear the memory store between independent sessions."""
        self.memory.clear()
