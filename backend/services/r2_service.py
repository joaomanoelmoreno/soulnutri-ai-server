"""Cloudflare R2 Storage Service for SoulNutri."""
import boto3
import os
import logging

logger = logging.getLogger(__name__)

_s3_client = None

def _get_s3():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3',
            endpoint_url=os.environ['R2_ENDPOINT'],
            aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
            region_name='auto'
        )
    return _s3_client

def get_bucket():
    return os.environ['R2_BUCKET']

def r2_get_image(key: str) -> tuple:
    """Download image from R2. Returns (bytes, content_type)."""
    try:
        s3 = _get_s3()
        # Remove "r2:" prefix if present
        if key.startswith("r2:"):
            key = key[3:]
        resp = s3.get_object(Bucket=get_bucket(), Key=key)
        data = resp['Body'].read()
        ct = resp.get('ContentType', 'image/jpeg')
        return data, ct
    except Exception as e:
        logger.error(f"[R2] Erro ao ler {key}: {e}")
        return None, None

def r2_upload_image(key: str, data: bytes, content_type: str = "image/jpeg") -> bool:
    """Upload image to R2."""
    try:
        s3 = _get_s3()
        if key.startswith("r2:"):
            key = key[3:]
        s3.put_object(Bucket=get_bucket(), Key=key, Body=data, ContentType=content_type)
        return True
    except Exception as e:
        logger.error(f"[R2] Erro ao upload {key}: {e}")
        return False

def r2_delete_image(key: str) -> bool:
    """Delete image from R2."""
    try:
        s3 = _get_s3()
        if key.startswith("r2:"):
            key = key[3:]
        s3.delete_object(Bucket=get_bucket(), Key=key)
        return True
    except Exception as e:
        logger.error(f"[R2] Erro ao deletar {key}: {e}")
        return False
