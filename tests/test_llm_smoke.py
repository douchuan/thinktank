"""Smoke test for CrewAI and the configured LLM."""

from crewai import LLM, Agent, Crew, Process, Task

from hundred_schools.config import Settings


def test_llm_smoke() -> None:
    """Verify that a single agent can complete a simple task."""
    settings = Settings.from_env()

    options = {
        "model": settings.model,
        "timeout": 30,
        "max_retries": 0,
    }

    if settings.api_key:
        options["api_key"] = settings.api_key

    if settings.base_url:
        options["base_url"] = settings.base_url

    llm = LLM(**options)

    agent = Agent(
        role="Test Assistant",
        goal="Verify that the model can respond normally",
        backstory="You are an assistant used to diagnose model connectivity.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description="Please reply only with: Test successful.",
        expected_output="Test successful",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    result = crew.kickoff()
    print(f"\nModel returned result: {result}")

    assert str(result).strip(), "Model returned empty result"
