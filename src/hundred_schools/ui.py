"""Streamlit Web UI for the Hundred Schools Advisory.

Run from the project root:
    uv run streamlit run src/hundred_schools/ui.py

Or via CLI entry point:
    uv run hundred-schools-ui
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

# Make src/ importable when running this file directly.
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from crewai import LLM, Agent  # noqa: E402

from hundred_schools.agents.experts import (  # noqa: E402
    create_confucian_agent,
    create_legalist_agent,
    create_strategist_agent,
    create_taoist_agent,
)
from hundred_schools.config import Settings  # noqa: E402
from hundred_schools.crews.council_crew import create_llm  # noqa: E402


@dataclass(frozen=True)
class SchoolDef:
    """Display metadata and agent factory for one school of thought."""

    id: str
    name: str
    color: str
    emoji: str
    creator: Callable[[LLM], Agent]


SCHOOLS: list[SchoolDef] = [
    SchoolDef("confucian", "Confucian", "#bf6f36", "🎓", create_confucian_agent),
    SchoolDef("legalist", "Legalist", "#cf222e", "⚖️", create_legalist_agent),
    SchoolDef("taoist", "Taoist", "#1a7f37", "🌿", create_taoist_agent),
    SchoolDef("strategist", "Strategist", "#8250df", "🎯", create_strategist_agent),
]


# ---------------------------------------------------------------------------
# Agent construction
# ---------------------------------------------------------------------------


def _build_llm(settings: Settings) -> LLM:
    return create_llm(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


@st.cache_resource(show_spinner="Initialising advisers…")
def _build_agents(
    model: str,
    api_key: str | None,
    base_url: str | None,
) -> dict[str, Agent]:
    """Cache agent definitions across Streamlit reruns."""
    settings = Settings(model=model, api_key=api_key, base_url=base_url)
    llm = _build_llm(settings)
    return {school.id: school.creator(llm) for school in SCHOOLS}


def _system_prompt(school: SchoolDef, agent: Agent) -> str:
    return (
        f"You are a {school.name} adviser. Answer the user's question based on "
        f"{school.name} thought.\n\n"
        f"Role: {agent.role}\n"
        f"Goal: {agent.goal}\n"
        f"Background: {agent.backstory}\n\n"
        "Requirements:\n"
        "1. Respond in English.\n"
        "2. Use Markdown formatting — headings, bullet points, bold, etc.\n"
        "3. Provide concrete, actionable advice.\n"
        "4. Keep it to ~150 words — 2-3 key points, no preamble.\n"
        "5. Do not pretend to represent other schools."
    )


def _call_agent(agent: Agent, llm: LLM, school: SchoolDef, message: str) -> str:
    messages = [
        {"role": "system", "content": _system_prompt(school, agent)},
        {"role": "user", "content": message},
    ]
    result = llm.call(messages)
    return result if isinstance(result, str) else str(result)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------


def _init_state() -> None:
    defaults = {
        "active_school_id": SCHOOLS[0].id,
        "enabled": {school.id: True for school in SCHOOLS},
        "history": {school.id: [] for school in SCHOOLS},
        "pending_question": None,
        "pending_idx": 0,
        "broadcast_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_chat() -> None:
    st.session_state.history = {school.id: [] for school in SCHOOLS}
    st.session_state.broadcast_count = 0
    st.session_state.pending_question = None
    st.session_state.pending_idx = 0


def _has_pending() -> bool:
    return st.session_state.pending_question is not None


def _active_schools() -> list[SchoolDef]:
    """Return the single adviser selected in the sidebar dropdown."""
    active_id = st.session_state.get("active_school_id", SCHOOLS[0].id)
    return [school for school in SCHOOLS if school.id == active_id]


# ---------------------------------------------------------------------------
# Chat rendering
# ---------------------------------------------------------------------------


def _render_school_chat(school: SchoolDef) -> None:
    """Render one school's history inside a bounded, native Streamlit container."""
    enabled = st.session_state.enabled.get(school.id, True)

    with st.container(height=500, border=True):
        for message in st.session_state.history[school.id]:
            role = message["role"]
            content = message["content"]

            if role == "user":
                st.chat_message("user", avatar="🧑").write(content)
            elif role == "assistant":
                st.chat_message("assistant", avatar=school.emoji).markdown(content)
            elif role == "system":
                st.caption(content)

        if _has_pending() and enabled:
            pending_idx = st.session_state.pending_idx
            if pending_idx < len(SCHOOLS) and SCHOOLS[pending_idx].id == school.id:
                st.chat_message("assistant", avatar=school.emoji).write("_Thinking…_")


def _render_active_school_chats() -> None:
    """Render enabled advisers' conversations in one full-width column."""
    active_schools = _active_schools()
    if not active_schools:
        st.info("Select at least one adviser from the panel on the right.")
        return

    for index, school in enumerate(active_schools):
        if index:
            st.divider()
        _render_school_chat(school)


