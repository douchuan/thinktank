"""Task factory for adviser consultations."""

from __future__ import annotations

from crewai import Agent, Task


def create_advice_task(agent: Agent, school: str) -> Task:
    """Create a school-specific advice task with Markdown output."""
    return Task(
        description=(
            "Based on the user question below, provide advice consistent with your "
            "school's philosophical framework.\n\n"
            "User question: {question}\n\n"
            f"Your school: {school}\n"
            "Requirements:\n"
            "1. Respond in English.\n"
            "2. Use Markdown formatting (headings, bold, bullet points, etc.) "
            "as appropriate.\n"
            "3. Provide concrete, actionable advice.\n"
            "4. Keep it to ~150 words — 2-3 key points, no preamble, no restating "
            "the question, no philosophical background summaries.\n"
            "5. Do not pretend to represent other schools; do not force alignment "
            "across different schools' conclusions."
        ),
        expected_output=(
            f"A piece of advice in English, using Markdown formatting, "
            f"reflecting the core thought of {school}."
        ),
        agent=agent,
    )
