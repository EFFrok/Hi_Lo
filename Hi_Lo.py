import random

def main ():

        player_hand = ["+", "-", "/"]
        deck = ["0P", "1P", "2P", "3P", "4P", "5P", "6P", "7P", "8P", "9P", "10P", "NJ", "X",
                "0X", "1X", "2X", "3X", "4X", "5X", "6X", "7X", "8X", "9X", "10X", "NJ", "X",
                "0R", "1R", "2R", "3R", "4R", "5R", "6R", "7R", "8R", "9R", "10R", "NJ", "X",
                "0H", "1H", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "NJ", "X"]

        print("Let's play Hi-Lo!")
        print("Here are your cards: ")
        hand(player_hand, deck)
        xcounter(player_hand, deck)
        njcounter(player_hand, deck)
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
                if "X" in player_hand:
                        discarded = input("What to discard (+, - or X)?: ").upper()
                        while discarded not in removing or len(discarded) != 1:
                                discarded = input("Remove +, - or X: ").upper()
                        while deck[0] == "X" or deck[0] == "NJ":
                                deck = deck[1:]
                player_hand.remove(discarded)
                player_hand.append(deck.pop())
                x_count -= 1
                print(discarded, "removed, new card added to hand. Your current hand: ")
                print(player_hand)
        return player_hand, deck

def njcounter(player_hand, deck):
        nj_count = player_hand.count("NJ")
        while nj_count > 0:
                if "NJ" in player_hand:
                        while deck[0] == "X" or deck[0] == "NJ":
                                deck = deck[1:]
                        player_hand.append(deck.pop())
                        nj_count -= 1
                        print("NJ in hand, new card added. Your current hand: ")
                        print(player_hand)
        return player_hand, deck

