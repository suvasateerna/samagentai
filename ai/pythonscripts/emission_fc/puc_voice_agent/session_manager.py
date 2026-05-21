"""
session_manager.py — Per-call session persistence
Keeps state isolated per call_id using in-memory store.
Swap _store for Redis or DB when scaling beyond single process.

Each session contains everything agent.py needs:
    - current state
    - transcript history
    - runtime counters
"""

import json
import os
from datetime import datetime
from agent import make_session  # reuse your existing factory

# ── In-memory store ───────────────────────────────────────────────────────────
# key: call_id (str)
# value: session dict
_store: dict = {}

# ── Transcript directory ──────────────────────────────────────────────────────
TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


def get_session(call_id: str) -> dict:
    """
    Returns existing session for call_id, or creates a fresh one.
    """
    if call_id not in _store:
        session = make_session()
        session["call_id"] = call_id
        session["started_at"] = datetime.utcnow().isoformat()
        session["transcript"] = []
        _store[call_id] = session

    return _store[call_id]


def save_session(call_id: str, session: dict) -> None:
    """
    Persists updated session back to store.
    Also flushes transcript to disk on every turn for crash safety.
    """
    _store[call_id] = session
    _flush_transcript(call_id, session)


def _flush_transcript(call_id: str, session: dict) -> None:
    """
    Writes full session transcript to a JSON file after every turn.
    Safe to call repeatedly — overwrites same file each time.
    """
    path = os.path.join(TRANSCRIPT_DIR, f"call_{call_id}.json")
    payload = {
        "call_id": call_id,
        "started_at": session.get("started_at"),
        "final_state": session.get("state"),
        "turns": session.get("transcript", [])
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def append_turn(session: dict, user_input: str, agent_reply: str,
                state_before: str, state_after: str) -> None:
    """
    Integration-layer transcript logger — called by server.py after each turn.
    agent.py remains pure state-machine logic and never calls this directly.
    """
    session.setdefault("transcript", []).append({
        "turn": len(session["transcript"]) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "user_raw": user_input,
        "user_normalized": user_input,   # normalizer.py will populate this later
        "agent": agent_reply,
        "state_before": state_before,
        "state_after": state_after
    })