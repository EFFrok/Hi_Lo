import random
import math
import socket
import time

def main():

    players, player_names = connections()
    game_logic(players, player_names)

def connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5555))
    server_socket.listen(4) 

    print("Waiting for players to connect...")

    players = []
    player_names = []

    while len(players) < 4:
        client_socket, client_address = server_socket.accept()
        players.append(client_socket)
        player_name = client_socket.recv(1024).decode()
        player_names.append(player_name)
        print(f"{player_name} connected.")

    print("All players connected. Ready to start the game?")

    timeout_duration = 60
    start_time = time.time()
    while time.time() - start_time < timeout_duration:
        all_ready = True
        for player_socket in players:
            player_socket.send("Are you ready to start the game? (yes/no): ".encode())
            response = player_socket.recv(1024).decode().strip().lower()

            if response != "yes":
                all_ready = False
                print("Player is not ready. Waiting for other players...")
        
        if all_ready:
            print("All players are ready. Starting the game...")
            break
    if not all_ready:
        print("Time's out. Starting the game...")

def game_logic(players, player_names):

    while len(players) >= 2:

        deck = ["0G", "1G", "2G", "3G", "4G", "5G", "6G", "7G", "8G", "9G", "10G", "S", "X",
                "0S", "1S", "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "S", "X",
                "0B", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B", "10B", "S", "X",
                "0D", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "S", "X"]

        hands = {player_name: [] for player_name in player_names}
        for player_name in player_names:
            hands[player_name], deck = hand(hands[player_name], deck)
        
        for player_socket, player_name in zip(players, player_names):
            player_socket.send(f"Welcome to the game, {player_name}!\nYour hand: {' '.join(hands[player_name])}".encode())

        player_equations = {}
        target_choices = {}
        player_results = {}

        while True:
            for player_socket, player_name in zip(players, player_names):
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
                    ready_response = player_socket.recv(1024).decode().strip().lower()
                    if ready_response == "yes":
                        player_ready = True
                        break
                    result = player_eq(equation, hands[player_name])
                    diff = hi_lo(result)
                    player_socket.send(f"Result: {result}, Difference from target: {diff}".encode())

                if not player_ready:
                    player_socket.send("Time's up!")

            for player_socket, player_name in zip(players, player_names):
                equation = player_equations.get(player_name, "")
                if equation:
                    result = player_eq(equation, hands[player_name])
                    diff = hi_lo(result)
                    player_socket.send(f"Your final result: {result}, Difference from target: {diff}".encode())
                else:
                    player_socket.send("No submissions have been made. You lost this round.".encode())
            
            diff_to_target = {player: abs(result - target_choices[player]) for player, result in player_results.items()}

            high_winner = min(((player, diff) for player, diff in diff_to_target.items() if target_choices[player] == 'high'), key=lambda x: x[1], default=None)
            low_winner = min(((player, diff) for player, diff in diff_to_target.items() if target_choices[player] == 'low'), key=lambda x: x[1], default=None)

            if high_winner:
                print(f"High winner is: {high_winner[0]} with a difference of {high_winner[1]} to the target")
            else:
                print("No high equations were made.")

            if low_winner:
                print(f"Low winner is: {low_winner[0]} with a difference of {low_winner[1]} to the target")
            else:
                print("No low equations were made.")
            
            player_socket.send("Do you want to continue the game? (yes/no): ".encode())
            continue_response = player_socket.recv(1024).decode().strip().lower()
            if continue_response != "yes":
                players.remove(player_socket)
                player_names.remove(player_name)

            if len(players) < 2:
                for player_socket in players:
                    message = "Game over. Not enough players."
                    player_socket.send(message.encode())
                    player_socket.close()
                players.clear()
                player_names.clear()

def hand(player_hand, deck):
    start_hand = ["+", "-", "/"]
    random.shuffle(deck)
    player_hand.extend(start_hand + deck[:4])
    deck = deck[4:]
    return player_hand, deck

def xcounter(player_hand, deck, player_socket):
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