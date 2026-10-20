# CLAUDE.md — Hundred Schools Advisory

## Project Goal

This is a Python project for learning the CrewAI multi-agent framework. When the user submits a question, four expert Agents — Confucianism, Legalism, Taoism, and Sunzi's Art of War — each provide advice based on their respective philosophical framework.

## Technical Constraints

- Python version pinned to `>=3.12,<3.13`.
- Uses `uv` for dependency and virtual environment management.
- Uses `pyproject.toml` for project metadata and tool configuration.
- Uses CrewAI's Agent, Task, Crew, and Process to orchestrate workflows.
- Uses Pydantic to describe structured output.
- Uses pytest for tests, Ruff for linting and format checking.
- API Keys and other secrets must only be provided via environment variables or a local `.env` file; never write real keys into source code, test cases, or documentation.
- Production code lives in `src/hundred_schools/`, tests in `tests/`.

## Product Behavior

- The first version provides a command-line interface.
- The user question is passed as input to all expert tasks.
- Each school expresses its position independently; conclusions should not be forced into a single unified answer.
- Each advice item targets 80–150 English words.
- Each advice item follows a natural "thesis–analysis–conclusion" structure: first give a core judgment, then provide specific analysis or actionable advice, and finally summarize the principle.
- Output is in English, with the school name labeled.
- The character count is a target constraint; outputs that do not meet the range should produce a readable warning or validation result, not silently truncate the body.

## Agent Thought Frameworks

### Confucianism
Benevolence, righteousness, ritual, wisdom, trust; virtue-based governance; people-centered approach; responsibility; trust; long-term reputation and relationship governance.

### Legalism
Law, administrative technique, positional power; institutional design; authority and responsibility alignment; execution; incentives and constraints; measurable outcomes.

### Taoism
Following the Way of nature; wuwei (non-action); going with the momentum; reducing over-intervention and wasteful consumption.

### Sunzi's Art of War (Strategist)
Know the enemy and know yourself; winning through situational advantage; resource allocation; competitive landscape; timing; risk; advance and retreat strategy.

The above is a simplified role setup for modern decision-making contexts and should not claim to exhaustively represent each school's philosophy.

## Architecture Principles

- Agent definitions, Task definitions, Crew orchestration, output models, and CLI are organized in layers.
- Prefer `Process.sequential` for the first version to reduce concurrency and debugging complexity.
- Do not turn four experts into four scattered LLM calls just to "look like multi-agent"; achieve it through CrewAI's orchestration abstractions.
- Keep code clear, well-typed, and avoid over-abstraction.
- Prompts should clearly specify output format, stance boundaries, and length requirements.
- Allow model configuration via environment variables; do not hardcode any model provider's key in code.

## Things Not Done in the Current Version

Unless the user explicitly requests, do not add these in the initial version:
- Web frontend or REST API
- RAG, vector databases, or external knowledge bases
- Long-term memory, complex tool calling
- Multi-round debate or complex hierarchy manager agents
- Databases, user accounts, or multi-tenant systems

## When Modifying Code

1. Read relevant modules and tests before making changes.
2. New features should have corresponding tests; prefer separating unit tests from real model calls.
3. Do not call paid model APIs in automated tests by default.
4. When updating dependencies, sync `pyproject.toml` and related documentation.
5. After changes, run `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .` (when the environment allows).
6. If the command does not run or fails due to a missing environment, state it clearly; do not claim tests passed.
7. Keep documentation and code behavior consistent.
