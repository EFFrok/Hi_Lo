import random

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
    print("Now make your equation.")


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


if __name__ == '__main__':
    main()

def calculator(player_hand):
    for card in player_hand:
        for i in card:
            if i >= 0 & i <= 10:
                 card = i