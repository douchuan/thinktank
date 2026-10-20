"""Langfuse observability integration for LLM call tracing."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def setup_langfuse() -> bool:
    """Initialize Langfuse tracing for OpenAI SDK calls.

    Monkey-patches the OpenAI SDK so that every LLM call (including
    those made internally by CrewAI) is traced to Langfuse.

    Requires ``LANGFUSE_PUBLIC_KEY`` and ``LANGFUSE_SECRET_KEY`` (or
    ``LANGFUSE_HOST`` for self-hosted) to be set in the environment.

    Returns:
        True if tracing was successfully enabled, False otherwise.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip() or None
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip() or None

    if not public_key or not secret_key:
        logger.debug("Langfuse credentials not found; tracing disabled.")
        return False

    try:
        # In the installed SDK version, importing this module enables
        # OpenAI instrumentation. Do not also call register_tracing(),
        # which caused duplicate traces in the current setup.
        import langfuse.openai  # noqa: F401

        # from langfuse.openai import register_tracing
        # register_tracing()

        logger.info("Langfuse OpenAI tracing enabled.")
        return True
    except ImportError:
        logger.warning("langfuse.openai not available; tracing disabled.")
        return False
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to enable Langfuse tracing: %s", exc)
        return False
