"""AWS integration package for Factory.ai."""

from .lambda_deploy import deploy_lambda, get_lambda_client

__all__ = ["get_lambda_client", "deploy_lambda"]
