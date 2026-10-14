import os
import json
import logging
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from django.conf import settings

logger = logging.getLogger(__name__)


def is_supabase_configured():
    """Check if Supabase Storage environment variables are configured."""
    return bool(
        getattr(settings, "SUPABASE_URL", None)
        and getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
        and getattr(settings, "SUPABASE_STORAGE_BUCKET", None)
    )


def get_supabase_public_url(filename):
    """Generate public access URL for an object in Supabase Storage."""
    if not is_supabase_configured():
        return ""
    base_url = settings.SUPABASE_URL.rstrip("/")
    bucket = settings.SUPABASE_STORAGE_BUCKET
    return f"{base_url}/storage/v1/object/public/{bucket}/{filename}"


def upload_file_to_supabase(file_bytes, filename, content_type="application/octet-stream"):
    """
    Upload a file directly to the configured Supabase Storage Bucket.
    Returns (success: bool, url_or_error: str)
    """
    if not is_supabase_configured():
        return False, "Supabase Storage is not configured."

    base_url = settings.SUPABASE_URL.rstrip("/")
    bucket = settings.SUPABASE_STORAGE_BUCKET
    api_key = settings.SUPABASE_SERVICE_ROLE_KEY

    # Supabase storage upload endpoint: POST/PUT /storage/v1/object/{bucket}/{filename}
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "apikey": api_key,
        "Content-Type": content_type or "application/octet-stream",
        "x-upsert": "true",
    }

    try:
        req = urllib_request.Request(upload_url, data=file_bytes, headers=headers, method="POST")
        with urllib_request.urlopen(req, timeout=15) as response:
            if response.status in (200, 201):
                public_url = get_supabase_public_url(filename)
                return True, public_url
            return False, f"Supabase responded with status {response.status}"
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        logger.error("Supabase Storage HTTPError: %s %s", e.code, err_body)
        return False, f"Supabase HTTP {e.code}: {err_body}"
    except URLError as e:
        logger.error("Supabase Storage URLError: %s", e.reason)
        return False, f"Network error connecting to Supabase: {e.reason}"
    except Exception as e:
        logger.error("Supabase upload exception: %s", str(e))
        return False, str(e)


def delete_file_from_supabase(filename):
    """
    Delete a file from Supabase Storage Bucket.
    Returns (success: bool, error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase Storage is not configured."

    base_url = settings.SUPABASE_URL.rstrip("/")
    bucket = settings.SUPABASE_STORAGE_BUCKET
    api_key = settings.SUPABASE_SERVICE_ROLE_KEY

    delete_url = f"{base_url}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "apikey": api_key,
    }

    try:
        req = urllib_request.Request(delete_url, headers=headers, method="DELETE")
        with urllib_request.urlopen(req, timeout=15) as response:
            return response.status in (200, 204), ""
    except Exception as e:
        logger.error("Failed to delete Supabase object: %s", str(e))
        return False, str(e)
