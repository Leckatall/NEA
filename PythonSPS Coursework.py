

# Exercise 1

def AND(bools):
    for e in bools:
        if e is False:
            return False
    return True


def OR(bools):
    for e in bools:
        if e is True:
            return True
    return False


# Parity-based implementation of XOR
def XOR_1(bools):
    p = False
    for e in bools:
        if e is True:
            p = not p
    return p


# Exclusively 1 True value allowed
def XOR_2(bools):
    p = False
    for e in bools:
        if e is True:
            if p:
                return False
            p = True
    return p


# Function index
logic_gate = {"AND": AND,
              "OR": OR,
              "XOR": XOR_1}

def user_input_handling(message, data_type):
    user = input(message)

# Interacts with the user and provides the interface for the logic gates
def user_management():
    print("How would you like to enter your binary inputs?")
    print("(1) - Responding to repeated queries until you provide an empty element")
    print("(2) - Comma separated list")
    print("(3) - Custom character(or series of characters) separated list")
    choice = input("Please enter a single digit representing your choice:\n")
    while not choice.isdigit():
        choice = input("Choice not a digit. Please try again:\n")
    choice = int(choice)
    bools = [bool(e) for e in input("Enter a list of boolean elements separated by a (\",\")"
                                    " that you want the binary operation to be performed on.").split(",")]
    print("Select which binary operation you want to perform from the following list.")
    for bin_op in logic_gate.keys():
        print(bin_op)
        # .upper() provides some more input sanitization without risking additional exceptions
    operation_selection = input("Please enter a name of an operation listed.").upper()
    while operation_selection not in logic_gate.keys():
        operation_selection = input("Please enter a name of an operation listed.").upper()
    print("Collected inputs and operation choice from the user executing operation now")
    print(f"result of {operation_selection}({bools}) is {logic_gate[operation_selection](bools)}")

    print("Please enter the binary inputs you want to provide to the logic gate")









