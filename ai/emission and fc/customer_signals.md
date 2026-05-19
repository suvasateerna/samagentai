# customer_signals.md

# Purpose

This document defines the taxonomy of customer signals used in the Vehicle Pollution Certificate Renewal Reminder System.

It exists to:

- establish clean intent boundaries before implementation,
- guide scenario construction,
- support future intent classification (rule-based or AI-assisted),
- and prevent signal boundary ambiguity across revisions.

This document does NOT implement signal detection.
Signal detection lives in `agent.py`.

---

# Document Control

| Field         | Value                             |
| ------------- | --------------------------------- |
| Document Name | Customer Signal Taxonomy          |
| File Name     | `customer_signals.md`             |
| Version       | 1.1                               |
| Status        | Draft                             |
| Owner         | Operations / Communication Design |
| Last Updated  | 2026-05-19                        |

---

# Signal Categories

---

## CONFIRMATION

Customer is agreeing, accepting, or indicating willingness to proceed.

### Examples

- "yes"
- "ok"
- "okay"
- "sure"
- "haan"
- "alright"
- "yeah"
- "yep"
- "fine"
- "go ahead"

### Current Detection

`CONFIRM_WORDS` set in `agent.py`

### Future Detection

`classify() == CONFIRMATION`

### Governs

- CALLBACK state: proceed to close call
- SCHEDULE state: not applicable

---

## REJECTION

Customer is declining, refusing, or indicating unwillingness to proceed immediately.

### Examples

- "no"
- "nope"
- "nahi"
- "naa"
- "not now"
- "later"
- "don't want"

### Current Detection

`REJECT_WORDS` set in `agent.py`

### Future Detection

`classify() == REJECTION`

### Governs

- CALLBACK state: move to SCHEDULE state
- General flow: preserve customer autonomy per DL-006

### Phase 1 Unification Note

"no" and "later" are semantically distinct signals:

| Signal  | Semantic Meaning                        |
| ------- | --------------------------------------- |
| "no"    | resistance, refusal                     |
| "later" | deferment, future possibility preserved |

Runtime handling is intentionally unified in Phase 1 — both transition to SCHEDULE state.
This unification is a Phase 1 simplification, not a true semantic equivalence.

Future phases will likely care about this distinction for:

- retry logic,
- callback prioritization,
- outcome classification,
- and analytics.

### Known Ambiguity

"not now" and "no problem" both contain "no".
Current word-set detection is acceptable for Phase 1.
NLU layer resolves this in future phases.

---

## INFO_REQUEST

Customer is asking for clarification or information without objecting to the call purpose.

### Sub-signals

| Sub-signal | Example Phrases                                                         |
| ---------- | ----------------------------------------------------------------------- |
| IDENTITY   | "who is this", "which company", "where from"                            |
| VEHICLE    | "which vehicle", "what number"                                          |
| PURPOSE    | "what is this for", "why calling"                                       |
| DURATION   | "how long it takes", "how much time"                                    |
| PRICING    | "how much charge", "what is the cost"                                   |
| DOCUMENTS  | "what documents needed", "what to bring"                                |
| LOCATION   | "where exactly", "send location", "how to come", "WhatsApp the address" |

### Current Detection

Keyword matching in `agent.py`

### Future Detection

`classify() == INFO_REQUEST` with sub-signal resolution

### Governs

- Non-progressing interrupts — conversation returns to main flow after response
- Does not advance business state
- LOCATION sub-signal: acknowledge during call per DL-002, actual sending becomes post-call operational task per DL-010

---

## OBJECTION

Customer is expressing resistance, suspicion, or friction without fully disengaging.

### Sub-signals

| Sub-signal   | Example Phrases                                                  |
| ------------ | ---------------------------------------------------------------- |
| SUSPICION    | "how did you get my number", "is this spam", "online payment ah" |
| URGENCY_PUSH | "can do later no", "not urgent"                                  |
| LEGAL_QUERY  | "police checking ah", "will insurance really become invalid"     |
| IRRITATION   | customer sounds frustrated or dismissive                         |

### Current Detection

Keyword matching in `agent.py`

### Future Detection

`classify() == OBJECTION` with sub-signal resolution

### Governs

- De-escalation responses per DL-004, DL-005, DL-006
- Soft consequence framing only
- Never argumentative handling
- Exit gracefully if resistance persists

### IRRITATION Detection Note

IRRITATION is qualitatively different from all other sub-signals.
It is tone-derived, not text-derived.
Current text-based architecture cannot reliably detect it.
Future voice deployments will require one of:

- operator annotation,
- sentiment analysis,
- or prosody detection.

IRRITATION should not be treated as structurally equivalent to keyword-detectable signals.

---

## DISENGAGEMENT

Customer is signaling the conversation is not relevant or they are exiting.

### Sub-signals

