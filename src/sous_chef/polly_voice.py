"""Amazon Polly Neural Voice Integration for Sous-Chef.

Provides authentic, expressive Amazon Alexa voice synthesis (VoiceId='Joanna' Neural Engine)
with local disk caching for instant low-latency audio playback in the web companion screen.
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger("kitchen_polly")

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "polly_audio"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_polly_client: Any = None
_polly_available: bool | None = None


def get_polly_client() -> Any:
    global _polly_client, _polly_available
    if _polly_client is not None:
        return _polly_client
    if _polly_available is False:
        return None

    try:
        import boto3
        from botocore.config import Config as BotoConfig

        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
        boto_config = BotoConfig(
            connect_timeout=2.0,
            read_timeout=3.0,
            retries={"max_attempts": 2}
        )
        _polly_client = boto3.client("polly", region_name=region, config=boto_config)
        _polly_available = True
        log.info("Amazon Polly client initialized successfully (region=%s)", region)
        return _polly_client
    except Exception as exc:
        log.warning("Amazon Polly client unavailable, using browser speech fallback: %s", exc)
        _polly_available = False
        return None


def synthesize_speech(text: str, voice_id: str = "Joanna", engine: str = "neural") -> bytes | None:
    """Synthesizes text into MP3 audio using Amazon Polly Neural.

    Caches output audio locally by MD5 hash for sub-millisecond replay.
    """
    clean_text = (text or "").strip()
    if not clean_text:
        return None

    # Check local cache first
    cache_key = hashlib.md5(f"{voice_id}:{engine}:{clean_text}".encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.mp3"
    if cache_file.exists():
        try:
            return cache_file.read_bytes()
        except Exception:
            pass

    client = get_polly_client()
    if client is None:
        return None

    try:
        # Detect if text contains SSML tags
        text_type = "ssml" if clean_text.startswith("<speak>") and clean_text.endswith("</speak>") else "text"
        
        response = client.synthesize_speech(
            Engine=engine,
            OutputFormat="mp3",
            Text=clean_text,
            TextType=text_type,
            VoiceId=voice_id
        )

        audio_stream = response.get("AudioStream")
        if audio_stream:
            audio_bytes = audio_stream.read()
            try:
                cache_file.write_bytes(audio_bytes)
            except Exception as cache_err:
                log.warning("Could not cache Polly audio: %s", cache_err)
            return audio_bytes
    except Exception as exc:
        log.warning("Amazon Polly synthesis failed: %s", exc)

    return None
