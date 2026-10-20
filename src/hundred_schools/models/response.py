"""Output models and lightweight response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdviserOpinion(BaseModel):
    """One school's concise recommendation."""

    school: str = Field(description="School name, e.g. Confucian, Legalist, Taoist, or Strategist")
    advice: str = Field(
        min_length=1,
        description=(
            "Advice body in English, targeting 80-150 English words, "
            "using a thesis-analysis-conclusion structure"
        ),
    )


def count_words(text: str) -> int:
    """Count English words in the advice text."""
    return len(text.split())


def length_warning(opinion: AdviserOpinion) -> str | None:
    """Return a warning when advice is outside the target word count range."""
    count = count_words(opinion.advice)
    if not 80 <= count <= 150:
        return (
            f"{opinion.school} advice contains approximately {count} "
            f"English words; target range is 80-150."
        )
    return None
