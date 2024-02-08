import socket

def main():
    server_address = ('127.0.0.1', 5555)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    initial_hand = client_socket.recv(1024).decode()
    print("Initial hand:", initial_hand)

    client_socket.close()