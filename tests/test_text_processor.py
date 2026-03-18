"""Tests for components/nlp/text_processor.py."""

from __future__ import annotations

from components.nlp.text_processor import detect_intent, extract_entities, tokenize


class TestTokenize:
    def test_basic_split(self):
        assert tokenize("hello world") == ["hello", "world"]

    def test_leading_trailing_whitespace(self):
        assert tokenize("  foo bar  ") == ["foo", "bar"]

    def test_single_word(self):
        assert tokenize("hello") == ["hello"]

    def test_empty_string(self):
        assert tokenize("") == []

    def test_multiple_spaces_between_words(self):
        assert tokenize("a  b   c") == ["a", "b", "c"]


class TestDetectIntent:
    INTENTS = {
        "greeting": ["hello", "hi", "hey"],
        "farewell": ["bye", "goodbye"],
        "help": ["help", "support"],
    }

    def test_exact_keyword_match(self):
        assert detect_intent("hello there", self.INTENTS) == "greeting"

    def test_case_insensitive(self):
        assert detect_intent("HELLO there", self.INTENTS) == "greeting"

    def test_substring_match(self):
        assert detect_intent("I need some help please", self.INTENTS) == "help"

    def test_no_match_returns_none(self):
        assert detect_intent("unrelated text", self.INTENTS) is None

    def test_empty_text(self):
        assert detect_intent("", self.INTENTS) is None

    def test_empty_intents(self):
        assert detect_intent("hello", {}) is None

    def test_first_match_wins(self):
        # Both "hello" (greeting) and "bye" (farewell) present; greeting defined first
        result = detect_intent("hello bye", self.INTENTS)
        assert result == "greeting"

    def test_farewell_keyword(self):
        assert detect_intent("goodbye everyone", self.INTENTS) == "farewell"


class TestExtractEntities:
    PATTERNS = {
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "number": r"\d+",
    }

    def test_extracts_email(self):
        result = extract_entities("Contact us at test@example.com today", self.PATTERNS)
        assert result["email"] == "test@example.com"

    def test_extracts_number(self):
        result = extract_entities("Order 42 is ready", self.PATTERNS)
        assert result["number"] == "42"

    def test_no_match_key_absent(self):
        result = extract_entities("no entities here", self.PATTERNS)
        assert result == {}

    def test_multiple_entities(self):
        result = extract_entities("Send 5 items to user@test.org", self.PATTERNS)
        assert result["number"] == "5"
        assert result["email"] == "user@test.org"

    def test_case_insensitive_pattern(self):
        patterns = {"word": r"HELLO"}
        result = extract_entities("hello world", patterns)
        assert "word" in result

    def test_empty_text(self):
        result = extract_entities("", self.PATTERNS)
        assert result == {}

    def test_empty_patterns(self):
        result = extract_entities("some text", {})
        assert result == {}
