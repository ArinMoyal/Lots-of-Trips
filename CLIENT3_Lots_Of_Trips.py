import socket as socket_library


def accept_response(message):
    print(f"{message}")
    print("Thank you! Closing connection")
    connection.shutdown(0)

def send_request(message):
    try:
        connection.send(message.encode())
        response = connection.recv(1024).decode()
        accept_response(response)
    except ConnectionResetError:
        print("Connection Reset Error, server likely got terminated.")
        exit(1)

# Establishing a connection to the server
host = "localhost"
port = 35970

connection = socket_library.socket(socket_library.AF_INET, socket_library.SOCK_STREAM)  # SOCK_STREAM == TCP
try:
    connection.connect((host, port))
except ConnectionRefusedError:
    print("Connection refused, server is likely not online.")
    exit(1)

# Some constants
CONTRACT_LIST = {'N': 25, 'C': 40, 'S': 30, 'O': None}
MAX_DEPOSIT = 9999

print("(C)reate a new card")
print("(D)eposit money")
print("(E)xchange contract")
print("(P)ay for a ride")
print("(Q)uit")
choice = input("What would you like to do? ").upper()

if choice == "C":
    contract = input("What contract would you like to use? (N)orth, (C)enter, (S)outh, N(O)ne. : ").upper()
    if contract not in CONTRACT_LIST:
        print("Not a valid answer, defaulting to None.")
        contract = "O"
    request = " ".join((choice, contract))
    send_request(request)

elif choice == "D":
    input_id = input("What's the card's ID? ")
    deposit = input("How much money would you like to deposit?  $")
    if deposit.isnumeric() and 0 < int(deposit) <= MAX_DEPOSIT:
        request = " ".join((choice, input_id, deposit))
        send_request(request)
    else:
        print(f"Invalid deposit amount, must be a whole number and not more than {MAX_DEPOSIT}.")
        exit(1)

elif choice == "E":
    input_id = input("What's the card's ID? ")
    new_contract = input("What contract would you like to change to? (N)orth, (C)enter, (S)outh, N(O)ne. : ").upper()
    if new_contract in CONTRACT_LIST:
        request = " ".join((choice, input_id, new_contract))
        send_request(request)
    else:
        print(f"Invalid contract area.")
        exit(1)

elif choice == "P":
    input_id = input("What's the card's ID? ")
    area = input("What area are you traveling in? (N)orth, (C)enter, or (S)outh? ").upper()
    if area in ("N", "C", "S"):     # Can't travel in "None", so areas are specified.
        request = " ".join((choice, input_id, area))
        send_request(request)
    else:
        print(f"Invalid area.")
        exit(1)

elif choice == "Q":
    print("Disconnecting...")

else:
    print("Invalid option.")

connection.shutdown(0)
