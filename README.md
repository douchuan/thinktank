# Hundred Schools of Thought Advisory

A multi-agent learning project built on Python 3.12 and CrewAI. Submit a question, and four advisers—Confucianism, Legalism, Daoism, and Sunzi's Art of War—each offer advice grounded in their respective philosophical frameworks.

## Features

- Four expert Agents with differentiated perspectives.
- CrewAI `Agent`, `Task`, `Crew`, and `Process.sequential` orchestration.
- Pydantic result models for structured output.
- Target output length: 50–100 Chinese characters per school, following a thesis–analysis–conclusion structure.
- CLI, Web UI, foundational unit tests, Ruff configuration, and `.env.example`.

> Length and structure are guided by prompts and enforced by basic programmatic validation. LLM output is not guaranteed to always meet requirements. The project warns on abnormal lengths rather than silently truncating advice.

## Prerequisites

- Python 3.12
- `uv`
- Accessible model API with a valid API key

## Installation

```bash
uv sync --extra dev
cp .env.example .env
```

Edit `.env` to set your model provider and API key. For example, using an OpenAI-compatible endpoint:

```dotenv
API_KEY=api-key
MODEL=deepseek-v4-1-flash-economy-261017
BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

`MODEL` uses LiteLLM/CrewAI model identifiers. Different providers may require additional environment variables—consult the model and CrewAI documentation for details.

## Usage

```bash
uv run hundred-schools "In the early stages of a startup, should I prioritize growth or risk control?"
```

Or run interactively:

```bash
uv run hundred-schools
```

### Web UI

The web interface provides each school with its own conversation window, supporting multi-turn follow-ups with isolated conversation histories across schools.

```bash
uv run hundred-schools-web
```

Open your browser to `http://localhost:8000` after starting.

## Development & Testing

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Directory Structure

```text
.
├── CLAUDE.md
├── pyproject.toml
├── README.md
├── .env.example
├── src/hundred_schools/
│   ├── agents/       # Expert Agent definitions
│   ├── crews/        # Crew orchestration
│   ├── tasks/        # Task definitions
│   ├── models/       # Pydantic output models
│   ├── config.py
│   ├── main.py       # CLI entry point
│   ├── server.py     # Web UI backend
│   └── static/       # Web UI frontend
│       └── index.html
└── tests/
```

## Design Boundaries

- CLI uses sequential execution; each of the four schools completes its advice task independently.
- Web UI provides independent conversation windows per school with multi-turn follow-ups and isolated conversation histories.
- Tool calling, RAG, long-term memory, and multi-round debate are not yet implemented.
- The "Hundred Schools" character and thought settings are simplified interpretations for modern decision-making contexts and do not claim to exhaustively represent each school's philosophy.
