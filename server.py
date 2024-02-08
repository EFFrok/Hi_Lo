import random
import math
import socket
import threading
import time

# Global variables
MAX_PLAYERS = 4

def main():
    # Initialize connections
    players, player_names = connections()

    # Start the game logic
    game_logic(players, player_names)

def connections():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5555))
    server_socket.listen(MAX_PLAYERS)

    print("Waiting for players to connect...")

    # Initialize lists for players and their names
    players = []
    player_names = []

    while len(players) < MAX_PLAYERS:
        # Accept incoming connections
        client_socket, client_address = server_socket.accept()
        players.append(client_socket)
        
        # Receive and store player name
        player_name = client_socket.recv(1024).decode()
        player_names.append(player_name)
        print(f"{player_name} connected.")

        # Notify players of connection status
        num_players_connected = len(players)
        for player_socket in players:
            player_socket.send(f"Players connected: {num_players_connected}. Waiting for other players...".encode())

        # If enough players have connected, break out of the loop
        if num_players_connected >= 2:
            break

    return players, player_names

def game_logic(players, player_names):
    # Game initialization
    player_equations = {}
    hands = {name: [] for name in player_names}
    target_choices = {}  # Not sure what this is for, you might need to define it
    player_results = {}

    # Handle game start
    handle_game_start(players, player_names, player_equations, hands, target_choices, player_results)

def handle_game_start(players, player_names, player_equations, hands, target_choices, player_results):
    # Notify players and wait for their readiness
    for player_socket in players:
        player_socket.send(f"Players connected: {len(players)}. Would you like to start the game with {len(players)} players? (yes/no)".encode())

    all_ready = all(player_socket.recv(1024).decode().strip().lower() == "yes" for player_socket in players)
    
    if all_ready:
        for player_socket in players:
            player_socket.send("All players are ready. Starting the game...".encode())
        
        # Start the game
        start_game(players, player_names, player_equations, hands, target_choices, player_results)
    else:
        for player_socket in players:
            player_socket.send("Not all players are ready. Waiting for more players for 1 minute...".encode())
        
        time.sleep(60)

        # Check if there are still enough players connected to start the game
        if len(players) >= 2:
            start_game(players, player_names, player_equations, hands, target_choices, player_results)
        else:
            for player_socket in players:
                player_socket.send("Starting the game as there are not enough players...".encode())
            
            # Start the game with existing players
            start_game(players, player_names, player_equations, hands, target_choices, player_results)

def start_game(players, player_names, player_equations, hands, target_choices, player_results):
    # Game loop
    while len(players) >= 2:
        # Initialize deck and hands for each player
        deck = initialize_deck()
        initialize_hands(player_names, hands, deck)

        # Notify players of their hands
        for player_socket, player_name in zip(players, player_names):
            player_socket.send(f"Welcome to the Hi_Lo, {player_name}!\nYour hand: {' '.join(hands[player_name])}".encode())

        # Create threads for each player's turn
        threads = []
        for player_socket, player_name in zip(players, player_names):
            thread = threading.Thread(target=handle_player_turn, args=(player_socket, player_name, player_equations, hands, target_choices, player_results, deck))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Process player results and continue game logic
        process_results(players, player_names, player_equations, player_results)

def initialize_deck():
    # Initialize and shuffle the deck
    deck = ["0G", "1G", "2G", "3G", "4G", "5G", "6G", "7G", "8G", "9G", "10G", "S", "X",
            "0S", "1S", "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "S", "X",
            "0B", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B", "10B", "S", "X",
            "0D", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "S", "X"]
    random.shuffle(deck)
    return deck

def initialize_hands(player_names, hands, deck):
    # Deal initial hands to players
    for player_name in player_names:
        hands[player_name] = deck[:4]
        deck = deck[4:]

