"""
Tests for ChatGPTWorkflow.

All HTTP calls are intercepted with unittest.mock.
"""

from unittest.mock import MagicMock, patch

import pytest

from workflows.chatgpt_workflow import ChatGPTWorkflow


@pytest.fixture
def workflow():
    return ChatGPTWorkflow(api_key="test-api-key")


def _openai_response(content):
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status.return_value = None
    mock.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": content}}]
    }
    return mock


class TestChatGPTWorkflow:
    def test_init_requires_api_key(self):
        with pytest.raises(ValueError, match="OpenAI API key"):
            with patch.dict("os.environ", {}, clear=True):
                ChatGPTWorkflow(api_key=None)

    def test_init_reads_env_key(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}):
            wf = ChatGPTWorkflow()
        assert wf.api_key == "env-key"

    def test_chat_returns_reply(self, workflow):
        with patch.object(
            workflow.session, "post", return_value=_openai_response("Hello!")
        ):
            reply = workflow.chat("Hi")
        assert reply == "Hello!"

    def test_chat_builds_history(self, workflow):
        with patch.object(
            workflow.session,
            "post",
            side_effect=[
                _openai_response("First reply"),
                _openai_response("Second reply"),
            ],
        ):
            workflow.chat("Message 1")
            workflow.chat("Message 2")
        # history: system (if any) + 2 user + 2 assistant = 4 entries
        user_messages = [m for m in workflow._history if m["role"] == "user"]
        assert len(user_messages) == 2

    def test_system_prompt_added_on_first_call(self, workflow):
        with patch.object(
            workflow.session, "post", return_value=_openai_response("OK")
        ):
            workflow.chat("Hello", system_prompt="You are helpful.")
        assert workflow._history[0]["role"] == "system"
        assert workflow._history[0]["content"] == "You are helpful."

    def test_reset_history(self, workflow):
        with patch.object(
            workflow.session, "post", return_value=_openai_response("Hi")
        ):
            workflow.chat("Hello")
        assert len(workflow._history) > 0
        workflow.reset_history()
        assert workflow._history == []

    def test_single_completion_no_history(self, workflow):
        with patch.object(
            workflow.session, "post", return_value=_openai_response("Done")
        ) as mock_post:
            reply = workflow.single_completion("One-shot prompt")
        assert reply == "Done"
        # History should remain untouched (empty)
        assert workflow._history == []

    def test_analyse_market_data(self, workflow):
        with patch.object(
            workflow.session,
            "post",
            return_value=_openai_response("Market looks bullish."),
        ):
            result = workflow.analyse_market_data('{"price": 50000}')
        assert "bullish" in result

    def test_generate_trading_signal(self, workflow):
        with patch.object(
            workflow.session,
            "post",
            return_value=_openai_response("BUY: momentum is strong."),
        ):
            result = workflow.generate_trading_signal("RSI=70, MACD positive")
        assert result.startswith("BUY")

    def test_summarise_github_activity(self, workflow):
        with patch.object(
            workflow.session,
            "post",
            return_value=_openai_response("3 open issues, 1 PR merged."),
        ):
            result = workflow.summarise_github_activity("issues: 3, prs: 1")
        assert "issues" in result

    def test_run(self, workflow):
        with patch.object(
            workflow.session, "post", return_value=_openai_response("All good.")
        ):
            reply = workflow.run("How are you?")
        assert reply == "All good."
