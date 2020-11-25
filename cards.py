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
        return self.deck.pop()

    def add_card_to_bottom(self, card):
        '''
        Adds the given card to the bottom of the deck. The card can not be
        a duplicate of a card already in the deck.

        card: Card - A Card object
        '''
        if not isinstance(card, Card):
            raise ValueError('card must be of type `Card`')
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
