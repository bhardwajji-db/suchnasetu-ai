"""
Durable Cloudflare R2 / S3 Object and Database Synchronization for SuchnaSetu AI.

Provides optional, zero-cost, serverless durability for Render Free Tier:
- Automatically restores SQLite database snapshots on container cold-starts.
- Automatically pushes atomic SQLite snapshots to Cloudflare R2 on writes/shutdown.
- Persists uploaded notices in R2 bucket (10 GB free tier with zero egress fees).
- Gracefully falls back to local-only SQLite when R2/S3 credentials are not configured.
"""

from __future__ import annotations

import os
import sys
import hmac
import hashlib
import datetime
import logging
import sqlite3
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

import requests

logger = logging.getLogger("notice2action.storage_sync")


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_signature_key(key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
    k_date = _sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = _sign(k_date, region_name)
    k_service = _sign(k_region, service_name)
    k_signing = _sign(k_service, "aws4_request")
    return k_signing


class R2StorageSync:
    """Lightweight pure-Python S3/R2 client supporting AWS Signature Version 4."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region: str = "auto",
    ):
        self.bucket_name = (bucket_name or os.getenv("R2_BUCKET_NAME") or os.getenv("S3_BUCKET_NAME") or "").strip()
        self.account_id = (account_id or os.getenv("R2_ACCOUNT_ID") or "").strip()
        self.access_key_id = (
            access_key_id or os.getenv("R2_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID") or ""
        ).strip()
        self.secret_access_key = (
            secret_access_key or os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY") or ""
        ).strip()
        self.region = region

        # Resolve endpoint URL
        explicit_endpoint = (endpoint_url or os.getenv("R2_ENDPOINT_URL") or os.getenv("S3_ENDPOINT_URL") or "").strip()
        if explicit_endpoint:
            self.endpoint_url = explicit_endpoint.rstrip("/")
        elif self.account_id:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        else:
            self.endpoint_url = ""

    @property
    def is_configured(self) -> bool:
        """True if sufficient credentials and bucket details exist to communicate with R2/S3."""
        return bool(self.bucket_name and self.access_key_id and self.secret_access_key and self.endpoint_url)

    def _build_signed_headers(
        self, method: str, host: str, canonical_uri: str, payload_bytes: bytes = b"", content_type: str = "application/octet-stream"
    ) -> Dict[str, str]:
        """Generates AWS SigV4 signed headers for an S3/R2 request."""
        now = datetime.datetime.now(datetime.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        canonical_headers = (
            f"host:{host}\n"
            f"x-amz-content-sha256:{payload_hash}\n"
            f"x-amz-date:{amz_date}\n"
        )
        signed_headers = "host;x-amz-content-sha256;x-amz-date"

        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/s3/aws4_request"
        string_to_sign = (
            f"{algorithm}\n"
            f"{amz_date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = _get_signature_key(self.secret_access_key, date_stamp, self.region, "s3")
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        return {
            "Host": host,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": authorization_header,
            "Content-Type": content_type,
        }

    def upload_file(self, local_path: Path, remote_key: str, content_type: str = "application/octet-stream") -> bool:
        """Uploads a local file to the remote bucket."""
        if not self.is_configured:
            logger.debug("R2/S3 storage sync skipped: credentials not configured.")
            return False

        local_path = Path(local_path)
        if not local_path.is_file():
            logger.warning(f"R2 upload failed: local file {local_path} does not exist.")
            return False

        try:
            payload = local_path.read_bytes()
            parsed = urlparse(self.endpoint_url)
            host = parsed.netloc
            canonical_uri = f"/{self.bucket_name}/{remote_key.lstrip('/')}"
            url = f"{self.endpoint_url}{canonical_uri}"

            headers = self._build_signed_headers("PUT", host, canonical_uri, payload, content_type)
            res = requests.put(url, data=payload, headers=headers, timeout=30)
            if res.status_code in (200, 201, 204):
                logger.info(f"Successfully synced {local_path.name} -> r2://{self.bucket_name}/{remote_key}")
                return True
            else:
                logger.warning(f"R2 upload failed ({res.status_code}): {res.text[:200]}")
                return False
        except Exception as exc:
            logger.warning(f"R2 upload exception for {remote_key}: {exc}")
            return False

    def download_file(self, remote_key: str, destination_path: Path) -> bool:
        """Downloads a remote object to a local file path."""
        if not self.is_configured:
            return False

        destination_path = Path(destination_path)
        try:
            parsed = urlparse(self.endpoint_url)
            host = parsed.netloc
            canonical_uri = f"/{self.bucket_name}/{remote_key.lstrip('/')}"
            url = f"{self.endpoint_url}{canonical_uri}"

            headers = self._build_signed_headers("GET", host, canonical_uri, b"")
            res = requests.get(url, headers=headers, timeout=60, stream=True)
            if res.status_code == 200:
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                with open(destination_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=65536):
                        f.write(chunk)
                logger.info(f"Successfully restored r2://{self.bucket_name}/{remote_key} -> {destination_path}")
                return True
            elif res.status_code == 404:
                logger.debug(f"Remote object r2://{self.bucket_name}/{remote_key} does not exist (HTTP 404).")
                return False
            else:
                logger.warning(f"R2 download failed ({res.status_code}): {res.text[:200]}")
                return False
        except Exception as exc:
            logger.warning(f"R2 download exception for {remote_key}: {exc}")
            return False

    def backup_database(self, db_path: Path, remote_key: str = "suchnasetu.db") -> bool:
        """Creates an atomic, consistent SQLite snapshot and uploads it to R2/S3."""
        if not self.is_configured:
            return False

        db_path = Path(db_path)
        if not db_path.is_file():
            return False

        temp_snapshot: Optional[Path] = None
        try:
            # Create a consistent online backup using SQLite backup API
            with tempfile.NamedTemporaryFile(suffix=".db.snapshot", delete=False) as tmp:
                temp_snapshot = Path(tmp.name)

            src_conn = sqlite3.connect(str(db_path))
            dst_conn = sqlite3.connect(str(temp_snapshot))
            with dst_conn:
                src_conn.backup(dst_conn)
            src_conn.close()
            dst_conn.close()

            return self.upload_file(temp_snapshot, remote_key, content_type="application/x-sqlite3")
        except Exception as exc:
            logger.warning(f"Database snapshot backup failed: {exc}")
            return False
        finally:
            if temp_snapshot and temp_snapshot.is_file():
                try:
                    temp_snapshot.unlink()
                except Exception:
                    pass

    def restore_database_if_missing(self, db_path: Path, remote_key: str = "suchnasetu.db") -> bool:
        """Restores the database from R2/S3 if local database file does not exist or has 0 bytes."""
        if not self.is_configured:
            return False

        db_path = Path(db_path)
        if db_path.is_file() and db_path.stat().st_size > 0:
            logger.debug("Local database already exists and has content; skipping initial restore.")
            return False

        logger.info(f"Local database empty/missing; attempting to restore from r2://{self.bucket_name}/{remote_key}...")
        return self.download_file(remote_key, db_path)


# Singleton instance
storage_sync = R2StorageSync()

