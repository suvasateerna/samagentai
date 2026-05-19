# conversation_runner.py
# Interactive CLI runner. All logic lives in agent.py.

from agent import get_greeting, process, make_session

def main():
    session = make_session(
        salutation = "",          # set to "sir", "madam", name etc. if known
    )

    print(f"Agent: {get_greeting(session)}")

    while True:
        user_input = input("User: ")
        result  = process(user_input, session)

        print(f"Agent: {result['reply']}")

        session = result["session"]

        if result["end_call"]:
            break
        
if __name__ == "__main__":
    main()