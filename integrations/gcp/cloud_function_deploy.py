"""
GCP integration helpers for Factory.ai.

Provides a lightweight wrapper for deploying bots as Google Cloud Functions.

``google-cloud-functions`` is an optional dependency; import errors are
caught gracefully so the rest of Factory.ai continues to function when
GCP is not enabled.
"""

from __future__ import annotations

from typing import Any


def deploy_cloud_function(
    project_id: str,
    region: str,
    function_name: str,
    zip_bytes: bytes,
    entry_point: str = "handle",
    runtime: str = "python311",
) -> dict[str, Any]:
    """Deploy a Cloud Function to GCP.

    Parameters
    ----------
    project_id:
        GCP project ID.
    region:
        Cloud Function region (e.g. ``"us-central1"``).
    function_name:
        Name for the Cloud Function.
    zip_bytes:
        Zipped source package bytes.
    entry_point:
        Function entry-point name inside the source package.
    runtime:
        Cloud Functions runtime identifier.

    Returns
    -------
    dict[str, Any]
        Deployment operation metadata.

    Notes
    -----
    Requires ``google-cloud-functions``. Install with::

        pip install google-cloud-functions
    """
    try:
        from google.cloud import functions_v2 as functions  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "google-cloud-functions is required for GCP integration. "
            "Install it with: pip install google-cloud-functions"
        ) from exc

    client = functions.FunctionServiceClient()
    parent = f"projects/{project_id}/locations/{region}"
    function_path = f"{parent}/functions/{function_name}"

    # Upload zip_bytes to GCS before referencing it in the source.
    # The Cloud Functions v2 API requires source code to be in a GCS bucket.
    # This stub returns a note explaining the required steps; callers must:
    #   1. Upload zip_bytes to a GCS bucket (e.g. via google-cloud-storage).
    #   2. Set storage_source.bucket / storage_source.object below.
    # For production use, replace this stub with a full GCS upload + deploy.
    storage_source = functions.StorageSource(
        # bucket="your-gcs-bucket",
        # object_="path/to/function.zip",
    )

    func = functions.Function(
        name=function_path,
        build_config=functions.BuildConfig(
            entry_point=entry_point,
            runtime=runtime,
            source=functions.Source(storage_source=storage_source),
        ),
    )

    operation = client.create_function(
        parent=parent, function=func, function_id=function_name
    )
    result = operation.result()
    return {
        "name": result.name,
        "state": str(result.state),
        "zip_size": len(zip_bytes),
        "note": (
            "zip_bytes must be uploaded to a GCS bucket first. "
            "Set storage_source.bucket and storage_source.object in the stub."
        ),
    }
