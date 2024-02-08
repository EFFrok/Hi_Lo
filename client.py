import socket

def main():
    client_socket = toTheServer()
    theGame(client_socket)
    client_socket.close()

def toTheServer():
    server_address = ('127.0.0.1', 5555)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    return client_socket

def theGame(client_socket):

    initial_hand = client_socket.recv(1024).decode()
    print("Initial hand:", initial_hand)
    while True:
        try:
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
            break
        except Exception as e:
            print("An error occurred:", e)
            break

if __name__ == "__main__":
        main()