"""Backward-compatible agent factory functions.

Agent definitions are loaded from agents.yaml via the loader module.
Prefer ``loader.load_schools()`` in new code for full access to school metadata.
"""

from __future__ import annotations

from crewai import LLM, Agent

from hundred_schools.agents.loader import load_schools

_SCHOOLS = {s.id: s for s in load_schools()}


def create_confucian_agent(llm: LLM) -> Agent:
    """Create the Confucian adviser."""
    return _SCHOOLS["confucian"].create_agent(llm)


def create_legalist_agent(llm: LLM) -> Agent:
    """Create the Legalist adviser."""
    return _SCHOOLS["legalist"].create_agent(llm)


def create_taoist_agent(llm: LLM) -> Agent:
    """Create the Taoist adviser."""
    return _SCHOOLS["taoist"].create_agent(llm)


def create_strategist_agent(llm: LLM) -> Agent:
    """Create the strategist adviser."""
    return _SCHOOLS["strategist"].create_agent(llm)