| Sub-signal      | Example Phrases                          |
| --------------- | ---------------------------------------- |
| ALREADY_RENEWED | "already done", "already renewed"        |
| VEHICLE_SOLD    | "sold the vehicle", "not my vehicle"     |
| NOT_INTERESTED  | "don't call again", "not interested"     |
| BUSY            | "busy now", "in a meeting", "call later" |

### Current Detection

Keyword matching in `agent.py`

### Future Detection

`classify() == DISENGAGEMENT` with sub-signal resolution

### Governs

- Graceful exit responses
- Post-call outcome classification:
  - ALREADY_RENEWED → `already_renewed`
  - NOT_INTERESTED → `declined`
  - BUSY → callback acknowledgment, post-call follow-up task

---

## SCHEDULE_INTENT

Customer is indicating a specific time or willingness to act at a future point.

### Examples

- "tomorrow"
- "this weekend"
- "10pm"
- "Monday"
- "evening"
- "next week"

### Naming Note

Previously considered `COMPLETION_SIGNAL`. Renamed to `SCHEDULE_INTENT` because:

- customer has not completed anything,
- signal indicates future timing intent only,
- avoids future conflict with call completion, workflow completion, or certificate completion terminology.

### Current Detection

Any input in SCHEDULE state treated as SCHEDULE_INTENT

### Future Detection

`classify() == SCHEDULE_INTENT` with time entity extraction

### Governs

- SCHEDULE state: acknowledge time, close call gracefully
- Post-call task: log preferred callback or visit time

---

## ESCALATION_TRIGGER

Customer is requesting operational routing beyond the scope of the current conversation.

### Examples

- "I want your supervisor"
- "connect me to your manager"
- "I will complain"
- abusive or hostile behavior

### Distinction From OBJECTION

OBJECTION signals are conversational — the agent handles them within the flow.
ESCALATION_TRIGGER signals are operational routing instructions — they require handoff or intervention beyond the agent's conversational scope.

Example:

- "How did you get my number?" → OBJECTION: SUSPICION — handled conversationally
- "I want your supervisor" → ESCALATION_TRIGGER — operational routing required

### Current Detection

Not yet implemented in `agent.py`

### Future Detection

`classify() == ESCALATION_TRIGGER`

### Governs

- Graceful acknowledgment during call
- Post-call escalation task generation
- Handling rules pending operational definition

### Phase 1 Note

ESCALATION_TRIGGER handling is not defined in the current operational script.
Runtime behavior is undefined for Phase 1.
Requires separate operational documentation before implementation.

---

# Signal Boundary Rules

1. A signal is classified by intent, not by exact wording
2. Ambiguous signals default to the safer, lower-escalation response
3. No signal classification should trigger an operational commitment during the call
4. Sub-signals that cannot be resolved fall back to parent signal handling
5. UNKNOWN signals follow escalation threshold logic:
   - UNKNOWN once → clarification attempt
   - UNKNOWN repeatedly → graceful exit

---

# Relationship To Governing Documents

| Signal                 | Governing Decision Log Entry                 |
| ---------------------- | -------------------------------------------- |
| CONFIRMATION           | DL-006 — customer autonomy preserved         |
| REJECTION              | DL-006 — customer autonomy preserved         |
| INFO_REQUEST: IDENTITY | DL-003, DL-008                               |
| INFO_REQUEST: LOCATION | DL-002, DL-010                               |
| OBJECTION: SUSPICION   | DL-004                                       |
| OBJECTION: LEGAL_QUERY | DL-005                                       |
| OBJECTION: IRRITATION  | DL-006                                       |
| DISENGAGEMENT          | DL-006                                       |
| ESCALATION_TRIGGER     | DL-010 — operational routing, post-call task |

---

# Known Gaps

The following signal handling areas are not yet defined and require future documentation:

- ESCALATION_TRIGGER handling rules and ownership
- hostile caller termination policy
- repeat caller detection
- multilingual signal variants
- STT noise and mishearing recovery
- signal confidence scoring
- interruption depth limits
- REJECTION semantic split runtime handling (hard refusal vs deferment)
- IRRITATION detection in voice deployments

---

# Revision History

| Version | Date       | Description                                                                                                                                                                                                                            |
| ------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0     | 2026-05-19 | Initial baseline                                                                                                                                                                                                                       |
| 1.1     | 2026-05-19 | LOCATION folded under INFO_REQUEST, COMPLETION_SIGNAL renamed to SCHEDULE_INTENT, REJECTION semantic divergence documented, IRRITATION detection note added, UNKNOWN threshold logic defined, ESCALATION_TRIGGER added as new category |

---

# Related Documents

| Document                      | Purpose                                 |
| ----------------------------- | --------------------------------------- |
| `01_context_and_rationale.md` | Communication philosophy and governance |
| `02_operational_script.md`    | Executable conversation script          |
| `03_decision_log.md`          | Wording decision history                |
