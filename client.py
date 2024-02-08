import socket

def main():
    player_name = input("Enter your player name: ")
    client_socket = toTheServer(player_name)
    theGame(client_socket)
    client_socket.close()

def toTheServer(player_name):
    server_address = ('127.0.0.1', 5555)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    client_socket.send(player_name.encode())
    return client_socket

def theGame(client_socket):

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Connection closed by server.")
                break
            print(message)
            if "Would you like to start" in message:
                response = input("")
                client_socket.send(response.encode())
            if "discard" in message:
                discard = input("").strip().upper()
                while discard not in ["+", "-", "X"]:
                    discard = input("Remove +, - or X: ").strip().upper()
                client_socket.send(discard.encode())
            elif "equation" in message:
                equation = input("")
                client_socket.send(equation.encode())
            elif "High(20) or Low(1)" in message:
                target = input("").strip().lower()
                while target != "high" and target != "low":
                    target = input("Type High or Low: ").strip().lower()
                client_socket.send(target.encode())
            elif "(yes/no):" in message:
                response = input("").strip().lower()
                while response != "yes" and response != "no":
                    response = input(message)
                client_socket.send(response.encode())
            elif "Do you want to continue the game?" in message:
                response = input("")
                client_socket.send(response.encode())
            elif "Game over." in message:
                break
            else:
                continue
    except ConnectionResetError:
        print("Connection reset by server.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
        main()