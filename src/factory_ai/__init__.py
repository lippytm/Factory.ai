"""Factory.ai - Connection workflows for GitHub, ChatGPT, AllBots.com, and more."""

from .workflow import ConnectionWorkflow
from .connections import GitHubConnection, OpenAIConnection, AllBotsConnection

__all__ = ["ConnectionWorkflow", "GitHubConnection", "OpenAIConnection", "AllBotsConnection"]
__version__ = "0.1.0"
