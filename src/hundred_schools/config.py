"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    model: str
    api_key: str | None = None
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        """Load settings from environment, including a local .env file."""
        load_dotenv()

        model = os.getenv("MODEL", "openai/gpt-4o-mini").strip()
        if not model:
            raise ValueError("MODEL 不能为空，请在环境变量或 .env 文件中配置。")

        api_key = os.getenv("API_KEY", "").strip() or None
        base_url = os.getenv("BASE_URL", "").strip() or None

        return cls(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
