"""Output models and lightweight response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdviserOpinion(BaseModel):
    """One school's concise recommendation."""

    school: str = Field(description="学派名称，例如儒家、法家、道家或兵家")
    advice: str = Field(
        min_length=1,
        description="中文建议正文，目标 50～100 个汉字，采用总—分—总结构",
    )


def count_cjk_characters(text: str) -> int:
    """Count CJK Unified Ideographs as a practical approximation of Chinese character count."""
    return sum("\u4e00" <= char <= "\u9fff" for char in text)


def length_warning(opinion: AdviserOpinion) -> str | None:
    """Return a warning when advice is outside the target CJK character range."""
    count = count_cjk_characters(opinion.advice)
    if not 50 <= count <= 100:
        return f"{opinion.school}建议包含约 {count} 个汉字，目标范围为 50～100 字。"
    return None
