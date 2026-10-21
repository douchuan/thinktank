"""CrewAI orchestration for the Hundred Schools council."""

from __future__ import annotations

from crewai import LLM, Crew, Process

from hundred_schools.agents.loader import load_schools
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

    schools = load_schools()
    advisers = [(school, school.create_agent(llm)) for school in schools]
    tasks = [create_advice_task(agent, school.name) for school, agent in advisers]
    return Crew(
        agents=[agent for _, agent in advisers],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )
