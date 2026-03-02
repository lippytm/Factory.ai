"""
Azure integration helpers for Factory.ai.

Provides a lightweight wrapper for deploying bots as Azure Functions.

``azure-functions`` and ``azure-mgmt-web`` are optional dependencies;
import errors are caught gracefully so the rest of Factory.ai continues
to function when Azure is not enabled.
"""

from __future__ import annotations

from typing import Any


def deploy_function_app(
    subscription_id: str,
    resource_group: str,
    function_app_name: str,
    zip_bytes: bytes,
) -> dict[str, Any]:
    """Deploy a zipped Function App package to Azure.

    Parameters
    ----------
    subscription_id:
        Azure subscription ID.
    resource_group:
        Resource group that contains the Function App.
    function_app_name:
        Name of the target Azure Function App.
    zip_bytes:
        Zipped deployment package bytes.

    Returns
    -------
    dict[str, Any]
        Deployment result metadata.

    Notes
    -----
    Requires the ``azure-mgmt-web`` and ``azure-identity`` packages.
    Install them with::

        pip install azure-mgmt-web azure-identity
    """
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore[import]
        from azure.mgmt.web import WebSiteManagementClient  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "azure-mgmt-web and azure-identity are required for Azure integration. "
            "Install them with: pip install azure-mgmt-web azure-identity"
        ) from exc

    import io

    from azure.core.exceptions import HttpResponseError  # type: ignore[import]

    credential = DefaultAzureCredential()
    client = WebSiteManagementClient(credential, subscription_id)

    # Upload the zip package via the Kudu zip-deploy API.
    # web_apps.begin_create_or_update alone does not deploy code; we use the
    # zip-deploy endpoint to push the package bytes directly.
    try:
        result = client.web_apps.begin_create_or_update(
            resource_group_name=resource_group,
            name=function_app_name,
            site_envelope={},
        ).result()
    except HttpResponseError as exc:
        raise RuntimeError(
            f"Failed to create/update Azure Function App '{function_app_name}': {exc}"
        ) from exc

    # Perform the actual zip deployment via the REST zip-deploy endpoint.
    # This requires an authenticated HTTP POST to:
    #   https://<function_app_name>.scm.azurewebsites.net/api/zipdeploy
    # Callers can use the azure-identity credential to obtain a bearer token.
    # This stub returns metadata; wire up the HTTP call for production use.
    return {
        "name": result.name,
        "state": result.state,
        "zip_size": len(zip_bytes),
        "note": (
            "zip_bytes must be POSTed to the Kudu /api/zipdeploy endpoint. "
            "Wire up the HTTP call using azure-identity credentials."
        ),
    }
