"""
Rule-based decision engine for Factory.ai bots.

Provides a lightweight :class:`RuleEngine` that evaluates an ordered list of
condition/action pairs and returns the first matching action.
"""

from __future__ import annotations

from typing import Any, Callable


# A rule is a tuple of (condition_callable, action_callable).
Rule = tuple[Callable[[dict[str, Any]], bool], Callable[[dict[str, Any]], Any]]


class RuleEngine:
    """Evaluate an ordered set of rules against a context dictionary.

    Parameters
    ----------
    rules:
        Ordered list of ``(condition, action)`` callables.  Each
        *condition* receives the context dict and returns a bool; each
        *action* receives the context dict and returns the result.
    """

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self._rules: list[Rule] = list(rules or [])

    def add_rule(self, condition: Callable, action: Callable) -> None:
        """Append a new rule to the end of the rule list."""
        self._rules.append((condition, action))

    def evaluate(self, context: dict[str, Any]) -> Any:
        """Return the action result for the first matching rule.

        Parameters
        ----------
        context:
            Arbitrary key-value context passed to each rule condition.

        Returns
        -------
        Any
            Result of the matched action callable, or ``None`` if no
            rule condition evaluates to ``True``.
        """
        for condition, action in self._rules:
            if condition(context):
                return action(context)
        return None
