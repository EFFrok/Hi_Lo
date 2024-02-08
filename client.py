import socket
import math

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
    hand = []
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
            elif "hand: " in message:
                hand = [x.strip() for x in message.split("hand: ")[1].split(" ")]
            elif "discard" in message:
                discard = input("").strip().upper()
                while discard not in ["+", "-", "X"]:
                    discard = input("Remove +, - or X: ").strip().upper()
                client_socket.send(discard.encode())
            elif "Make" in message:
                equation = input("")
                result = player_eq(equation, hand)
                target, diff = hi_lo(result)
                package = ' '.join(["{:.4f}".format(result), target, "{:.4f}".format(diff)])
                client_socket.send(package.encode())
            # elif "High(20) or Low(1)" in message:
            #     target = input("").strip().lower()
            #     while target != "high" and target != "low":
            #         target = input("Type High or Low: ").strip().lower()
            #     client_socket.send(target.encode())
            elif "(yes/no):" in message:
                response = input("").strip().lower()
                while response != "yes" and response != "no":
                    response = input(message)
                client_socket.send(response.encode())
            # elif "Do you want to continue the game?" in message:
            #     response = input("")
            #     client_socket.send(response.encode())
            elif "Game over." in message:
                break
            else:
                continue
    except ConnectionResetError:
        print("Connection reset by server.")
    except Exception as e:
        print("An error occurred:", e)

def player_eq(player_input, hand):
    cards = player_input.upper().split(" ")
    operations = []
    result = 0
    hand_copy = hand.copy()

    while len(cards) > 0:
        if cards[0] not in hand:
            print("Make an equation from your hand: ")
            print(f"{' '.join(hand)}")
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
    target = input("Do you want to make High(20) or Low(1) equation?: ").strip().lower()
    while target != "high" and target != "low":
        target = input("Type High or Low: ")
    if target == "high":
        diff = 20 - number
    else:
        diff = 1 - number
    return target, abs(diff)

if __name__ == "__main__":
        main()