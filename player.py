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

# At this point, only 5 Card Draw is available
NUM_CARDS_IN_HAND = 5


class Player:
    '''
    Provides a poker player API implementation in the form of a class.
    This class deals with python variables, so TCP API parsing is required
    before using these methods.
    '''
    # NOTE: display_hand not implemented here because that prints other players'
    # hands to this player's terminal. That is better handled by the client code
    # when it recieves the display_hand TCP message.

    def __init__(self, wallet_amt):
        '''
        Creates a new Player class.
        '''
        self.wallet = wallet_amt
        self.hand = Hand(NUM_CARDS_IN_HAND)

    def get_action(self):
        '''
        Provides the player with options of what to do doing their turn. Only
        called when the server notifies the client it is this player's turn.
        '''
        # TODO: Implement
        pass

    def print_menu(self):
        '''
        Prints a menu of commands that a player can take on their turn.
        '''
        # TODO: Implement
        pass

    def notify(self, message):
        '''
        Prints the given message to the player's terminal.

        message: str - a message to print
        '''
        # This method is not really needed, but here for completeness.
        # The client process could simply print the messages it recieves to the
        # terminal.
        print(message)

    def ante(self, amt):
        '''
        Removes the ante amount from this players wallet. Returns True if the
        debit was successful, returns False if the player does not have 
        enough in their wallet to ante.

        amt: int - the amount needed to ante
        '''
        self._debit_wallet(amt)

    def ack_call(self, amt):
        '''
        An acknowledgement of this player's decision to call during a betting
        round. The acknowledgement provides the player with the amount they
        need to bet in order to meet the call amount. This amount is subtracted
        from the player's wallet. Returns True if the amount is successfully
        subtracted, returns False if there is not enough in the player's wallet
        to handle the transaction.

        amt: int - the amount the player needs to bet
        '''
        self._debit_wallet(amt)

    def _debit_wallet(self, amt):
        '''
        Removes money from the player's wallet if able to do so.

        amt: int - the amount to remove
        '''
        if amt < 0:
            raise ValueError("ante amount cannot be negative")

        # Check the amount is not more than the player has
        if amt <= self.wallet:
            self.wallet -= amt
            return True

        # Notify that the player does not have enough in their wallet
        return False

    def add_cards(self, card_list):
        '''
        Adds each of the cards in the list to this players hand. There must be
        at least one card and no more than the max a hand can have. If there
        are more cards in the list than the hand can hold (i.e. 3 cards in the
        hand, 3 in the list), a HandFullError is thrown.

        card_list: [Card] - a list of cards to add to the hand
        '''
        l = len(card_list)
        if l < 1:
            raise ValueError('must have at least one card in the list')
        if l > NUM_CARDS_IN_HAND:
            raise ValueError('cannot have more cards than allowed in a hand')

        # Add the cards
        for card in card_list:
            self.hand.add_card(card)

    def win_pool(self, amt):
        '''
        Adds betting pool winnings to this players wallet. Should only be called when
        the player wins a round. This would be highly insecure in real life!

        amt: int - the amount this player has won
        '''
        if amt < 0:
            raise ValueError('amount cannot be negative')

        self.wallet += amt

    def ack_player_joined(self, player_name):
        '''
        Notifies this player that another player has joined the game.

        player_name: str - the name of the player who left the game
        '''
        print("Player", player_name, "has joined the game.")

    def ack_player_left(self, player_name):
        '''
        Notifies this player that another player has left the game.

        player_name: str - the name of the player who left the game
        '''
        print("Player", player_name, "has left the game.")


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
