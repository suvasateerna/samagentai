# agent.py

INITIAL_STATE = "IDENTIFIED"

STATE_IDENTIFIED = "IDENTIFIED"
STATE_CALLBACK = "CALLBACK"
STATE_SCHEDULE = "SCHEDULE"
STATE_DONE = "DONE"

UNKNOWN_INPUT = "Sorry, could not understand."

CONFIRM_WORDS = {"yes", "ok", "okay", "sure", "haan", "alright", "yeah", "yep"}
REJECT_WORDS  = {"no", "nope", "nahi", "later", "naa"}


def get_greeting(salutation=""):
    if salutation:
        return f"Hello {salutation}, calling regarding your emission test."
    return "Hello, calling regarding your emission test."

def process(user_input, state):
    """
    Args:
        user_input (str): user utterance
        state (str): current conversation state

    Returns:
        dict with keys:
            reply    (str)  : agent's response
            state    (str)  : updated state
            end_call (bool) : True if conversation should terminate
    """
    user_input = user_input.lower().strip()
    words     = set(user_input.split())
    confirmed = bool(words & CONFIRM_WORDS)
    rejected  = bool(words & REJECT_WORDS)

    if state == STATE_IDENTIFIED:
        if "who" in user_input:
            return {"reply": "You had done emission test earlier from our side.", "state": STATE_IDENTIFIED, "end_call": False}
        elif "vehicle" in user_input:
            return {"reply": "KA01AB1234", "state": STATE_IDENTIFIED, "end_call": False}
        elif "busy" in user_input:
            return {"reply": "Okay, shall I call later?", "state": STATE_CALLBACK, "end_call": False}
        else:
            return {"reply": UNKNOWN_INPUT, "state": STATE_IDENTIFIED, "end_call": False}

    elif state == STATE_CALLBACK:
        if confirmed:
            return {"reply": "Sure, we will call later. Thank you.", "state": STATE_DONE, "end_call": True}
        elif rejected:
            return {"reply": "Okay, please let us know a suitable time.", "state": STATE_SCHEDULE, "end_call": False}
        else:
            return {"reply": UNKNOWN_INPUT, "state": STATE_CALLBACK, "end_call": False}

    elif state == STATE_SCHEDULE:
        return {"reply": f"Sure, we will call you {user_input}. Thank you.", "state": STATE_DONE, "end_call": True}

    else:
        return {"reply": UNKNOWN_INPUT, "state": state, "end_call": False}