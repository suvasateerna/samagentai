# agent.py

INITIAL_STATE = "INITIAL"

STATE_INITIAL                = "INITIAL"
STATE_CALLBACK_CONFIRMATION  = "CALLBACK_CONFIRMATION"
STATE_CALLBACK_SCHEDULING    = "CALLBACK_SCHEDULING"
STATE_DONE                   = "DONE"

UNKNOWN_INPUT = "Sorry, could not understand."

CONFIRM_WORDS = {"yes", "ok", "okay", "sure", "haan", "alright", "yeah", "yep"}
REJECT_WORDS  = {"no", "nope", "nahi", "later", "naa"}


def make_session(
    state=INITIAL_STATE,
    salutation="",
    vehicle_number="",
    fc_expired=False,
    whatsapp_number="",
    personalization_allowed=True,
):
    """
    Factory for a well-formed session object.
    Always use this to construct sessions — never build the dict by hand in tests or runners.

    Future additions (previous_state, interrupt_stack, transcript, retry_counters,
    escalation_flags, runtime_metadata, stt_confidence, operational_tasks,
    outcome_classification) go here when they arrive.

    Args:
        state                  (str)  : initial conversation state
        salutation             (str)  : e.g. "Sir", "Madam", "" if unknown
        vehicle_number         (str)  : e.g. "KA01AB1234", "" if unknown
        fc_expired             (bool) : True only when fc_expiry_status = expired (DL-009)
        whatsapp_number        (str)  : number to acknowledge, never confirm sent (DL-002)
        personalization_allowed(bool) : False suppresses name/salutation use (DL-007)

    Returns:
        dict: session object
    """
    return {
        "state": state,
        "greeted": False,
        "context": {
            "salutation":              salutation,
            "vehicle_number":          vehicle_number,
            "fc_expired":              fc_expired,
            "whatsapp_number":         whatsapp_number,
            "personalization_allowed": personalization_allowed,
        },
    }


# ---------------------------------------------------------------------------
# Rendering helpers
# Detection stays in state machine. Wording stays in operational script.
# Rendering stays here.
# Extraction to renderer.py deferred until 3+ helpers or localization arrives.
# ---------------------------------------------------------------------------

def render_suspicion_reply(ctx):
    """
    Render suspicion handling reply.
    Personalization gated on personalization_allowed and salutation (DL-007).
    Wording governed by DL-004.

    With honorific:    "No online payment or anything {honorific}, just informing before expiry."
    Without honorific: "No online payment or anything, just informing before expiry."
    """
    if ctx["personalization_allowed"] and ctx["salutation"]:
        return f"No online payment or anything {ctx['salutation']}, just informing before expiry."
    return "No online payment or anything, just informing before expiry."


def get_greeting(session):
    """
    Render the opening greeting line.

    Personalization is gated on context["personalization_allowed"] (DL-007).
    Salutation is used only when non-empty and personalization is permitted.

    Args:
        session (dict): well-formed session object

    Returns:
        str: greeting utterance
    """
    ctx = session["context"]
    if ctx["personalization_allowed"] and ctx["salutation"]:
        return f"Hello {ctx['salutation']}, calling regarding your emission test."
    return "Hello, calling regarding your emission test."


