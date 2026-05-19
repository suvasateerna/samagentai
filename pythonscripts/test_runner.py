# test_runner.py
# Loads all scenario JSON files from the scenarios/ folder,
# runs them against agent.py, and reports PASS / FAIL per step.

import json
import os
from agent import get_greeting, process, INITIAL_STATE

SCENARIOS_DIR = "scenarios"

def run_scenario(scenario):
    name        = scenario["name"]
    salutation  = scenario.get("salutation", "")
    inputs      = scenario["inputs"]
    expected    = scenario["expected"]

    print(f"\nScenario: {name}")
    print("-" * 60)

    # Print greeting but do not compare — it is not driven by user input
    print(f"  Agent : {get_greeting(salutation)}")

    state   = INITIAL_STATE
    passed  = 0
    failed  = 0

    for i, user_input in enumerate(inputs):
        result      = process(user_input, state)
        actual      = result["reply"]
        state       = result["state"]
        end_call    = result["end_call"]
        exp         = expected[i] if i < len(expected) else None

        status = "PASS" if actual == exp else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"  User  : {user_input}")
        print(f"  Agent : {actual}")

        if status == "FAIL":
            print(f"  [FAIL] Expected : {exp}")
            print(f"         Got      : {actual}")
        else:
            print("  [PASS]")

        if end_call:
            print("  [CALL ENDED]")
            break

    print(f"\n  Result: {passed} PASS / {failed} FAIL")
    return failed == 0

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