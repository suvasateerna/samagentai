"""
server.py — VAPI Custom LLM endpoint
Bridges VAPI's OpenAI-compatible /chat/completions calls to agent.py

Architecture:
    VAPI → POST /chat/completions → server.py → session_manager.py → agent.py → response
"""

from flask import Flask, request, jsonify, Response, stream_with_context

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
    payload = request.get_json(force=True)
    log.info(json.dumps({
    "event": "raw_payload",
    "payload": payload
}))

    call_id = (
        payload.get("call", {}).get("id")
        or payload.get("metadata", {}).get("call_id")
        or "unknown"
    )

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
        reply_text = "I'm sorry, I encountered an issue. Let me transfer you to our team."
        end_call = False
        result = {"reply": reply_text, "end_call": end_call, "session": session}
    logging.info(json.dumps({
    "event": "end_call_debug",
    "call_id": call_id,
    "end_call": result.get("end_call")
}))

    if isinstance(result, dict):
        reply_text = result.get("reply", "")
        end_call   = result.get("end_call", False)
        session    = result.get("session", session)
    else:
        reply_text = result
        end_call   = False

    state_after = session.get("state", "unknown")
    append_turn(session, user_input, reply_text, state_before, state_after)
    save_session(call_id, session)

    log.info(json.dumps({
        "event": "turn_response",
        "call_id": call_id,
        "reply": reply_text,
        "state_before": state_before,
        "state_after": state_after,
        "end_call": end_call
    }))

    # ── Detect streaming ──────────────────────────────────────────────────────
    use_stream = payload.get("stream", False)

    if not use_stream:
        response_body = {
            "id": f"chatcmpl-{call_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "agent",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply_text,
                    "tool_calls": [
        {
            "id": "call_end_1",
            "type": "function",
            "function": {
                "name": "end_call_tool",
                "arguments": "{}"
            }
        }
    ]
                },
                "finish_reason": "stop"
            }]
        }
        return jsonify(response_body), 200

    # ── SSE streaming response ────────────────────────────────────────────────
    chunk_id = f"chatcmpl-{call_id}"
    created  = int(time.time())

    def generate():
        # 1. Role chunk
        yield "data: " + json.dumps({
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": "agent",
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant"},
                "finish_reason": None
            }]
        }) + "\n\n"

        # 2. Content chunk
        yield "data: " + json.dumps({
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": "agent",
            "choices": [{
                "index": 0,
                "delta": {"content": reply_text},
                "finish_reason": None
            }]
        }) + "\n\n"

        # 3. Tool call chunk
        if end_call:
            yield "data: " + json.dumps({
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": "agent",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "tool_calls": [{
                            "index": 0,
                            "id": "call_end_1",
                            "type": "function",
                            "function": {
                                "name": "end_call_tool",
                                "arguments": "{}"
                            }
                        }]
                    },
                    "finish_reason": None
                }]
            }) + "\n\n"

        # 4. Finish chunk
        
        yield "data: " + json.dumps({
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": "agent",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }) + "\n\n"

        # 5. Done
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # debug=False — even for local dev, keeps behaviour predictable
    app.run(host="0.0.0.0", port=5000, debug=False)