def process(user_input, session):
    """
    Advance the conversation by one turn.

    Returns a new session dict with state updated.
    Note: context dict is a shared reference — not deep-copied.
    Explicit mutability semantics deferred until runtime counters or transcript accumulation arrive.

    Args:
        user_input (str)  : raw utterance from customer
        session    (dict) : current session object (use make_session() to construct)

    Returns:
        dict with keys:
            reply    (str)  : agent's response
            session  (dict) : updated session object (state may have changed)
            end_call (bool) : True if conversation should terminate
    """
    normalized_input = user_input.strip().lower()
    user_input = user_input.lower().strip()
    words      = {w.strip(".,!?;:'\"") for w in user_input.split()}
    confirmed  = bool(words & CONFIRM_WORDS)
    rejected   = bool(words & REJECT_WORDS)

    state = session["state"]
    ctx   = session["context"]

    def reply(text, new_state, end_call=False):
        updated_session = {
            **session,
            "state":   new_state,
            "context": ctx,
        }
        return {"reply": text, "session": updated_session, "end_call": end_call}

    if state == STATE_INITIAL:
        if confirmed:
            return reply("Thank you. We will send you the details shortly.", STATE_DONE, end_call=True)

        # --- INFO_REQUEST handlers ---
        # Non-progressing interrupts — answer and remain in current state.
        # Triggers kept minimal; classify_intent() replacement is planned.
        # "where" marked as future refinement candidate (collision risk as breadth grows).
        elif "who" in user_input:
            return reply("You had done emission test earlier from our side.", STATE_INITIAL)
        elif "vehicle" in user_input:
            vehicle = ctx["vehicle_number"] if ctx["vehicle_number"] else "not available"
            return reply(vehicle, STATE_INITIAL)
        elif "why" in user_input:
            return reply("Pollution certificate only\u2026 emission test renewal.", STATE_INITIAL)
        elif "long" in words or "minutes" in words:
            return reply("Normally 10\u201315 minutes only if crowd is less.", STATE_INITIAL)
        elif "charge" in words or "charges" in words or "cost" in words or "price" in words:
            return reply("We'll confirm exact amount when you visit.", STATE_INITIAL)
        elif "documents" in words:
            return reply("No documents required.", STATE_INITIAL)
        elif "location" in words or "address" in words or "where" in words:
            return reply("Our team will share the location details with you after the call.", STATE_INITIAL)

        # --- OBJECTION handlers ---
        # Non-progressing — answer and remain in current state.
        # IRRITATION: tone-derived, undetectable by text — out of scope Phase 1.
        # render_suspicion_reply() is the first rendering helper (DL-004, DL-007).
        # SUSPICION: "payment" is a future collision hotspot — "online payment available?",
        # "how much payment?" etc. Acceptable for Phase 1. Revisit at classify_intent() replacement.
        elif "payment" in words or "spam" in words or "scam" in words or "genuine" in words:
            return reply(render_suspicion_reply(ctx), STATE_INITIAL)
        # URGENCY_PUSH: "later" also exists in REJECT_WORDS.
        # This handler must remain before any rejected-branch handling in STATE_INITIAL.
        # In STATE_CALLBACK_CONFIRMATION, rejected fires instead — that is correct and intentional.
        # If STATE_INITIAL ever gains a rejected branch, revisit ordering here immediately.
        # "later" = deferment, "urgent" = urgency challenge — unified in Phase 1, split expected later.
        
        elif "later" in words or "urgent" in words:
            return reply("Small delay okay\u2026 but if pollution certificate fully expires, later insurance renewal issue can come.", STATE_INITIAL)
        elif "police" in words or "insurance" in words or "legal" in words or "invalid" in words:
            return reply("Later renewal or document issue can come. Better to renew before expiry.", STATE_INITIAL)

        # --- DISENGAGEMENT: BUSY ---
        elif "busy" in user_input:
            return reply("Okay, shall I call later?", STATE_CALLBACK_CONFIRMATION)
        # --- GREETING / ACKNOWLEDGEMENT ---
        elif normalized_input in ["hello", "hi", "hey"]:
            return reply("Your emission test is pending. Would you like to renew it now?", STATE_INITIAL)
        else:
            return reply(UNKNOWN_INPUT, STATE_INITIAL)

    elif state == STATE_CALLBACK_CONFIRMATION:
        if confirmed:
            return reply("Sure, we will call later. Thank you.", STATE_DONE, end_call=True)
        elif rejected:
            return reply("Okay, please let us know a suitable time.", STATE_CALLBACK_SCHEDULING)
        else:
            return reply(UNKNOWN_INPUT, STATE_CALLBACK_CONFIRMATION)

    elif state == STATE_CALLBACK_SCHEDULING:
        return reply(f"Sure, we will call you {user_input}. Thank you.", STATE_DONE, end_call=True)

    else:
        return reply(UNKNOWN_INPUT, state)