def handle_player_turn(player_socket, player_name, player_equations, hands, target_choices, player_results, deck):
    # Function to handle each player's turn
    hands[player_name], deck = xcounter(hands[player_name], deck, player_socket)
    hands[player_name], deck = scounter(hands[player_name], deck, player_socket)

    player_ready = False
    timeout_duration = 120
    start_time = time.time()

    while time.time() - start_time < timeout_duration:
        player_socket.send("Make your equation: ".encode())
        equation = player_socket.recv(1024).decode().strip().upper()
        player_equations[player_name] = equation
        result = player_eq(equation, hands[player_name])
        diff = hi_lo(result)
        player_socket.send(f"Result: {result}, Difference from target: {diff}".encode())

        player_socket.send("Are you ready? (yes/no): ".encode())
        ready_response = player_socket.recv().decode().strip().lower()
        if ready_response == "yes":
            player_ready = True
            break
        result = player_eq(equation, hands[player_name])
        diff = hi_lo(result)
        player_socket.send(f"Result: {result}, Difference from target: {diff}".encode())

    if not player_ready:
        player_socket.send("Time's up!")

    # Add the player result to the dictionary
    player_results[player_name] = result

def process_results(players, player_names, player_equations, player_results):
    # Process player results and continue game logic
    for player_socket, player_name in zip(players, player_names):
        equation = player_equations.get(player_name, "")
        if equation:
            result = player_results.get(player_name, None)
            if result is not None:
                diff = hi_lo(result)
                player_socket.send(f"Your final result: {result}, Difference from target: {diff}".encode())
            else:
                player_socket.send("Error occurred while calculating result.".encode())
        else:
            player_socket.send("No submissions have been made. You lost this round.".encode())

    # Handle continue game logic here...

def xcounter(player_hand, deck, player_socket):
    # Function to handle the X cards in the player's hand
    x_count = player_hand.count("X")
    removing = ["+", "-", "X"]

    while x_count > 0:
        player_socket.send("What to discard (+, - or X)?: ".encode())
        discarded = player_socket.recv(1024).decode().strip().upper()

        while discarded not in removing or len(discarded) != 1:
            player_socket.send("Remove +, - or X: ".encode())
            discarded = player_socket.recv(1024).decode().strip().upper()

        while deck[0] == "X" or deck[0] == "S":
            deck = deck[1:]

        player_hand.remove(discarded)
        player_hand.append(deck.pop(0))
        x_count -= 1
        player_socket.send(f"{discarded} removed, new card added to hand. Your current hand: {player_hand}".encode())

    return player_hand, deck

def scounter(player_hand, deck, player_socket):
    # Function to handle the S cards in the player's hand
    s_count = player_hand.count("S")
    while s_count > 0:
        if "S" in player_hand:
            while deck[0] == "X" or deck[0] == "S":
                deck = deck[1:]
            player_hand.append(deck.pop(0))
            s_count -= 1
            player_socket.send(f"S in hand, new card added. Your current hand: {player_hand}".encode())
    return player_hand, deck

def player_eq(player_input, hand):
    cards = player_input.upper().split(" ")
    operations = []
    result = 0
    hand_copy = hand.copy()

    while len(cards) > 0:
        if cards[0] not in hand:
            print("Make an equation from your hand: ")
            print(hand)
            return player_eq(input(""), hand)
        if len(cards[0]) > 2:
            hand_copy.remove(cards[0])
            cards.pop(0)
            operations.append(10)
        elif len(cards[0]) == 2:
            hand_copy.remove(cards[0])
            operations.append(int(cards.pop(0)[0]))
        elif cards[0] == "S":
            hand_copy.remove(cards[0])
            cards.pop(0)
            if len(cards[0]) > 2:
                operations.append(math.sqrt(10))
            else:
                operations.append(math.sqrt(int(cards[0][0])))
            hand_copy.remove(cards[0])
            cards.pop(0)
        else:
            hand_copy.remove(cards[0])
            operations.append(cards.pop(0))
    if len(hand_copy) != 0:
        print("Make an equation with your entire hand: ")
        print(hand)
        return player_eq(input(""), hand)
    result = operations.pop(0)
    for i in range(len(operations)):
        if operations[i] == "-":
            i += 1
            result -= operations[i]
        elif operations[i] == "+":
            i += 1
            result += operations[i]
        elif operations[i] == "X":
            i += 1
            result *= operations[i]
        elif operations[i] == "/":
            i += 1
            if operations[i] == 0:
                print("Can't divide by zero!")
                return player_eq(input("Make a new equation: "), hand)
            result /= operations[i]
    
    print(f"{result:.4f}")
    return result

def hi_lo(number):
    target = input("Do you want to make High(20) or Low(1) equation?: ").lower()
    while target != "high" and target != "low":
        target = input("Type High or Low: ")
    if target == "high":
        diff = 20 - number
    else:
        diff = 1 - number
    return abs(diff)

if __name__ == '__main__':
    main()