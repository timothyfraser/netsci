"""Thin OpenAI SDK wrapper for Cornell AI Gateway."""

from __future__ import annotations

from openai import OpenAI

from env import get_litellm_env


def get_client() -> OpenAI:
    base, key = get_litellm_env()
    if not key:
        raise RuntimeError("LITELLM_API_KEY not set in .canvas/.env")
    return OpenAI(base_url=f"{base}/v1", api_key=key)
