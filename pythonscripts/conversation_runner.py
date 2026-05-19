# conversation_runner.py
# Interactive CLI runner. All logic lives in agent.py.

from agent import get_greeting, process, INITIAL_STATE

def main():
    salutation  = ""          # set to "sir", "madam", name etc. if known
    state       = INITIAL_STATE

    print(f"Agent: {get_greeting(salutation)}")

    while True:
        user_input = input("User: ")
        result     = process(user_input, state)

        print(f"Agent: {result['reply']}")

        state = result["state"]

        if result["end_call"]:
            break

if __name__ == "__main__":
    main()