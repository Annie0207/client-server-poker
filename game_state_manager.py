'''
The `game_manager` module contains the class GameStateManager that implements the
poker API for a poker game manager created for this project. The API can be
viewed in Google Docs here:
https://docs.google.com/document/d/1p03ydY3g0QY7WARs0TSkFAcQ-Ut0rUP-xKc40t47tTs/edit?usp=sharing
'''

import cards


class GameStateManager:
    '''
    Implements the server side API of a multi-player poker game. 
    This class deals with variables, so TCP API parsing is required
    before using these methods.
    '''

    def __init__(self, num_players, wallet_amt, ante_amt):
        '''
        Creates the GameManager.

        num_players: int - Number of players in the game. Min: 2, Max: 5
        wallet_amt: int - Initial amount of money in each player's wallet. 
                          Basically, the buy in amount. Min: 5
        ante_amt: int - The amount each player needs to ante per round.
        '''
        # Simple constants
        # Player info
        self.p_addr_key = 'addr'
        self.p_name_key = 'name'
        self.p_conn_key = 'conn'

        # Game specific set up
        self.start(num_players, wallet_amt, ante_amt)

    def start(self, num_players, wallet_amt, ante_amt):
        '''
        Instructs the server to set up a game of poker with the given number of
        players and to give each player the specified amount of money to start.
        This is the only command available in the server at start-up. Once 
        called, the server moves into a state of waiting for the remaining 
        players to join.

        num_players: int - Number of players in the game. Min: 2, Max: 5
        wallet_amt: int - Initial amount of money in each player's wallet. 
                          Basically, the buy in amount. Min: 5
        ante_amt: int - The amount each player needs to ante per round.
        '''
        self.num_players = num_players
        self.wallet_amt = wallet_amt
        self.ante_amt = ante_amt
        self.deck = cards.Deck()
        self.players = dict()
        self.final_hands = dict()
        self.next_id = 1  # incremented when players join
        self.bets = BetInfo()
        self.turn_id = 1  # ID of the player who's turn it is
        self.folded_ids = set()  # IDs of players who have folded during betting
        self.left_ids = set()

    def join(self, connection, address_tup, player_name=''):
        '''
        Adds a player to the game and returns their generated ID. Can optionally 
        provide the player's name here as a convenience, in addition to the 
        set_name function. Raises a GameFullError if the game already has the
        set number of players.

        address_tup: (IP, PORT) - The address tuple provided by a client message
                                  to the server.
        player_name: str - Optional, empty string by default. The player's 
                           chosen name.
        '''
        # NOTE: This function signature is slightly different than the actual
        # server API for join. The server can extract the address tuple from
        # the client message, but it has to be passed in here.

        if self.next_id > self.num_players:
            raise GameFullError(
                'designated number of players reached, game full')

        # Get ID and increment
        p_id = self.next_id
        self.next_id += 1

        # Create a player as a dict
        player = {
            self.p_addr_key: address_tup,
            self.p_name_key: player_name,
            self.p_conn_key: connection
        }

        # Add to the players group
        self.players[p_id] = player

        return p_id

    def notify_all(self, message):
        '''
        Sends the given message to all players in the game. Keywords need to 
        be included by the caller if they are needed.

        message: str - A message to send to every player.
        '''
        for p_id in self.players:
            conn = self.players[p_id][self.p_conn_key]
            conn.send(message.encode())

    def notify_one(self, player_id, message):
        '''
        Sends the given player the message. Keywords need to be included by 
        the caller if they are needed.

        player_id: int - The ID of the player.
        message: str - A message to send to the player.
        '''
        conn = self.players[player_id][self.p_conn_key]
        conn.send(message.encode())

    def get_curr_num_players(self):
        '''
        Returns the number of players in the game currently.
        '''
        return len(self.players)

    def get_player_conn(self, player_id):
        '''
        Gets the connection object for a specific player.

        player_id: int - The ID of the player.
        '''
        return self.players[player_id][self.p_conn_key]

    def set_name(self, player_id, name):
        '''
        Sets the name of the player with the given ID.

        player_id: int - The ID of the player.
        name: string - The player’s name.
        '''
        # Ensure this player is in the game
        if player_id not in self.players:
            raise KeyError('player id not found')

        # Set the name
        self.players[player_id][self.p_name_key] = name

    def bet_info(self, player_id):
        '''
        Returns the amount of money currently in the pool, how much the call 
        amount is, and how much this player has bet so far. Value returned is
        a tuple of the form:
        (pool_amt, max_bet, current_bet)

        player_id: int - The ID of the player.
        '''
        pool_amt = self.bets.get_pool_amt()
        max_bet = self.bets.get_max_bet()[0]  # Don't need the player list
        curr_bet = self.bets.get_player_bet(player_id)

        return (pool_amt, max_bet, curr_bet)

    def increment_turn(self):
        '''
        Moves turn to the next player. Goes by the order players joined the game.
        Ignores any players who have folded or left the game.
        '''
        num_folded = len(self.folded_ids)
        num_left = len(self.left_ids)
        num_out = num_folded + num_left
        if self.num_players - num_out < 2:
            # Turn would never change
            return

        # For readability
        turn = self.turn_id

        # Increment until valid turn found
        turn = (turn + 1) % self.num_players
        while (turn in self.folded_ids) or (turn in self.left_ids):
            turn = (turn + 1) % self.num_players
        
        # Set new turn
        self.turn_id = turn

    def leave(self, player_id):
        '''
        Removes the given player from the game, if the player exists.  
        Returns the player value. Raises a KeyError if the player is not found.

        player_id: int - The ID of the player.
        '''
        player = self.players[player_id]
        del self.players[player_id]
        return player  # ID is already known, as it was passed in

    def bet_raise(self, player_id, amt):
        '''
        Indicates the given player wants to raise by the given amount. Player
        will have to check that they have the funds to raise before calling this.

        player_id: int - The ID of the player.
        amt: int - The amount to raise.
        '''
        # Need to make sure raise is on top of the max bet so far
        _, max_bet, curr_bet = self.bet_info(player_id)
        call_amt = max_bet - curr_bet
        total_bet = call_amt + amt

        # Now bet the total.
        self.bets.add_bet(player_id, total_bet)

    def bet_call(self, player_id):
        '''
        Indicates the given player wants to call during a round of betting. 
        Player will have to check that they have the funds to raise before 
        calling this.

        player_id: int - The ID of the player.
        '''
        _, max_bet, curr_bet = self.bet_info(player_id)
        call_amt = max_bet - curr_bet
        self.bets.add_bet(player_id, call_amt)

    def bet_check(self, player_id):
        '''
        Indicates that the given player has checked during a round of betting. 
        Only allowed by the person to start any given round of betting.

        player_id: int - The ID of the player.
        '''
        check_amt = self.bets.get_player_bet(player_id)
        self.bets.add_bet(player_id, check_amt)

    def bet_fold(self, player_id):
        '''
        Indicates that the given player has folded during a round of betting.

        player_id: int - The ID of the player.
        '''
        pass

    def is_betting_over(self):
        '''
        Determines if a round of betting has ended or not. A round of betting is
        over if all players besides those who have folded have bet the same 
        amount, or if all players except one have folded. If the latter, the 
        one player left has won the hand. If the former, all players must have 
        had at least one chance to bet for a round to be over.
        Returns a boolean tuple indicating if betting is over and if the hand
        has been won: (betting_over, hand_won)
        '''
        # The above description is just a suggestion
        cur_plays_num = len(self.players)
        if cur_plays_num - len(self.folded_ids) < 1:
            raise GameFullError(
                "There is no one in the game.")

        if cur_plays_num - len(self.folded_ids) == 1:
            return (True, True)

        cur_bets = -1
        for p_id in self.players:
            if p_id in self.folded_ids:
                continue
            if cur_bets == -1:
                cur_bets = self.bets.get_player_bet(p_id)
            elif cur_bets != self.bets.get_player_bet(p_id):
                return (False, False)
        return (True, False)

    def get_cards(self, num_cards):
        '''
        Gets and removes the given number of cards from the game deck. Returns
        cards in a list.
        '''
        if not num_cards >= 0 and num_cards <= cards.NUM_CARDS_IN_HAND:
            raise ValueError(
                'invalid number of cards, must be within the range of cards in a hand')
        card_list = []
        for _ in range(num_cards):
            card_list.append(self.deck.deal_card())

        return card_list

    def store_hand(self, player_id, card_list):
        '''
        Takes the players hand and stores it to be evaluated.

        player_id: int - The ID of the player.
        cards: Card - The cards in the player's hand
        '''
        # Cards not in Hand because it will be easier for server to pass to the
        # class; not sent as a hand, but individual cards. Creates the hand here.
        num_cards = len(card_list)
        hand = cards.Hand(num_cards)
        for card in card_list:
            hand.add_card(card)

        self.final_hands[player_id] = hand

    def evaluate_hands(self):
        '''
        Evaluates player hands at the end of a round of betting and determines
        the winner.
        '''
        # NOTE: Needs to empty the evaluated hands after, add back to deck,
        # and shuffle for next round.
        pass

    def ack_ante(self, player_id):
        '''
        Indicates that the given player has decided to ante and adds the ante 
        amount to the betting pool.

        player_id: int - The ID of the player. 
        '''
        self.bets.add_bet(player_id, self.ante_amt)


