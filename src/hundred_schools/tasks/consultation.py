"""Task factory for adviser consultations."""

from __future__ import annotations

from crewai import Agent, Task


def create_advice_task(agent: Agent, school: str) -> Task:
    """Create a concise, school-specific advice task."""
    return Task(
        description=(
            "Based on the user question below, provide advice consistent with your "
            "school's philosophical framework.\n\n"
            "User question: {question}\n\n"
            f"Your school: {school}\n"
            "Requirements:\n"
            "1. Respond in English; target 50-100 Chinese characters for the body.\n"
            "2. Use a natural thesis-analysis-conclusion structure: first state the "
            "core judgment, then provide specific analysis or actionable advice, "
            "and finally summarize the principle. Do not write structural labels "
            "such as 'thesis', 'analysis', or 'conclusion'.\n"
            "3. Must reflect your school's analytical approach and give concrete, "
            "actionable advice.\n"
            "4. Do not pretend to represent other schools; do not force alignment "
            "across different schools' conclusions.\n"
            "5. Output only the advice body; do not add headings, character counts, "
            "or Markdown lists."
        ),
        expected_output=(
            f"A piece of English advice, targeting 50-100 Chinese characters, "
            f"structured as thesis-analysis-conclusion, and reflecting the core "
            f"thought of {school}."
        ),
        agent=agent,
    )
