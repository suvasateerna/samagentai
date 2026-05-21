# test_runner.py
# Loads all scenario JSON files from the scenarios/ folder,
# runs them against agent.py, and reports PASS / FAIL per step.

import json
import os
from agent import get_greeting, process, make_session
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"


def run_scenario(scenario):
    name  = scenario["name"]
    turns = scenario["turns"]

    # Build session from scenario context block.
    # All keys are optional — make_session() defaults apply when absent.
    ctx = scenario.get("context", {})
    session = make_session(
        salutation              = ctx.get("salutation", ""),
        vehicle_number          = ctx.get("vehicle_number", ""),
        fc_expired              = ctx.get("fc_expired", False),
        whatsapp_number         = ctx.get("whatsapp_number", ""),
        personalization_allowed = ctx.get("personalization_allowed", True),
    )

    print(f"\nScenario: {name}")
    print("-" * 60)

    # --- Greeting assertion ---
    # If the scenario declares expect_greeting, assert it.
    # If absent, print only — governed behavior (DL-007, opening variants)
    # will require assertion at Step 5 when rendering layer is complete.
    assertions_passed = 0
    assertions_failed = 0
    turns_completed   = 0
    call_ended        = False
    greeting = get_greeting(session)
    expect_greeting = scenario.get("expect_greeting")
    if expect_greeting is not None:
        if greeting == expect_greeting:
            print(f"  Agent : {greeting}")
            print("  [PASS] greeting")
        else:
            assertions_failed += 1
            print(f"  Agent : {greeting}")
            print(f"  [FAIL] greeting")
            print(f"         Expected : {expect_greeting}")
            print(f"         Got      : {greeting}")
    else:
        print(f"  Agent : {greeting}")

    expect_end_call = scenario.get("expect_end_call")
    

    for i, turn in enumerate(turns):
        user_input   = turn["user"]
        expect_reply = turn.get("expect_reply")
        expect_state = turn.get("expect_state")

        result   = process(user_input, session)
        actual   = result["reply"]
        session  = result["session"]
        end_call = result["end_call"]

        print(f"  User  : {user_input}")
        print(f"  Agent : {actual}")

        # --- Reply assertion ---
        if expect_reply is not None:
            if actual == expect_reply:
                assertions_passed += 1
                print("  [PASS] reply")
            else:
                assertions_failed += 1
                print(f"  [FAIL] reply")
                print(f"         Expected : {expect_reply}")
                print(f"         Got      : {actual}")

        # --- State assertion (optional per turn) ---
        if expect_state is not None:
            actual_state = session["state"]
            if actual_state == expect_state:
                assertions_passed += 1
                print(f"  [PASS] state → {actual_state}")
            else:
                assertions_failed += 1
                print(f"  [FAIL] state")
                print(f"         Expected : {expect_state}")
                print(f"         Got      : {actual_state}")

        turns_completed += 1  # terminal turn is a completed turn

        # --- Premature end_call detection ---
        # If end_call fires but unconsumed turns remain, the scenario fails.
        # Early termination that silently skips assertions is a regression risk.
        if end_call:
            remaining = len(turns) - (i + 1)
            if remaining > 0:
                assertions_failed += 1
                print(f"  [FAIL] end_call fired at turn {i + 1} with {remaining} turn(s) remaining")
            else:
                print("  [CALL ENDED]")
            call_ended = True
            break

    if expect_end_call is True and not call_ended:
        assertions_failed += 1
        print("  [FAIL] expected end_call but call did not terminate")
    elif expect_end_call is False and call_ended:
        assertions_failed += 1
        print("  [FAIL] expected call to continue but end_call was triggered")

    print(f"\n  Turns      : {turns_completed} / {len(turns)}")
    print(f"  Assertions : {assertions_passed} PASS / {assertions_failed} FAIL")
    return assertions_failed == 0


def main():
    files = [f for f in os.listdir(SCENARIOS_DIR) if f.endswith(".json")]

    if not files:
        print("No scenario files found in scenarios/")
        return

    total_passed = 0
    total_failed = 0

    for filename in sorted(files):
        path = os.path.join(SCENARIOS_DIR, filename)
        with open(path, "r") as f:
            scenario = json.load(f)
        success = run_scenario(scenario)
        if success:
            total_passed += 1
        else:
            total_failed += 1

    print("\n" + "=" * 60)
    print(f"Total Scenarios: {total_passed + total_failed}")
    print(f"Passed         : {total_passed}")
    print(f"Failed         : {total_failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()