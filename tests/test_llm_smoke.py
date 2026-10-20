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
        role="测试助手",
        goal="验证模型是否能够正常响应",
        backstory="你是一个用于诊断模型连接的助手。",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description="请只回答：测试成功。",
        expected_output="测试成功",
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
    print(f"\n模型返回结果：{result}")

    assert str(result).strip(), "模型返回了空结果"
