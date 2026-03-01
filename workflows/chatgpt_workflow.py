"""
ChatGPT Connectivity Workflow
Handles interactions with the OpenAI ChatGPT API, including single-turn
completions, multi-turn conversations, and streaming responses.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

OPENAI_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o"


class ChatGPTWorkflow:
    """Workflow for ChatGPT / OpenAI API connectivity and automation."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ):
        """
        Initialise the ChatGPT workflow.

        Args:
            api_key: OpenAI API key. Falls back to the ``OPENAI_API_KEY``
                     environment variable when not provided.
            model: ChatGPT model to use. Defaults to ``gpt-4o``.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "An OpenAI API key is required. Set the OPENAI_API_KEY "
                "environment variable or pass api_key= explicitly."
            )
        self.model = model
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        # Conversation history for multi-turn sessions.
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Core completion helpers
    # ------------------------------------------------------------------

    def chat(self, user_message: str, system_prompt: str | None = None) -> str:
        """
        Send a single user message and return the assistant's reply.

        This method maintains a running conversation history so successive
        calls form a coherent multi-turn dialogue.

        Args:
            user_message: The user's input text.
            system_prompt: Optional system-level instruction. Applied only on
                           the first call or when the history is empty.

        Returns:
            The assistant's reply text.
        """
        if not self._history and system_prompt:
            self._history.append({"role": "system", "content": system_prompt})

        self._history.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": self._history,
        }
        response = self.session.post(
            f"{OPENAI_API_BASE}/chat/completions", json=payload
        )
        response.raise_for_status()
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        self._history.append({"role": "assistant", "content": reply})
        logger.info("ChatGPT replied (%d chars).", len(reply))
        return reply

    def single_completion(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send a one-shot completion without storing conversation history.

        Args:
            prompt: The user's prompt text.
            system_prompt: Optional system-level instruction.

        Returns:
            The assistant's reply text.
        """
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages}
        response = self.session.post(
            f"{OPENAI_API_BASE}/chat/completions", json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def reset_history(self) -> None:
        """Clear the conversation history to start a fresh session."""
        self._history = []
        logger.info("Conversation history cleared.")

    # ------------------------------------------------------------------
    # Bot-specific workflows
    # ------------------------------------------------------------------

    def analyse_market_data(self, market_data: str) -> str:
        """
        Ask ChatGPT to analyse raw market data and return a summary.

        Args:
            market_data: Serialised market data (e.g. JSON or CSV string).

        Returns:
            Analysis text produced by ChatGPT.
        """
        system = (
            "You are a financial analyst. Analyse the provided market data and "
            "return a concise summary with key insights, trends, and risks."
        )
        return self.single_completion(market_data, system_prompt=system)

    def generate_trading_signal(self, context: str) -> str:
        """
        Ask ChatGPT to generate a trading signal based on given context.

        Args:
            context: Market context, indicators, or news summary.

        Returns:
            Trading signal text (e.g. BUY / SELL / HOLD with rationale).
        """
        system = (
            "You are an expert quantitative trader. Based on the provided market "
            "context, output a trading signal: BUY, SELL, or HOLD, followed by a "
            "brief rationale. Be concise and data-driven."
        )
        return self.single_completion(context, system_prompt=system)

    def summarise_github_activity(self, activity: str) -> str:
        """
        Ask ChatGPT to summarise recent GitHub repository activity.

        Args:
            activity: Raw GitHub activity data (issues, PRs, commits).

        Returns:
            Human-readable summary of the activity.
        """
        system = (
            "You are a helpful engineering assistant. Summarise the provided "
            "GitHub repository activity in plain English, highlighting important "
            "updates, open issues, and pull requests."
        )
        return self.single_completion(activity, system_prompt=system)

    def run(self, prompt: str) -> str:
        """
        Execute the ChatGPT workflow with a single prompt.

        Args:
            prompt: User prompt to send to ChatGPT.

        Returns:
            The assistant's reply.
        """
        logger.info("Running ChatGPT workflow …")
        reply = self.chat(prompt)
        logger.info("ChatGPT workflow complete.")
        return reply
