"""CrewAI orchestration for the Hundred Schools council."""

from __future__ import annotations

from crewai import LLM, Crew, Process

from hundred_schools.agents.experts import (
    create_confucian_agent,
    create_legalist_agent,
    create_strategist_agent,
    create_taoist_agent,
)
from hundred_schools.config import Settings
from hundred_schools.tasks.consultation import create_advice_task


def create_llm(
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> LLM:
    """Create a configured LLM instance."""
    options = {
        "model": model,
        "timeout": 60,
        "max_retries": 0,
    }

    if api_key:
        options["api_key"] = api_key

    if base_url:
        options["base_url"] = base_url

    return LLM(**options)


def build_council_crew(settings: Settings) -> Crew:
    """Build a sequential crew with four independent adviser tasks."""

    llm = create_llm(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )

    advisers = [
        ("儒家", create_confucian_agent(llm)),
        ("法家", create_legalist_agent(llm)),
        ("道家", create_taoist_agent(llm)),
        ("兵家", create_strategist_agent(llm)),
    ]
    tasks = [create_advice_task(agent, school) for school, agent in advisers]
    return Crew(
        agents=[agent for _, agent in advisers],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )
