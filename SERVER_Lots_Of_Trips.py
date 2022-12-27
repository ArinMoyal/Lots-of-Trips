import sqlite3
import socket as socket_library


#   Function for creating a new card
def create_new_card(new_contract_id):
    if c.lastrowid >= 9999:
        client.send(f"Too many cards registered, cannot process request.")
        return
    c.execute(f"INSERT INTO cards (contract)VALUES ('{new_contract_id}')")
    conn.commit()
    client.send(f"Card created successfully! The card ID is: {c.lastrowid}".encode())
    print(f"Card created successfully! The card ID is: {c.lastrowid}")


#   Function for getting a card's ID to make sure it exists
def card_exists(input_card_id):
    c.execute(f"""SELECT card_id
                FROM cards
                WHERE card_id = '{input_card_id}'
                """)
    return c.fetchone()


#   Function for getting a card's balance using its ID
def get_card_balance(input_card_id):
    c.execute(f"""SELECT wallet
                FROM cards
                WHERE card_id = '{input_card_id}'""")
    return c.fetchone()


#   Function for getting the contract a card has using its ID
def get_card_contract(input_card_id):
    c.execute(f"""SELECT contract
                        FROM cards
                        WHERE card_id = '{input_card_id}'
                        """)
    return c.fetchone()


#   Function to update a card's balance using its ID and user-inputted amount
def update_balance(input_card_id, input_amount):
    c.execute(f"""UPDATE cards
                SET wallet = wallet + {input_amount}
                WHERE card_id = '{input_card_id}'
                """)
    conn.commit()


#   Function to update a card's contract using its ID and user-inputted new contract
def update_contract(input_card_id, input_contract):
    c.execute(f"""UPDATE cards
                SET contract = '{input_contract}'
                WHERE card_id = '{input_card_id}'
                """)
    conn.commit()


#   Function to deposit money to card using its ID and user-inputted amount
def deposit(input_card_id, input_amount):
    if not card_exists(input_card_id):
        client.send("Invalid card ID.".encode())
        return
    print(f"Card ({input_card_id}) exists!")
    update_balance(input_card_id, input_amount)
    new_balance = get_card_balance(input_card_id)
    client.send(f"Deposit successful! Your new balance is: ${new_balance[0]}".encode())


#   Function to exchange contracts using a card's ID and user-inputted contract
def exchange_contract(input_card_id, input_contract):
    if not card_exists(input_card_id):
        client.send("Invalid card ID.".encode())
        return
    print(f"Card ({input_card_id}) exists!")
    update_contract(input_card_id, input_contract)
    if get_card_contract(input_card_id)[0] == "N":
        new_contract = "North"
    elif get_card_contract(input_card_id)[0] == "C":
        new_contract = "Center"
    elif get_card_contract(input_card_id)[0] == "S":
        new_contract = "South"
    else:
        new_contract = "None"
    client.send(f"Contract exchanged successfully to {new_contract}!".encode())


#   Function to pay for a ride using a card's ID and user-inputted destination
def pay_for_a_ride(input_card_id, input_destination):
    this_contract = get_card_contract(input_card_id)
    this_balance = get_card_balance(input_card_id)
    if not card_exists(input_card_id):
        client.send("Invalid card ID. No action will be taken.".encode())
        return
    print(f"Card ({input_card_id}) exists!".encode())
    if this_contract[0] not in CONTRACT_LIST:
        client.send("Invalid area.".encode())
        return
    elif this_contract[0] == input_destination:
        client.send("Done. Have a nice ride!".encode())
    elif this_balance[0] >= CONTRACT_LIST.get(input_destination):
        c.execute(f"""UPDATE cards
                        SET wallet = wallet - {CONTRACT_LIST.get(input_destination)}
                        WHERE card_id = {input_card_id}
                        """)
        conn.commit()
        updated_balance = get_card_balance(input_card_id)
        client.send(
            f"Payment successful! Your new balance is ${updated_balance[0]}. Have a nice ride!".encode())
    else:
        client.send("Not enough money for this ride. Try depositing!".encode())


def init_db_connection():
    conn = sqlite3.connect('Card_Database.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS cards (
                card_id INTEGER PRIMARY KEY,
                contract TEXT DEFAULT 'O' NOT NULL,
                wallet INTEGER DEFAULT 0 NOT NULL
            )""")

    conn.commit()

    return c, conn


def create_server(port):
    connection = socket_library.socket(
        socket_library.AF_INET, socket_library.SOCK_STREAM)
    connection.bind(("localhost", port))
    connection.listen(1)
    connection.settimeout(2.5)
    return connection


def accept_connection():
    try:
        client, address = connection.accept()
        if client not in clients:
            clients[client] = address
            client.settimeout(2.5)
    except socket_library.timeout:
        print("No accept. Connection timed out.")


#   A few constants.
POSSIBLE_ACTIONS = ["C", "D", "E", "P"]
CONTRACT_LIST = {'N': 25, 'C': 40, 'S': 30, 'O': None}

#   Establishing a connection to the database and creating a table if it doesn't exist yet
c, conn = init_db_connection()

#   Creating the server
connection = create_server(port=35970)
clients = {}

#   Main program
while True:
    accept_connection()
    aborted_connections = []
    for client in clients:
        try:
            data = client.recv(1024).decode().split()
            print("Received \"" + str(data) + "\" from", clients[client])
            action_code = data[0]
            if action_code == "C":
                contract_id = data[1]
                create_new_card(contract_id)
            elif action_code == "D":
                card_id = data[1]
                amount = data[2]
                deposit(card_id, amount)
            elif action_code == "P":
                card_id = data[1]
                destination = data[2]
                pay_for_a_ride(card_id, destination)
            elif action_code == "E":
                card_id = data[1]
                chosen_contract = data[2]
                exchange_contract(card_id, chosen_contract)
            else:
                print("Invalid option.")
                client.send("Invalid option.".encode())
        except socket_library.timeout:
            print(f"No message received from {clients[client]}.")
        except ConnectionError:
            print(f"{clients[client]} has disconnected.")
            aborted_connections.append(client)
        except IndexError:
            print(
                f"No data received from {clients[client]}, closing connection.")
            aborted_connections.append(client)
    for client in aborted_connections:
        del clients[client]