class BetInfo:
    '''
    Keeps track of important data during a round of betting.
    '''

    def __init__(self):
        '''
        Creates a BetInfo object.
        '''
        self.player_bets = dict()
        self.amt_key = 'amt'

    def add_bet(self, player_id, amt):
        '''
        Adds the given amount to the given player's bet total for a round.
        '''
        # If player hasn't bet yet, need to add to the dict
        if player_id not in self.player_bets:
            self.player_bets[player_id] = amt
        else:
            self.player_bets[player_id] += amt

        print("Player {} total bet amount {}".format(player_id, self.player_bets[player_id]))

    def get_max_bet(self):
        '''
        Finds the players who have bet the most this round so far and returns
        the the bet amount with a list of player IDs who've bet that amount in a
        tuple. If no bets have been made a tuple of the form (0, []) is returned.
        '''
        p_ids = []
        max_bet = 0
        d = self.player_bets
        # a = self.amt_key

        # Need to find max bet, then add players to list
        for key in d:
            if d[key] > max_bet:
                max_bet = d[key]

        for key in d:
            if d[key] == max_bet:
                p_ids.append(key)

        return (max_bet, p_ids)

    def get_player_bet(self, player_id):
        '''
        Get the amount a specific player has bet during a round.

        player_id: int - The ID of a player in the game.
        '''
        if player_id not in self.player_bets:
            return 0

        return self.player_bets[player_id]

    def get_pool_amt(self):
        '''
        Returns the total amount in the betting pool.
        '''
        d = self.player_bets
        # a = self.amt_key

        total = 0
        for key in d:
            total += d[key]

        return total

    def reset(self):
        '''
        Resets all betting info.
        '''
        self.player_bets = dict()


class GameFullError(Exception):
    '''
    Raised when a player tries to join a game that has reached its designated
    number of players.
    '''
    pass
