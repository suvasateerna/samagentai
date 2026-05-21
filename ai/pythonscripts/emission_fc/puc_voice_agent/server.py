"""
server.py — VAPI Custom LLM endpoint
Bridges VAPI's OpenAI-compatible /chat/completions calls to agent.py

Architecture:
    VAPI → POST /chat/completions → server.py → session_manager.py → agent.py → response
"""

from flask import Flask, request, jsonify
from session_manager import get_session, save_session, append_turn
from agent import process
import logging
import json
import time

# ── Structured logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    """
    VAPI sends an OpenAI-compatible messages array.
    We extract the latest user utterance, run it through agent.py,
    and return an OpenAI-compatible response.
    """
    payload = request.get_json(force=True)

    # ── Extract call/session ID from VAPI metadata ────────────────────────────
    # VAPI sends call metadata inside the payload
    call_id = (
        payload.get("call", {}).get("id")
        or payload.get("metadata", {}).get("call_id")
        or "unknown"
    )

    # ── Extract latest user utterance ─────────────────────────────────────────
    messages = payload.get("messages", [])
    user_input = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_input = msg.get("content", "").strip()
            break

    log.info(json.dumps({
        "event": "turn_received",
        "call_id": call_id,
        "user_input": user_input
    }))

    # ── Load or create session ────────────────────────────────────────────────
    session = get_session(call_id)
    state_before = session.get("state", "unknown")

    # ── Run through state machine ─────────────────────────────────────────────
    try:
        result = process(user_input, session)
    except Exception as e:
        log.error(json.dumps({
            "event": "process_error",
            "severity": "fatal",
            "fatal": True,
            "call_id": call_id,
            "user_input": user_input,
            "state_before": state_before,
            "error": str(e)
        }))
        return jsonify({
            "id": f"chatcmpl-{call_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "agent",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, I encountered an issue. Let me transfer you to our team."
                },
                "finish_reason": "stop"
            }]
        }), 200

    # result is either:
    #   a string (agent response text)
    #   or a dict with {"reply": "...", "end_call": True/False}
    if isinstance(result, dict):
        reply_text = result.get("reply", "")
        end_call   = result.get("end_call", False)
    else:
        reply_text = result
        end_call   = False

    state_after = session.get("state", "unknown")

    # ── Record turn in transcript ─────────────────────────────────────────────
    append_turn(session, user_input, reply_text, state_before, state_after)

    # ── Persist updated session ───────────────────────────────────────────────
    save_session(call_id, session)

    log.info(json.dumps({
        "event": "turn_response",
        "call_id": call_id,
        "reply": reply_text,
        "state_before": state_before,
        "state_after": state_after,
        "end_call": end_call
    }))

    # ── Build OpenAI-compatible response ─────────────────────────────────────
    response_body = {
        "id": f"chatcmpl-{call_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "agent",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply_text
                },
                "finish_reason": "stop"
            }
        ]
    }

    return jsonify(response_body), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # debug=False — even for local dev, keeps behaviour predictable
    app.run(host="0.0.0.0", port=5000, debug=False)