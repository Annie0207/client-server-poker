'''
The `player` module contains a class describing a player (Player) in a game 
of poker. It also contains a class for a hand of cards (Hand) that is used by
the player. The Player class implements the poker API created for this project.
The API can be viewed in Google Docs here: 
https://docs.google.com/document/d/1p03ydY3g0QY7WARs0TSkFAcQ-Ut0rUP-xKc40t47tTs/edit?usp=sharing
'''

import cards

# Char representations of suits
# Hearts, Diamonds, Clubs, Spades
SUITS = set(['H', 'D', 'C', 'S'])

# Char representations of rank including numbers and Jack, Queen, King, Ace
RANKS = set(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])

# Player

# Wallet

# Hand
class Hand:
    '''
    Hand represents a hand of cards that a poker player might have.
    '''

    def __init__(self, num_cards):
        '''
        Creates an empty hand.
        '''
        pass

    def add_card(self, card):
        '''
        Adds a card to the hand. If the hand is full, raises a HandFullError.

        
        '''
        pass

    def remove_card(self, card_id):
        '''
        Removes the card with the given index from the hand. The index is
        1-indexed for user friendliness. IDs are printed for the user next
        to each card when displayed.

        card_id: int - the 1-indexed position of the card to remove
        '''
        pass

    def swap_cards(self, card_id_1, card_id_2):
        '''
        Swaps two cards in a hand as one would do with a real hand of cards.
        
        card_id_1: int - the 1-indexed position of the first card to swap
        card_id_2: int - the 1-indexed position of the second card to swap
        '''

    def __str__(self):
        '''
        Displays each card in the hand along with its ID number.
        '''
        pass


class HandFullError(Exception):
    '''
    Raised when a hand is full.
    '''
    pass