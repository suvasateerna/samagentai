# server_setup.md — How to run and connect to VAPI

## What These Files Do

```
VAPI (mic + ASR + voice)
    ↓ POST /chat/completions
server.py           ← HTTP layer only
    ↓
session_manager.py  ← per-call state
    ↓
agent.py            ← your state machine
    ↑
response text back to VAPI → spoken aloud
```

---

## Step 1 — Install dependencies

```bash
pip install flask
```

`flask` is the only external dependency. Everything else (`json`, `logging`, `time`, `datetime`, `os`) is Python standard library — no additional installs needed.

---

## Step 2 — Place files

Put these two files in the same folder as your `agent.py`:

- `server.py`
- `session_manager.py`

---

## Step 3 — Run the server

```bash
python server.py
```

You should see:

```
* Running on http://0.0.0.0:5000
```

To stop: `Ctrl+C`

---

## Step 4 — Install and run ngrok

If not installed:

```bash
# Mac
brew install ngrok

# Or download from https://ngrok.com/download
```

Run tunnel:

```bash
ngrok http 5000
```

ngrok will give you a URL like:

```
https://abc123.ngrok-free.app
```

Copy that URL. You need it for VAPI.

To stop: `Ctrl+C`

---

## Step 5 — Configure VAPI

1. Go to your VAPI dashboard
2. Open your assistant
3. Under **Model** settings, change provider to **Custom LLM**
4. Set the endpoint URL to:
   ```
   https://abc123.ngrok-free.app/chat/completions
   ```
   (use your actual ngrok URL)
5. Save the assistant

---

## Step 6 — Test

Hit the Talk button in VAPI dashboard.
Speak a scenario.
Watch your terminal — you'll see structured logs per turn:

```json
{"event": "turn_received", "call_id": "abc123", "user_input": "yes"}
{"event": "turn_response", "call_id": "abc123", "reply": "...", "state_before": "STATE_INITIAL", "state_after": "STATE_CALLBACK_CONFIRMATION", "end_call": false}
```

If a crash occurs in `agent.py`, you will see instead:

```json
{
  "event": "process_error",
  "severity": "fatal",
  "fatal": true,
  "call_id": "abc123",
  "user_input": "yes",
  "state_before": "STATE_INITIAL",
  "error": "..."
}
```

---

## Step 7 — Find your transcripts

After each call, a file is saved automatically:

```
transcripts/call_<call_id>.json
```

These transcripts are your primary diagnostic asset. Use them for:

- ASR drift analysis — what did the speech engine actually return?
- Normalization rules — which utterances need cleanup before keyword matching?
- Transition failures — which states are being missed or skipped?
- Interruption taxonomy — where did users speak over the agent?
- Prompt wording refinement — where did users sound confused?
- State machine gap discovery — signals that have no handler yet

---

## Verify agent.py has make_session()

`session_manager.py` imports `make_session` from `agent.py`:

```python
from agent import make_session
```

If your `make_session` function is named differently, update that import line.

---

## Health check

To confirm server is running:

```bash
curl http://localhost:5000/health
```

Should return:

```json
{ "status": "ok" }
```
