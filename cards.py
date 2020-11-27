'''
The `cards` module contains classes related to a deck of cards and how they are used.
It contains classes for a card (Card) and deck of cards (Deck). It does not
contain a class for a hand of cards because that is dependent on the game being 
played and managed by the player of a game.
'''

import random

# Char representations of suits
# Hearts, Diamonds, Clubs, Spades
SUITS = set(['H', 'D', 'C', 'S'])

# Char representations of rank including numbers and Jack, Queen, King, Ace
RANKS = set(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])

# At this point, only 5 Card Draw is available
NUM_CARDS_IN_HAND = 5

class Deck:
    '''
    Represents a standard 52 card deck of playing cards. It does not include
    Jokers, only the standard suits and ranks.
    '''

    def __init__(self):
        '''
        Creates the inital deck.
        '''
        self.deck = []
        self.create()
        self.shuffle()

    def create(self):
        '''
        Builds a 52 card deck from scratch.
        '''
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))

    def shuffle(self):
        '''
        Suffles the deck.
        '''
        random.shuffle(self.deck)

    def deal_card(self):
        '''
        Removes and returns a card from the top of the deck.
        '''
        if len(self.deck) <= 0:
            raise DeckEmptyError()

        return self.deck.pop()

    def add_card_to_bottom(self, card):
        '''
        Adds the given card to the bottom of the deck. The card can not be
        a duplicate of a card already in the deck.

        card: Card - A Card object
        '''
        if not isinstance(card, Card):
            raise TypeError('card must be of type `Card`')
        if card in self.deck:
            raise ValueError('cannot add duplicate card to the deck')

        self.deck.insert(0, card)

    def _print_deck(self):
        '''
        Prints each card of a deck. Should only be needed for debugging.
        '''
        for card in self.deck:
            print(card)


class Card:
    '''
    Represents a standard playing card with a suit and rank.
    '''

    def __init__(self, suit, rank):
        '''
        Creates a Card.

        suit: str - A char representing a suit ('H', 'D', 'C', 'S')
        rank: str - A char representing a rank
            ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
        '''
        if suit not in SUITS:
            raise ValueError('invalid suit')
        if rank not in RANKS:
            raise ValueError('invalid rank')

        self.suit = suit
        self.rank = rank

        # Assign UTF suit also
        if suit == 'H':
            self.utf_suit = '♥'    # U+2665
        elif suit == 'D':
            self.utf_suit = '♦'    # U+2666
        elif suit == 'C':
            self.utf_suit = '♣'    # U+2663
        else:
            # Must be spade, from check above
            self.utf_suit = '♠'    # U+2660

    def __str__(self):
        '''
        Prints the card so it looks like a playing card.
        '''
        edge = '+-----+'  # top and bottom, so no newline automatically
        middle = '|  ' + self.utf_suit + '  |\n'

        # Account for different length ranks ('2' vs '10')
        if self.rank == '10':
            rank_top =    '|10   |\n'
            rank_bottom = '|   10|\n'
        else:
            rank_top =    '|' + self.rank + '    |\n'
            rank_bottom = '|    ' + self.rank + '|\n'

        return edge + '\n' + rank_top + middle + rank_bottom + edge

    def __repr__(self):
        '''
        Simple representation of a card for TCP messaging.
        '''
        return self.suit + self.rank


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
        Adds a card to the hand. If the hand is full, raises a HandFullError. If
        the given card is not a Card object, raises a TypeError.

        card: Card - the card to add to the hand
        '''
        if not isinstance(card, Card):
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
        if not 0 < card_id <= len(self.hand):
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
        if not 0 < card_id_1 <= len(self.hand):
            raise ValueError('card_id_1 must be a valid index (1 to len)')
        if not 0 < card_id_2 <= len(self.hand):
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

class DeckEmptyError(Exception):
    '''
    Raised when an empty deck tries to deal a card.
    '''
    pass