state = "IDENTIFIED"
print("Agent: Hello sir, calling regarding your emission test.")
while True:
    user_input = input("User: ").lower()
    if state == "IDENTIFIED":
        if "who" in user_input:
            print("Agent: You had done emission test earlier from our side.")
        elif "vehicle" in user_input:
            print("Agent: KA01AB1234")
        elif "busy" in user_input:
            print("Agent: Okay sir, shall I call later?")
            state = "CALLBACK"
        else:
            print("Agent: Sorry sir, could not understand.")
    elif state == "CALLBACK":
        if "yes" in user_input:
            print("Agent: Sure sir, we will call later.")
            print("Agent: Thank you sir.")
            break
        elif "no" in user_input:
            print("Agent: Okay sir, please let us know suitable time.")
        else:
            print("Agent: Sorry sir, could not understand.")