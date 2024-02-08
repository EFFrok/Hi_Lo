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
            if "Are you ready to start the game?" in message:
                response = input("Are you ready to start the game? (yes/no): ")
                client_socket.send(response.encode())
            elif "Make your equation:" in message:
                equation = input("Make your equation: ")
                client_socket.send(equation.encode())
            elif "Are you ready? (yes/no):" in message:
                response = input("Are you ready? (yes/no): ")
                client_socket.send(response.encode())
            elif "Do you want to continue the game?" in message:
                response = input("Do you want to continue the game? (yes/no): ")
                client_socket.send(response.encode())
            elif "Game over." in message:
                break
    except ConnectionResetError:
        print("Connection reset by server.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
        main()