"""Streamlit Web UI for the Hundred Schools Advisory.

Run from the project root:
    uv run streamlit run src/hundred_schools/ui.py

Or via CLI entry point:
    uv run hundred-schools-ui
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Make src/ importable when running `streamlit run src/hundred_schools/ui.py`
# directly (without `uv run`). When installed via uv, this is a no-op.
# ---------------------------------------------------------------------------
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from crewai import LLM, Agent  # noqa: E402

from hundred_schools.agents.experts import (  # noqa: E402
    create_confucian_agent,
    create_legalist_agent,
    create_strategist_agent,
    create_taoist_agent,
)
from hundred_schools.config import Settings  # noqa: E402
from hundred_schools.crews.council_crew import create_llm  # noqa: E402
from hundred_schools.models.response import (  # noqa: E402
    AdviserOpinion,
    length_warning,
)

# ---------------------------------------------------------------------------
# School definitions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SchoolDef:
    id: str
    name: str
    color: str
    emoji: str
    creator: object  # (LLM) -> Agent


SCHOOLS: list[SchoolDef] = [
    SchoolDef("confucian", "Confucian", "#bf6f36", "🎓", create_confucian_agent),
    SchoolDef("legalist", "Legalist", "#cf222e", "⚖️", create_legalist_agent),
    SchoolDef("taoist", "Taoist", "#1a7f37", "🌿", create_taoist_agent),
    SchoolDef("strategist", "Strategist", "#8250df", "🎯", create_strategist_agent),
]

SCHOOL_MAP = {s.id: s for s in SCHOOLS}

# ---------------------------------------------------------------------------
# CSS theme (mirrors the existing HTML UI's GitHub-inspired light palette)
# ---------------------------------------------------------------------------

_PAGE_CSS = """
<style>
    .stApp { background: #ffffff; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 0.5rem; }
    .stChatMessage { line-height: 1.6; }

    /* Color dots in column headers */
    .school-dot {
        display: inline-block;
        width: 10px; height: 10px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }

    /* System / notice messages appear italic and muted */
    .sys-msg { color: #656d76; font-style: italic; font-size: 13px; }

    /* Input area */
    .stTextArea textarea { font-size: 14px !important; }

    /* Make disabled school columns visually dimmed */
    div[data-testid="column"] { transition: opacity 0.2s; }
</style>
"""


# ---------------------------------------------------------------------------
# Agent cache — built once per model config, survives reruns
# ---------------------------------------------------------------------------


def _build_llm(settings: Settings) -> LLM:
    return create_llm(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


@st.cache_resource(show_spinner="Initialising advisers…")
def _build_agents(model: str, api_key: str | None, base_url: str | None) -> dict[str, Agent]:
    settings = Settings(model=model, api_key=api_key, base_url=base_url)
    llm = _build_llm(settings)
    return {s.id: s.creator(llm) for s in SCHOOLS}


def _system_prompt(school: SchoolDef, agent: Agent) -> str:
    return (
        f"You are a {school.name} adviser. Answer the user's question based on "
        f"{school.name} thought.\n\n"
        f"Role: {agent.role}\n"
        f"Goal: {agent.goal}\n"
        f"Background: {agent.backstory}\n\n"
        f"Requirements:\n"
        f"1. Respond in English; target 80-150 English words for the body.\n"
        f"2. Use a natural thesis-analysis-conclusion structure.\n"
        f"3. Provide concrete, actionable advice.\n"
        f"4. Output only the advice body; do not add headings, character counts, "
        f"or Markdown lists."
    )


def _call_agent(agent: Agent, llm: LLM, school: SchoolDef, message: str) -> str:
    messages = [
        {"role": "system", "content": _system_prompt(school, agent)},
        {"role": "user", "content": message},
    ]
    result = llm.call(messages)
    return result if isinstance(result, str) else str(result)


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

# Keys used in st.session_state:
#   enabled          – dict[school_id -> bool]
#   history          – dict[school_id -> list[{role, content}]]
#   pending_question – str | None (question waiting for broadcast)
#   pending_idx      – index into SCHOOLS of the next school to process
#   broadcast_count  – number of completed broadcast rounds


def _init_state() -> None:
    defaults = {
        "enabled": {s.id: True for s in SCHOOLS},
        "history": {s.id: [] for s in SCHOOLS},
        "pending_question": None,
        "pending_idx": 0,
        "broadcast_count": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _clear_chat() -> None:
    st.session_state.history = {s.id: [] for s in SCHOOLS}
    st.session_state.broadcast_count = 0
    st.session_state.pending_question = None
    st.session_state.pending_idx = 0


def _has_pending() -> bool:
    return st.session_state.pending_question is not None


def _active_schools() -> list[SchoolDef]:
    return [s for s in SCHOOLS if st.session_state.enabled.get(s.id)]


# ---------------------------------------------------------------------------
# Render one school's chat column
# ---------------------------------------------------------------------------


def _render_school_column(school: SchoolDef) -> None:
    enabled = st.session_state.enabled.get(school.id, True)

    # Header with color dot
    st.markdown(
        f'<span class="school-dot" style="background:{school.color}"></span>**{school.name}**',
        unsafe_allow_html=True,
    )

    # Chat history
    for msg in st.session_state.history[school.id]:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.chat_message("user", avatar="🧑").write(content)
        elif role == "assistant":
            st.chat_message("assistant", avatar=school.emoji).write(content)
        elif role == "system":
            st.markdown(f'<p class="sys-msg">{content}</p>', unsafe_allow_html=True)

    # Typing indicator for schools currently being processed
    if _has_pending() and enabled:
        idx = st.session_state.pending_idx
        if idx < len(SCHOOLS) and SCHOOLS[idx].id == school.id:
            st.chat_message("assistant", avatar=school.emoji).write("_Thinking…_")


# ---------------------------------------------------------------------------
# Process one school per rerun cycle (progressive broadcast)
# ---------------------------------------------------------------------------


def _process_pending() -> None:
    """Handle the next school in the broadcast pipeline, then rerun."""
    if not _has_pending():
        return

    question = st.session_state.pending_question
    idx = st.session_state.pending_idx
    active = _active_schools()
    active_ids = {s.id for s in active}

    # Skip disabled schools
    while idx < len(SCHOOLS) and SCHOOLS[idx].id not in active_ids:
        # Still add a disabled notice
        st.session_state.history[SCHOOLS[idx].id].append(
            {"role": "system", "content": f"({SCHOOLS[idx].name} is disabled)"}
        )
        idx += 1
        st.session_state.pending_idx = idx

    if idx >= len(SCHOOLS):
        # All done
        st.session_state.pending_question = None
        st.session_state.pending_idx = 0
        st.session_state.broadcast_count += 1
        st.rerun()
        return

    school = SCHOOLS[idx]
    agent_map = st.session_state.get("_agents", {})
    llm = st.session_state.get("_llm")

    if llm is None or not agent_map:
        st.session_state.pending_question = None
        st.session_state.pending_idx = 0
        st.error("Advisers not initialised — please check your model configuration.")
        st.rerun()
        return

    with st.spinner(f"{school.name} is thinking…"):
        try:
            agent = agent_map[school.id]
            reply = _call_agent(agent, llm, school, question)
            st.session_state.history[school.id].append({"role": "assistant", "content": reply})
            opinion = AdviserOpinion(school=school.name, advice=reply)
            warning = length_warning(opinion)
            if warning:
                st.session_state.history[school.id].append(
                    {"role": "system", "content": f"[Length note] {warning}"}
                )
        except Exception as exc:
            st.session_state.history[school.id].append(
                {"role": "system", "content": f"Request failed: {exc}"}
            )

    st.session_state.pending_idx = idx + 1
    st.rerun()


# ---------------------------------------------------------------------------
# Main UI
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
    st.set_page_config(page_title="Hundred Schools Advisory", layout="wide")
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    _init_state()

    # --- Build agents (cached) ---
    settings = Settings.from_env()
    try:
        agents = _build_agents(settings.model, settings.api_key, settings.base_url)
        llm = _build_llm(settings)
        # Persist into session_state for _process_pending
        st.session_state["_agents"] = agents
        st.session_state["_llm"] = llm
    except Exception as exc:
        st.error(f"Failed to initialise advisers: {exc}")
        st.stop()

    # --- Check if we are mid-broadcast ---
    if _has_pending():
        _process_pending()
        return  # _process_pending already called rerun

    # --- Header ---
    hdr_left, hdr_right = st.columns([3, 1])
    with hdr_left:
        st.title("Hundred Schools Advisory")
    with hdr_right:
        st.write("")  # spacer
        st.write("")
        if st.button("New Chat", use_container_width=True):
            _clear_chat()
            st.rerun()

    # --- Toggle row ---
    st.caption("Toggle advisers on / off before sending.")
    tog_cols = st.columns(len(SCHOOLS))
    for col, school in zip(tog_cols, SCHOOLS, strict=True):
        with col:
            val = st.checkbox(
                school.name,
                value=st.session_state.enabled[school.id],
                key=f"tog_{school.id}",
            )
            st.session_state.enabled[school.id] = val

    # --- Chat columns ---
    chat_cols = st.columns(len(SCHOOLS))
    for col, school in zip(chat_cols, SCHOOLS, strict=True):
        with col:
            _render_school_column(school)

    # --- Input row ---
    st.write("")  # spacer
    question = st.text_area(
        "Your question",
        placeholder="Type your question…",
        key="question_input",
        height=80,
        label_visibility="collapsed",
    )

    left_btn, mid, right = st.columns([1, 1, 8])
    with left_btn:
        clicked = st.button("Send", use_container_width=True, type="primary")

    if clicked:
        text = (question or "").strip()
        if not text:
            st.warning("Please enter a question.")
            st.stop()
        if not _active_schools():
            st.warning("Enable at least one adviser.")
            st.stop()

        # Add user message to ALL columns (visible even for disabled schools)
        for s in SCHOOLS:
            st.session_state.history[s.id].append({"role": "user", "content": text})

        # Kick off broadcast from index 0
        st.session_state.pending_question = text
        st.session_state.pending_idx = 0
        st.rerun()


if __name__ == "__main__":
    _main()
