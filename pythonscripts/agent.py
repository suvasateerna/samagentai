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
        "context": {
            "salutation":              salutation,
            "vehicle_number":          vehicle_number,
            "fc_expired":              fc_expired,
            "whatsapp_number":         whatsapp_number,
            "personalization_allowed": personalization_allowed,
        },
    }


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
    user_input = user_input.lower().strip()
    words      = {w.strip(".,!?;:'\"") for w in user_input.split()}
    confirmed  = bool(words & CONFIRM_WORDS)
    rejected   = bool(words & REJECT_WORDS)

    state = session["state"]
    ctx   = session["context"]

    def reply(text, new_state, end_call=False):
        updated_session = {
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

        # --- DISENGAGEMENT: BUSY ---
        elif "busy" in user_input:
            return reply("Okay, shall I call later?", STATE_CALLBACK_CONFIRMATION)
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