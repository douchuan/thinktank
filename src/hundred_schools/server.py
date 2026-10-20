"""FastAPI server for the Hundred Schools council Web UI."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from crewai import LLM

from hundred_schools.agents.experts import (
    create_confucian_agent,
    create_legalist_agent,
    create_strategist_agent,
    create_taoist_agent,
)
from hundred_schools.config import Settings

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
except ImportError:
    raise ImportError(
        "FastAPI is required for the Web UI. Install with: uv add fastapi uvicorn"
    ) from None


# ---------------------------------------------------------------------------
# Session model
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SchoolMeta:
    """One school's identity."""

    id: str
    name: str
    creator: object  # callable: (LLM) -> Agent


SCHOOLS: list[SchoolMeta] = [
    SchoolMeta("confucian", "Confucian", create_confucian_agent),
    SchoolMeta("legalist", "Legalist", create_legalist_agent),
    SchoolMeta("taoist", "Taoist", create_taoist_agent),
    SchoolMeta("strategist", "Strategist", create_strategist_agent),
]

SCHOOL_MAP = {s.id: s for s in SCHOOLS}


@dataclass
class Message:
    """A single chat message."""

    role: str  # "user" | "assistant"
    content: str


@dataclass
class SchoolSession:
    """Conversation history for one school."""

    history: list[Message] = field(default_factory=list)


@dataclass
class Session:
    """A user session containing per-school conversation histories."""

    id: str
    created_at: float
    schools: dict[str, SchoolSession] = field(default_factory=dict)

    def get_school_session(self, school_id: str) -> SchoolSession:
        if school_id not in self.schools:
            self.schools[school_id] = SchoolSession()
        return self.schools[school_id]


# In-memory session store
_sessions: dict[str, Session] = {}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str


class SchoolInfo(BaseModel):
    id: str
    name: str


class SessionCreateResponse(BaseModel):
    session_id: str
    schools: list[SchoolInfo]


class SchoolListResponse(BaseModel):
    schools: list[SchoolInfo]


