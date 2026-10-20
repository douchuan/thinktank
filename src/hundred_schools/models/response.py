"""Output models and lightweight response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdviserOpinion(BaseModel):
    """One school's concise recommendation."""

    school: str = Field(description="School name, e.g. Confucian, Legalist, Taoist, or Strategist")
    advice: str = Field(
        min_length=1,
        description=(
            "Advice body in English, targeting 50-100 Chinese characters, "
            "using a thesis-analysis-conclusion structure"
        ),
    )


def count_cjk_characters(text: str) -> int:
    """Count CJK Unified Ideographs as a practical approximation of Chinese character count."""
    return sum("\u4e00" <= char <= "\u9fff" for char in text)


def length_warning(opinion: AdviserOpinion) -> str | None:
    """Return a warning when advice is outside the target CJK character range."""
    count = count_cjk_characters(opinion.advice)
    if not 50 <= count <= 100:
        return (
            f"{opinion.school} advice contains approximately {count} "
            f"Chinese characters; target range is 50-100."
        )
    return None
