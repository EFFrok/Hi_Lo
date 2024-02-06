import socket
import random
import math

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5555))
    server_socket.listen(4)  # Listen for maximum of 2 players

    print("Waiting for players to connect...")

    players = []
    player_names = []

    while len(players) < 4:
        client_socket, client_address = server_socket.accept()
        players.append(client_socket)
        player_name = client_socket.recv(1024).decode()
        player_names.append(player_name)
        print(f"{player_name} connected.")

    print("All players connected. Starting the game...")

    player_scores = {player_name: 0 for player_name in player_names}

    deck = ["0G", "1G", "2G", "3G", "4G", "5G", "6G", "7G", "8G", "9G", "10G", "S", "X",
            "0S", "1S", "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "S", "X",
            "0B", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B", "10B", "S", "X",
            "0D", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "S", "X"]

    random.shuffle(deck)

    start_hand = ["/", "+", "-"]

    hands = {player_name: [] for player_name in player_names}
    for player_name in player_names:
        hands[player_name] = start_hand + deck[:4]
        deck = deck[4:]

    for player_socket, player_name in zip(players, player_names):
        player_socket.send(f"Welcome to the game, {player_name}!\nYour hand: {' '.join(hands[player_name])}".encode())

    while True:
        for player_socket, player_name in zip(players, player_names):
            player_socket.send("Make your equation: ".encode())
            equation = player_socket.recv(1024).decode().strip().upper()

            try:
                result = eval(equation)
            except Exception as e:
                player_socket.send(f"Invalid equation: {str(e)}".encode())
                continue

            if result.is_integer():
                result = int(result)

            if result == 20:
                player_socket.send("You hit the target!".encode())
            else:
                diff = abs(20 - result)
                player_socket.send(f"You were {diff} away from the target.".encode())

            player_scores[player_name] += diff

            if len(deck) < 5:
                player_socket.send("Game over!".encode())
                print("Game over!")
                print("Scores:")
                for name, score in player_scores.items():
                    print(f"{name}: {score}")
                server_socket.close()
                return

            new_game_prompt = player_socket.recv(1024).decode().strip().lower()
            if new_game_prompt == 'no':
                player_socket.send("Thanks for playing!".encode())
                server_socket.close()
                return

if __name__ == "__main__":
    main()