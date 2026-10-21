# Hundred Schools Advisory — Streamlit UI

A Python-native web interface built with [Streamlit](https://streamlit.io/),
keeping frontend and backend in a single codebase.

## Quick start

```bash
# Install the optional dependency
uv sync --extra web

# Launch
uv run streamlit run src/hundred_schools/ui.py

# Or use the CLI entry point
uv run hundred-schools-ui
```

## How it works

| Concept | Implementation |
|---|---|
| **4 adviser agents** | Imported directly from `src/hundred_schools/agents/experts.py` — no REST API layer needed |
| **Agent caching** | `@st.cache_resource` builds agents once per model config, survives reruns |
| **Broadcast** | Sends the question to all enabled schools sequentially, one per Streamlit rerun cycle (progressive rendering) |
| **Toggle** | Per-school checkbox to enable / disable before sending |
| **Chat history** | `st.session_state` stores per-school message lists |
| **Length validation** | Reuses `length_warning()` from the existing output model |
| **New Chat** | Clears all history, resets broadcast counter |

## Architecture

```text
src/hundred_schools/
├── ui.py               # Streamlit app + CLI entry point (run)
├── agents/experts.py   # Agent definitions (reused)
├── crews/council_crew.py  # LLM factory (reused)
├── config.py           # Settings (reused)
└── models/response.py  # Validation (reused)
```

The Streamlit app imports directly from `src/hundred_schools/` — no API layer needed.

## Theme

The UI uses the same GitHub-inspired light color palette as the original HTML
frontend:

- Confucian: `#bf6f36` (warm amber)
- Legalist: `#cf222e` (red)
- Taoist: `#1a7f37` (green)
- Strategist: `#8250df` (purple)

## Environment variables

Same as the CLI — configure via `.env` or environment:

| Variable | Required | Example |
|---|---|---|
| `MODEL` | Yes | `openai/gpt-4o-mini` |
| `API_KEY` | Conditional | Your API key (if the model requires one) |
| `BASE_URL` | Optional | Custom API endpoint |
