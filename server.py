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

    while True:
        client_socket, client_address = server_socket.accept()
        players.append(client_socket)
        player_name = client_socket.recv(1024).decode()
        player_names.append(player_name)
        print(f"{player_name} connected.")

        num_players_connected = len(players)

        if num_players_connected == 1:
            for player_socket in players:
                player_socket.send("Players connected: 1. Waiting for other players...".encode())
        elif num_players_connected == 2:
            for player_socket in players:
                player_socket.send("Players connected: 2. Would you like to start the game with 2 players? (yes/no)".encode())
            # Wait for responses
            all_ready = all(player_socket.recv(1024).decode().strip().lower() == "yes" for player_socket in players)
            if not all_ready:
                for player_socket in players:
                    player_socket.send("Not all players are ready. Waiting for more players for 1 minute...".encode())
                time.sleep(15)
                if len(players) == 2:
                    break
            else:
                break
        elif num_players_connected == 3:
            for player_socket in players:
                player_socket.send("Players connected: 3. Would you like to start the game with 3 players? (yes/no)".encode())
            # Wait for responses
            all_ready = all(player_socket.recv(1024).decode().strip().lower() == "yes" for player_socket in players)
            if not all_ready:
                for player_socket in players:
                    player_socket.send("Not all players are ready. Waiting for more players for 1 minute...".encode())
                time.sleep(15)
                if len(players) == 3:
                    break
            else:
                break
        elif num_players_connected == 4:
            for player_socket in players:
                player_socket.send("All players connected. Starting a game.".encode())
            break

    return players, player_names

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
            player_socket.send(f"Welcome to the Hi_Lo, {player_name}!\nYour hand: {' '.join(hands[player_name])}".encode())

        player_equations = {}
        target_choices = {}
        diff_to_target = {}
        player_results = {}

        for player_socket, player_name in zip(players, player_names):
            hands[player_name], deck = xcounter(hands[player_name], deck, player_socket)
            hands[player_name], deck = scounter(hands[player_name], deck, player_socket)

        # player_ready = False
        # timeout_duration = 120
        # start_time = time.time()

        for player_socket in players:
            player_socket.send("Make your equation: ".encode())
        for player_socket, player_name in zip(players, player_names):
            packet = player_socket.recv(1024).decode().split(" ")
            player_results[player_name] = float(packet[0])
            target_choices[player_name] = packet[1]
            diff_to_target[player_name] = float(packet[2])
        # for player_socket, player_name in zip(players, player_names):
        #     result = player_eq(equation, hands[player_name], player_socket)
        #     target, diff = hi_lo(result, player_socket)
        #     player_socket.send(f"Result: {result:.4f}, Difference from target: {diff:.4f}".encode())
        for player_socket in players:
            player_socket.send("Are you ready? (yes/no): ".encode())
        ready = all(player_socket.recv(1024).decode().strip().lower() == "yes" for player_socket in players)
        if ready:
            for player_socket, player_name in zip(players, player_names):
                result = player_results[player_name]
                diff = diff_to_target[player_name]
                player_socket.send(f"Result: {result:.4f}, Difference from target: {diff:.4f}".encode())

        # if not player_ready:
        #     player_socket.send("Time's up!")

        for player_socket, player_name in zip(players, player_names):
            equation = player_equations.get(player_name)
            if equation:
                # result = player_eq(equation, hands[player_name], player_socket)
                # target, diff = hi_lo(result, player_socket)
                player_socket.send(f"Your final result: {result:.4f}, Difference from target: {diff:.4f}".encode())
            else:
                player_socket.send("No submissions have been made. You lost this round.".encode())
        
        # diff_to_target = {player: abs(result - target_choices[player]) for player, result in player_results.items()}

        high_winner = min(((player, diff) for player, diff in diff_to_target.items() if target_choices[player] == 'high'), key=lambda x: x[1], default=None)
        low_winner = min(((player, diff) for player, diff in diff_to_target.items() if target_choices[player] == 'low'), key=lambda x: x[1], default=None)

        
        if high_winner:
            for player_socket in players:
                player_socket.send((f"High winner is: {high_winner[0]} with a difference of {high_winner[1]:.4f} to the target").encode())
        else:
            print("No high equations were made.")
            for player_socket in players:
                player_socket.send("No high equations were made.".encode())
        if low_winner:
            for player_socket in players:
                player_socket.send(f"Low winner is: {low_winner[0]} with a difference of {low_winner[1]:.4f} to the target".encode())
        else:
            print("No low equations were made.")
            for player_socket in players:
                player_socket.send("No low equations were made.".encode())
        print("Continue game?")
        for player_socket in players:
            player_socket.send("Do you want to continue the game? (yes/no): ".encode())
        for player_socket, player_name in zip(players, player_names):
            continue_response = player_socket.recv(1024).decode().strip().lower()
            if continue_response != "yes":
                print(player_name, "left the game.")
                players.remove(player_socket)
                player_names.remove(player_name)
            else:
                print(player_name, "playing")

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
        discarded = player_socket.recv(1024).decode()
        while deck[0] == "X" or deck[0] == "S":
            deck = deck[1:]
        player_hand.remove(discarded)
        player_hand.append(deck.pop(0))
        x_count -= 1
        player_socket.send(f"{discarded} removed, new card added to hand. Your current hand: {' '.join(player_hand)}".encode())

    return player_hand, deck

def scounter(player_hand, deck, player_socket):
    s_count = player_hand.count("S")
    while s_count > 0:
        if "S" in player_hand:
            while deck[0] == "X" or deck[0] == "S":
                deck = deck[1:]
            player_hand.append(deck.pop(0))
            s_count -= 1
            player_socket.send(f"S in hand, new card added. Your current hand: {' '.join(player_hand)}".encode())
    return player_hand, deck

def player_eq(player_input, hand, player_socket):
    cards = player_input.upper().split(" ")
    operations = []
    result = 0
    hand_copy = hand.copy()

    while len(cards) > 0:
        if cards[0] not in hand:
            player_socket.send(f"Make an equation from your hand: {' '.join(hand)}".encode())
            print("card not in hand used")
            print(player_input)
            eq = player_socket.recv(1024).decode().strip().upper()
            print(eq)
            return player_eq(eq, hand, player_socket)
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
        else:
            hand_copy.remove(cards[0])
            operations.append(cards.pop(0))
    if len(hand_copy) != 0:
        player_socket.send(f"Make an equation from your hand: {' '.join(hand)}".encode())
        print("not all cards used")
        eq = player_socket.recv(1024).decode().strip().upper()
        print(eq)
        return player_eq(eq, hand, player_socket)
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
                player_socket.send(f"Can't divide by zero!\n Make a new equation: ".encode())
                return player_eq(player_socket.recv(1024).decode().strip().upper(), hand, player_socket)
            result /= operations[i]
    
    player_socket.send(f"{result:.4f}".encode())
    return result

def hi_lo(number, player_socket):
    player_socket.send("Do you want to make High(20) or Low(1) equation?: ".encode())
    target = player_socket.recv(1024).decode().strip()
    if target == "high":
        diff = 20 - number
    else:
        diff = 1 - number
    return target, abs(diff)

if __name__ == '__main__':
    main()