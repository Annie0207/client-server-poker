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


class Player:
    '''
    Provides a poker player API implementation for the 
    '''
    pass


class Hand:
    '''
    Hand represents a hand of cards that a poker player might have.
    '''

    def __init__(self, num_cards):
        '''
        Creates an empty hand.

        num_cards: int - the number of cards a hand should contain
        '''
        self.max_len = num_cards
        self.hand = []

    def add_card(self, card):
        '''
        Adds a card to the hand. If the hand is full, raises a HandFullError.

        card: Card - the card to add to the hand
        '''
        if not isinstance(card, cards.Card):
            raise TypeError('card must be of type Card')
        if len(self.hand) >= self.max_len:
            raise HandFullError()

        self.hand.append(card)

    def remove_card(self, card_id):
        '''
        Removes the card with the given index from the hand. The index is
        1-indexed for user friendliness. IDs are printed for the user next
        to each card when displayed. The card is returned after removal.

        card_id: int - the 1-indexed position of the card to remove
        '''
        if not 0 < card_id <= self.max_len:
            raise ValueError('card_id must be a valid index (1 to len)')

        card = self.hand[card_id - 1]
        self.hand.remove(card)
        return card

    def swap_cards(self, card_id_1, card_id_2):
        '''
        Swaps two cards in a hand as one would do with a real hand of cards.

        card_id_1: int - the 1-indexed position of the first card to swap
        card_id_2: int - the 1-indexed position of the second card to swap
        '''
        if not 0 < card_id_1 <= self.max_len:
            raise ValueError('card_id_1 must be a valid index (1 to len)')
        if not 0 < card_id_2 <= self.max_len:
            raise ValueError('card_id_2 must be a valid index (1 to len)')

        i = card_id_1 - 1
        j = card_id_2 - 1
        self.hand[i], self.hand[j] = self.hand[j], self.hand[i]

    def print_hand(self):
        '''
        Displays each card in the hand along with its ID number.
        '''
        for i, card in enumerate(self.hand):
            print(i+1)
            print(card)

    def __repr__(self):
        '''
        Provides a simple representation of the hand.
        '''
        # Get the representation of each card in the hand
        hand_repr = map(lambda card: card.__repr__(), self.hand)

        # Return them as comma seperated values
        return "Hand(" + ', '.join(hand_repr) + ")"


class HandFullError(Exception):
    '''
    Raised when a hand is full.
    '''
    pass
