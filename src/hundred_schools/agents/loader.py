"""Load school definitions from agents.yaml.

Provides a single source of truth for agent metadata (name, emoji, color)
and CrewAI agent construction, consumed by both the crew orchestration
layer and the Streamlit UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml
from crewai import LLM, Agent

_AGENTS_YAML = Path(__file__).parent / "agents.yaml"


@dataclass(frozen=True)
class SchoolDef:
    """Metadata and agent factory for one school of thought."""

    id: str
    """YAML key, e.g. ``"confucian"``."""
    name: str
    """Display name, e.g. ``"Confucian"``."""
    emoji: str
    color: str
    role: str
    goal: str
    backstory: str

    def create_agent(self, llm: LLM) -> Agent:
        """Build a CrewAI Agent from this school's definition."""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )


def _load_yaml() -> dict[str, dict[str, Any]]:
    with open(_AGENTS_YAML) as f:
        return cast("dict[str, dict[str, Any]]", yaml.safe_load(f))


def load_schools() -> list[SchoolDef]:
    """Parse agents.yaml and return all schools in YAML order."""
    data = _load_yaml()
    schools: list[SchoolDef] = []
    for school_id, entry in data.items():
        schools.append(
            SchoolDef(
                id=school_id,
                name=entry["name"],
                emoji=entry["emoji"],
                color=entry["color"],
                role=entry["role"],
                goal=entry["goal"],
                backstory=entry["backstory"],
            )
        )
    return schools
