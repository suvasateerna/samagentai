## Test Harness Semantics

Current limitation:
`expect_end_call` at scenario level is semantically ambiguous for multi-turn scenarios.

Current meaning:
Whether the call has ended by completion of all turns.

Future options:

- `expect_final_end_call`
- per-turn `expect_end_call`

Deferred because:
Current scenario volume does not justify added harness complexity.

Here are the corrected additions:

---

## Intent Classification

Current limitation:
`classify_intent()` is a planned replacement for the current keyword-based intent detection.

Current meaning:
Intent is detected via minimal keyword triggers directly in the state machine.

Future options:

- Introduce a dedicated `classify_intent()` layer for centralized intent routing

Deferred because:
Current trigger volume does not justify the abstraction. Revisit when keyword collisions accumulate.

---

## Payment Keyword Collision

Current limitation:
`"payment"` is handled under suspicion detection but is a known collision hotspot.

Current meaning:
Any utterance containing "payment" is routed to suspicion reply.

Future options:

- Disambiguate at `classify_intent()` replacement ("online payment available?", "how much payment?" etc.)

Deferred because:
Acceptable false-positive rate for Phase 1 volume.

---

## Renderer Extraction

Current limitation:
Rendering helpers live inline rather than in a dedicated `renderer.py`.

Current meaning:
All rendering co-located with state machine logic.

Future options:

- Extract to `renderer.py`

Deferred because:
Fewer than 3 helpers exist and localization has not arrived. Revisit when either threshold is crossed.

---

## URGENCY_PUSH Ordering Dependency

Current limitation:
`URGENCY_PUSH` handler must remain before any rejected-branch handling in `STATE_INITIAL`.

Current meaning:
Ordering is correct today because `STATE_INITIAL` has no rejected branch.

Future options:

- Revisit ordering immediately if `STATE_INITIAL` ever gains a rejected branch

Deferred because:
Not yet a live risk. Flagged as a hard revisit trigger.

---

## Tone Detection (Irritation)

Current limitation:
Reliable irritation detection is out of scope for text-only Phase 1 handling.

Current meaning:
Irritation is tone-derived; text alone is insufficient for reliable detection in the current architecture.

Future options:

- Tone/prosody-aware detection in future voice-aware phases

Deferred because:
Requires voice/audio signals not available in Phase 1.

---

## "later" and "urgent" Unification

Current limitation:
`"later"` (deferment intent) and `"urgent"` (urgency skepticism/challenge) currently share the same operational path.

Current meaning:
Both routed through `URGENCY_PUSH` in Phase 1.

Future options:

- Split into separate handlers with distinct responses

Deferred because:
Unified handling is acceptable for Phase 1.

---

## "where" Keyword Collision Risk

Current limitation:
`"where"` is used as an `INFO_REQUEST` trigger but is a future collision candidate.

Current meaning:
Minimal trigger, acceptable for current intent breadth.

Future options:

- Refine or disambiguate as intent coverage grows

Deferred because:
Collision risk is low at current breadth. Revisit as new intents are added.
