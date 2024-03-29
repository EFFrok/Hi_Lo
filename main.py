import random
import math

def main():

    player_hand = ["+", "-", "/"]
    deck = ["0G", "1G", "2G", "3G", "4G", "5G", "6G", "7G", "8G", "9G", "10G", "S", "X",
            "0S", "1S", "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "S", "X",
            "0B", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B", "10B", "S", "X",
            "0D", "1D", "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "S", "X"]

    print("Let's play Hi-Lo!")
    print("Here are your cards: ")
    player_hand, deck = hand(player_hand, deck)
    player_hand, deck = xcounter(player_hand, deck)
    player_hand, deck = scounter(player_hand, deck)
    eq = input("Now make your equation: ")
    number = player_eq(eq, player_hand)
    newEq = "yes"
    while newEq == "yes":
        newEq = input("Do you want to make a different equation?: ").lower()
        while newEq != "yes" and newEq != "no":
            newEq = input("Yes or no?: ")
        if newEq == "yes":
            new = input("Make a new equation: ")
            number = player_eq(new, player_hand)
    diff = hi_lo(number)
    if diff != 0:
        print("You were ", diff, " away from the target.")
    else:
        print("You hitted the target!")
    answer = input("New game? Type yes or no: ").lower()
    while answer != "yes" and answer != "no":
        answer = input("Type yes or no: ")
    if answer == "yes":
        main()
    else:
        return print("Thanks for playing!")



def hand(player_hand, deck):

    random.shuffle(deck)
    player_hand.extend(deck[:4])
    deck = deck[4:]
    print(player_hand)
    return player_hand, deck


def xcounter(player_hand, deck):
    x_count = player_hand.count("X")
    removing = ["+", "-", "X"]

    while x_count > 0:
        discarded = input("What to discard (+, - or X)?: ").upper()
        while discarded not in removing or len(discarded) != 1:
            discarded = input("Remove +, - or X: ").upper()
        while deck[0] == "X" or deck[0] == "S":
            deck = deck[1:]
        player_hand.remove(discarded)
        player_hand.append(deck.pop(0))
        x_count -= 1
        print(discarded, "removed, new card added to hand. Your current hand: ")
        print(player_hand)
    return player_hand, deck


def scounter(player_hand, deck):
    s_count = player_hand.count("S")
    while s_count > 0:
        if "S" in player_hand:
            while deck[0] == "X" or deck[0] == "S":
                deck = deck[1:]
            player_hand.append(deck.pop(0))
            s_count -= 1
            print("S in hand, new card added. Your current hand: ")
            print(player_hand)
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