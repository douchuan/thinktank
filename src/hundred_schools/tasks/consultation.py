"""Task factory for adviser consultations."""

from __future__ import annotations

from crewai import Agent, Task


def create_advice_task(agent: Agent, school: str) -> Task:
    """Create a concise, school-specific advice task."""
    return Task(
        description=(
            "请针对以下用户问题，给出符合你所属学派思想的建议。\n\n"
            "用户问题：{question}\n\n"
            f"你的学派：{school}\n"
            "要求：\n"
            "1. 使用中文，建议正文目标为 50～100 个汉字。\n"
            "2. 采用自然的总—分—总结构：先提出核心判断，再给出具体分析或行动建议，"
            "最后总结原则。不要写出“总、分、总”等结构标签。\n"
            "3. 必须体现本学派的分析方式，给出具体、可执行的建议。\n"
            "4. 不要假装代表其他学派，不要强行追求各家结论一致。\n"
            "5. 只输出建议正文，不要添加标题、字数说明或 Markdown 列表。"
        ),
        expected_output=(
            f"一段中文建议，目标 50～100 个汉字，结构为总—分—总，且体现{school}的核心思想。"
        ),
        agent=agent,
    )