def _render_sidebar() -> None:
    """Render the title + school dropdown in the right column."""
    st.markdown("**Hundred Schools Advisory**")

    school_options = {school.id: f"{school.emoji} {school.name}" for school in SCHOOLS}
    st.selectbox(
        "Adviser",
        options=[school.id for school in SCHOOLS],
        format_func=lambda sid: school_options[sid],
        key="active_school_id",
        label_visibility="collapsed",
    )
    # Changing the dropdown activates only that adviser.
    st.session_state.enabled = {
        school.id: school.id == st.session_state.active_school_id for school in SCHOOLS
    }

    st.divider()
    if st.button("New Chat", use_container_width=True):
        _clear_chat()
        st.rerun()


# ---------------------------------------------------------------------------
# Progressive broadcast: process one enabled school per rerun
# ---------------------------------------------------------------------------


def _process_pending() -> None:
    """Handle the next adviser, then rerun to continue the broadcast."""
    if not _has_pending():
        return

    question = st.session_state.pending_question
    idx = st.session_state.pending_idx
    active_ids = {school.id for school in _active_schools()}

    # Skip disabled advisers without making an LLM call.
    while idx < len(SCHOOLS) and SCHOOLS[idx].id not in active_ids:
        school = SCHOOLS[idx]
        st.session_state.history[school.id].append(
            {"role": "system", "content": f"({school.name} is disabled)"}
        )
        idx += 1
        st.session_state.pending_idx = idx

    if idx >= len(SCHOOLS):
        st.session_state.pending_question = None
        st.session_state.pending_idx = 0
        st.session_state.broadcast_count += 1
        st.rerun()
        return

    school = SCHOOLS[idx]
    agents = st.session_state.get("_agents", {})
    llm = st.session_state.get("_llm")

    if llm is None or not agents:
        st.session_state.pending_question = None
        st.session_state.pending_idx = 0
        st.error("Advisers not initialised — please check your model configuration.")
        st.stop()

    try:
        with st.spinner(f"{school.name} is thinking…"):
            reply = _call_agent(agents[school.id], llm, school, question)
        st.session_state.history[school.id].append({"role": "assistant", "content": reply})
    except Exception as exc:  # Keep the broadcast moving if one adviser fails.
        st.session_state.history[school.id].append(
            {"role": "system", "content": f"Request failed: {exc}"}
        )

    st.session_state.pending_idx = idx + 1
    st.rerun()


# ---------------------------------------------------------------------------
# Streamlit entry points
# ---------------------------------------------------------------------------


def run() -> None:
    """CLI entry point — launches Streamlit for the UI."""
    try:
        import streamlit.web.cli as st_cli
    except ImportError:
        raise ImportError(
            "Streamlit is required for the UI. Install with: uv add streamlit"
        ) from None

    app_path = Path(__file__).resolve()
    sys.argv = ["streamlit", "run", str(app_path)]
    st_cli.main()


def _main() -> None:
    st.set_page_config(
        page_title="Hundred Schools Advisory",
        page_icon="🎓",
        layout="wide",
    )
    st.markdown(
        "<style>"
        " .block-container { padding-top: 1rem; } "
        " #MainMenu, header { visibility: hidden; }"
        "</style>",
        unsafe_allow_html=True,
    )
    _init_state()

    # Initialise shared model/agent resources. These are cached or retained in
    # session state so a normal Streamlit rerun does not rebuild the agents.
    settings = Settings.from_env()
    try:
        agents = _build_agents(settings.model, settings.api_key, settings.base_url)
        llm = _build_llm(settings)
        st.session_state["_agents"] = agents
        st.session_state["_llm"] = llm
    except Exception as exc:
        st.error(f"Failed to initialise advisers: {exc}")
        st.stop()

    # Process the next adviser before rendering the normal page.
    if _has_pending():
        _process_pending()
        return

    # Two-column layout: chat area (left) + sidebar (right).
    chat_col, sidebar_col = st.columns([4, 1])

    # --- Left column: chat messages + input ---
    with chat_col:
        _render_active_school_chats()

        # Native chat input inside the left column so it stays aligned with
        # the conversation area instead of spanning the full page width.
        question = st.chat_input("Ask the advisers a question…", key="question_input")

    # --- Right column: title + adviser dropdown + new chat ---
    with sidebar_col:
        _render_sidebar()

    # Handle any pending advisers advanced by sidebar interactions.
    if _has_pending():
        _process_pending()
        return

    if question is not None:
        text = question.strip()
        if not text:
            st.warning("Please enter a question.")
            return
        if not _active_schools():
            st.warning("Select an adviser before sending a question.")
            return

        # Show the question in each adviser's independent conversation history.
        for school in SCHOOLS:
            st.session_state.history[school.id].append({"role": "user", "content": text})

        st.session_state.pending_question = text
        st.session_state.pending_idx = 0
        st.rerun()


if __name__ == "__main__":
    _main()
