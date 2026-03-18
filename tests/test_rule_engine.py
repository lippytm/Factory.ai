"""Tests for components/decision/rule_engine.py."""

from __future__ import annotations

from components.decision.rule_engine import RuleEngine


def _always_true(ctx):
    return True


def _always_false(ctx):
    return False


def _echo_action(ctx):
    return ctx.get("value")


class TestRuleEngine:
    def test_no_rules_returns_none(self):
        engine = RuleEngine()
        assert engine.evaluate({}) is None

    def test_matching_rule_returns_action_result(self):
        engine = RuleEngine([(_always_true, _echo_action)])
        result = engine.evaluate({"value": "hello"})
        assert result == "hello"

    def test_non_matching_rule_returns_none(self):
        engine = RuleEngine([(_always_false, _echo_action)])
        assert engine.evaluate({"value": "x"}) is None

    def test_first_matching_rule_wins(self):
        first_action = lambda ctx: "first"  # noqa: E731
        second_action = lambda ctx: "second"  # noqa: E731
        engine = RuleEngine([
            (_always_true, first_action),
            (_always_true, second_action),
        ])
        assert engine.evaluate({}) == "first"

    def test_skips_non_matching_rules(self):
        second_action = lambda ctx: "second"  # noqa: E731
        engine = RuleEngine([
            (_always_false, lambda ctx: "first"),
            (_always_true, second_action),
        ])
        assert engine.evaluate({}) == "second"

    def test_add_rule_appended(self):
        engine = RuleEngine()
        engine.add_rule(_always_true, _echo_action)
        assert engine.evaluate({"value": 42}) == 42

    def test_add_rule_after_init(self):
        engine = RuleEngine([(_always_false, lambda ctx: "skip")])
        engine.add_rule(_always_true, lambda ctx: "added")
        assert engine.evaluate({}) == "added"

    def test_context_passed_to_condition(self):
        condition = lambda ctx: ctx.get("flag") is True  # noqa: E731
        action = lambda ctx: "matched"  # noqa: E731
        engine = RuleEngine([(condition, action)])
        assert engine.evaluate({"flag": False}) is None
        assert engine.evaluate({"flag": True}) == "matched"

    def test_action_receives_context(self):
        action = lambda ctx: ctx["x"] + ctx["y"]  # noqa: E731
        engine = RuleEngine([(_always_true, action)])
        assert engine.evaluate({"x": 3, "y": 4}) == 7

    def test_none_rules_treated_as_empty(self):
        engine = RuleEngine(None)
        assert engine.evaluate({}) is None
