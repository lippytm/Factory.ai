"""
AWS integration helpers for Factory.ai.

Provides convenience wrappers for deploying bots to AWS Lambda and
publishing events to SNS/SQS via ``boto3``.

``boto3`` is an optional dependency; import errors are caught gracefully
so the rest of Factory.ai continues to function when AWS is not enabled.
"""

from __future__ import annotations

from typing import Any

try:
    import boto3  # type: ignore[import]
    _BOTO3_AVAILABLE = True
except ImportError:
    _BOTO3_AVAILABLE = False


def get_lambda_client(region: str = "us-east-1") -> Any:
    """Return a ``boto3`` Lambda client for *region*.

    Raises
    ------
    ImportError
        If ``boto3`` is not installed.
    """
    if not _BOTO3_AVAILABLE:
        raise ImportError(
            "boto3 is required for AWS integration. "
            "Install it with: pip install boto3"
        )
    return boto3.client("lambda", region_name=region)


def deploy_lambda(
    function_name: str,
    zip_bytes: bytes,
    role_arn: str,
    handler: str = "handler.handle",
    runtime: str = "python3.11",
    region: str = "us-east-1",
) -> dict[str, Any]:
    """Create or update a Lambda function with the supplied *zip_bytes*.

    Parameters
    ----------
    function_name:
        Name for the Lambda function.
    zip_bytes:
        Zipped deployment package bytes.
    role_arn:
        IAM role ARN the function will assume.
    handler:
        Module and function path inside the zip (e.g. ``"handler.handle"``).
    runtime:
        Lambda runtime identifier.
    region:
        AWS region to deploy into.

    Returns
    -------
    dict[str, Any]
        Raw boto3 API response.
    """
    client = get_lambda_client(region)
    try:
        response: dict[str, Any] = client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes,
        )
    except client.exceptions.ResourceNotFoundException:
        response = client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zip_bytes},
        )
    return response