class MessageResponse(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    assistant: MessageResponse
    history: list[MessageResponse]


class HistoryResponse(BaseModel):
    history: list[MessageResponse]


class SchoolReply(BaseModel):
    content: str


class BroadcastRequest(BaseModel):
    message: str


class BroadcastResponse(BaseModel):
    responses: dict[str, SchoolReply]


class CompressResponse(BaseModel):
    compressed: bool
    summary: str


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def _build_llm(settings: Settings) -> LLM:
    from hundred_schools.crews.council_crew import create_llm

    return create_llm(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Hundred Schools Advisory")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings = Settings.from_env()
    llm = _build_llm(settings)

    # Pre-create agents
    agents: dict[str, object] = {}
    for school in SCHOOLS:
        agents[school.id] = school.creator(llm)

    # --- Static frontend ---
    static_dir = Path(__file__).parent / "static"
    index_html = static_dir / "index.html"

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        if index_html.exists():
            return HTMLResponse(content=index_html.read_text(encoding="utf-8"))
        return HTMLResponse(
            content="<h1>Frontend not found. Run the server from the project root.</h1>"
        )

    @app.get("/schools", response_model=SchoolListResponse)
    async def list_schools():
        """Return available schools."""
        return SchoolListResponse(schools=[SchoolInfo(id=s.id, name=s.name) for s in SCHOOLS])

    @app.post("/sessions", response_model=SessionCreateResponse)
    async def create_session():
        """Create a new session."""
        session_id = uuid.uuid4().hex[:12]
        session = Session(id=session_id, created_at=time.time())
        _sessions[session_id] = session
        return SessionCreateResponse(
            session_id=session_id,
            schools=[SchoolInfo(id=s.id, name=s.name) for s in SCHOOLS],
        )

    @app.post("/sessions/{session_id}/chat/{school_id}", response_model=ChatResponse)
    async def chat(session_id: str, school_id: str, req: ChatRequest):
        """Send a message to a specific school and get a response."""
        session = _sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        school = SCHOOL_MAP.get(school_id)
        if not school:
            raise HTTPException(status_code=404, detail=f"Unknown school: {school_id}")

        agent = agents.get(school_id)
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")

        school_session = session.get_school_session(school_id)

        # Build system prompt from agent's role/goal/backstory
        system_prompt = (
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

        # Build message list with system prompt + history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in school_session.history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": req.message})

        # Call the LLM through the agent's llm
        try:
            assistant_content = llm.call(messages)
            if not isinstance(assistant_content, str):
                assistant_content = str(assistant_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM call failed: {e}") from e

        # Update history
        school_session.history.append(Message(role="user", content=req.message))
        school_session.history.append(Message(role="assistant", content=assistant_content))

        return ChatResponse(
            assistant=MessageResponse(role="assistant", content=assistant_content),
            history=[
                MessageResponse(role=m.role, content=m.content) for m in school_session.history
            ],
        )

    @app.get("/sessions/{session_id}/history/{school_id}", response_model=HistoryResponse)
    async def get_history(session_id: str, school_id: str):
        """Get conversation history for a specific school."""
        session = _sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if school_id not in SCHOOL_MAP:
            raise HTTPException(status_code=404, detail=f"Unknown school: {school_id}")

        school_session = session.schools.get(school_id)
        if not school_session:
            return HistoryResponse(history=[])

        return HistoryResponse(
            history=[
                MessageResponse(role=m.role, content=m.content) for m in school_session.history
            ],
        )

    @app.post("/sessions/{session_id}/broadcast", response_model=BroadcastResponse)
    async def broadcast(session_id: str, req: BroadcastRequest):
        """Send a message to all four schools simultaneously and return all responses."""
        session = _sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        responses: dict[str, SchoolReply] = {}

        for school in SCHOOLS:
            agent = agents[school.id]
            school_session = session.get_school_session(school.id)

            system_prompt = (
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

            messages = [{"role": "system", "content": system_prompt}]
            for msg in school_session.history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": req.message})

            try:
                assistant_content = llm.call(messages)
                if not isinstance(assistant_content, str):
                    assistant_content = str(assistant_content)
            except Exception as e:
                assistant_content = f"Reply failed: {e}"

            school_session.history.append(Message(role="user", content=req.message))
            school_session.history.append(Message(role="assistant", content=assistant_content))
            responses[school.id] = SchoolReply(content=assistant_content)

        return BroadcastResponse(responses=responses)

    @app.post("/sessions/{session_id}/compress", response_model=CompressResponse)
    async def compress_session(session_id: str):
        """Compress conversation history for all schools by summarizing.

        Keeps the latest 3 rounds per school and prepends a summary of earlier rounds.
        """
        session = _sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        summary_parts: list[str] = []

        for school in SCHOOLS:
            school_session = session.schools.get(school.id)
            if not school_session or not school_session.history:
                continue

            # Collect all user messages for this school
            user_msgs = [m.content for m in school_session.history if m.role == "user"]
            if len(user_msgs) <= 6:
                # Not enough to compress — keep as-is
                continue

            # Build a summary prompt
            compress_prompt = (
                f"You are a {school.name} adviser assistant. Below is a conversation "
                f"history.\n"
                f"Please compress the following {len(user_msgs)} rounds of user "
                f"questions into a 50-80 character summary,\n"
                f"preserving the core issues and discussion points.\n\n"
                + "\n".join(f"- Q{i + 1}: {q}" for i, q in enumerate(user_msgs[:-3]))
            )

            try:
                summary = llm.call([{"role": "user", "content": compress_prompt}])
                if not isinstance(summary, str):
                    summary = str(summary)
                summary_parts.append(f"[{school.name} History Summary] {summary}")
            except Exception:
                summary_parts.append(
                    f"[{school.name} History Summary] (compression failed, keeping original)"
                )
                continue

            # Keep the latest 3 rounds (6 messages: 3 user + 3 assistant)
            school_session.history = school_session.history[-6:]

        summary_text = "\n".join(summary_parts) if summary_parts else "No compression needed"

        return CompressResponse(compressed=bool(summary_parts), summary=summary_text)

    return app


def run() -> None:
    """CLI entry point for the web server."""
    import uvicorn

    uvicorn.run("hundred_schools.server:create_app", factory=True, host="0.0.0.0", port=8000)
