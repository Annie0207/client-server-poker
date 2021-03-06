'''
The `player` module contains a class describing a player (Player) in a game 
of poker. It also contains a class for a hand of cards (Hand) that is used by
the player. The Player class implements the poker API created for this project.
The API can be viewed in Google Docs here: 
https://docs.google.com/document/d/1p03ydY3g0QY7WARs0TSkFAcQ-Ut0rUP-xKc40t47tTs/edit?usp=sharing
'''

import cards


class Player:
    '''
    Provides a poker player API implementation in the form of a class.
    This class deals with variables, so TCP API parsing is required
    before using these methods.
    '''
    # NOTE: display_hand not implemented here because that prints other players'
    # hands to this player's terminal. That is better handled by the client code
    # when it receives the display_hand TCP message.

    def __init__(self, wallet_amt, player_id, player_name):
        '''
        Creates a new Player class.

        wallet_amt: int - the "buy in" amount that a player starts with
        player_id: int - the id for this player, provided by the server
        player_name: str - this player's name
        '''
        self.wallet = wallet_amt
        self.hand = cards.Hand(cards.NUM_CARDS_IN_HAND)
        self.name = player_name
        self.id = player_id
        self.prompt = '> '

    def get_action(self):
        '''
        Provides the player with options of what to do doing their turn. Only
        called when the server notifies the client it is this player's turn.
        Returns a string in the form of a TCP API call to the server.
        '''
        # Can add extra options to each command, but keep the first one
        # the same as it is because that is the TCP API command name.
        cards = ['cards', 'c']
        swap = ['swap', 's']
        bet_info = ['bet_info', 'b']
        check = ['check', 'ch']
        call = ['call', 'cl']
        rse = ['raise', 'r']  # raise is a reserved word
        fold = ['fold', 'f']
        leave = ['leave', 'l']
        menu = ['menu', 'm']
        cmds = set(cards + swap + bet_info + check +
                   call + rse + fold + leave + menu)

        # Convenience variable
        _id = ' ' + str(self.id)

        # Print menu and get response
        self.print_menu()
        while True:
            choice = input(self.prompt).strip()
            choice_lst = choice.split()
            len_args = len(choice_lst)
            cmd = choice_lst[0]

            # Check valid command
            if cmd not in cmds:
                print('invalid command, please try again')
                continue

            # Check commands one by one
            if cmd in cards:
                self.hand.print_hand()
                # This move for player only, still has a choice to make
                continue

            if cmd in swap:
                if len_args != 3:
                    print('invalid command: swap takes exactly two integer arguments')
                    continue

                # Ensure args are integers
                try:
                    id_1 = int(choice_lst[1])
                    id_2 = int(choice_lst[2])
                except ValueError:
                    print("invalid command: arguments are not integers")
                    continue

                # Perform swap
                # This move for player only, still has a choice to make
                self.hand.swap_cards(id_1, id_2)
                continue

            if cmd in bet_info:
                # IMPORTANT: If this option is chosen, the method needs to be
                # called again once the player receives the info. Without some
                # extra multi-threading, the prompt will block the info from
                # getting printed. So, for now this returns the API string,
                # BUT WE STILL NEED TO CALL THIS METHOD AGAIN IN THE CLIENT.
                return bet_info[0] + _id

            # TODO: Add a way to check that if this is called, it is only
            # allowed by the first player to bet in a round.
            if cmd in check:
                return check[0] + _id

            # TODO: Add methods to check that player has enough to bet and
            # subtracts funds from wallet. Might be best as a client process
            # method.
            if cmd in call:
                return call[0] + _id

            if cmd in rse:
                if len_args != 2:
                    print('invalid command: raise takes exactly 1 integer argument')
                    continue

                try:
                    int(choice_lst[1])
                except ValueError:
                    print("invalid command: argument is not an integer")
                    continue

                return rse[0] + _id + ' ' + choice_lst[1]

            if cmd in fold:
                return fold[0] + _id

            if cmd in leave:
                return leave[0] + _id

            if cmd in menu:
                self.print_menu()
                continue

    def print_menu(self):
        '''
        Prints a menu of commands that a player can take on their turn.
        '''
        intro = 'Enter a command at the prompt to choose an action:\n'
        see_cards = (
            'c, cards\n' +
            '\tview the cards in your hand\n'
        )
        swap = (
            's, swap <id_1> <id_2>\n' +
            '\tswap two cards in your hand\n'
        )
        see_betting = (
            'b, bet_info\n' +
            '\tview betting pool, highest bet so far, the amount \n' +
            '\tyou have bet so far, and the amount in your wallet\n'
        )
        check = (
            'ch, check\n' +
            '\tbetting: check (only allowed if you are first to bet)\n'
        )
        call = (
            'cl, call\n' +
            '\tbetting: call\n'
        )
        rse = (
            'r, raise <amt>\n' +
            '\tbetting: raise by <amt>\n'
        )
        fold = (
            'f, fold\n' +
            '\tbetting: fold\n'
        )
        leave = (
            'l, leave\n' +
            '\tleave the game, forfeit any bets made so far\n'
        )
        menu = (
            'm, menu\n' +
            '\tprint this menu\n'
        )
        menu = (
            intro +
            see_cards +
            swap +
            see_betting +
            check +
            call +
            rse +
            fold +
            leave +
            menu
        )

        # Printed without newline so it is easier to swap ordering if needed.
        # All above have newline.
        print(menu, end='')

    def ante(self, amt):
        '''
        Removes the ante amount from this players wallet. Returns True if the
        debit was successful, returns False if the player does not have 
        enough in their wallet to ante.

        amt: int - the amount needed to ante
        '''
        return self._debit_wallet(amt)

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
        return self._debit_wallet(amt)

    def _debit_wallet(self, amt):
        '''
        Removes money from the player's wallet if able to do so. True if 
        successful, False if there is not enough in the wallet.

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
        if l > cards.NUM_CARDS_IN_HAND:
            raise ValueError('cannot have more cards than allowed in a hand')

        # Add the cards
        for card in card_list:
            self.hand.add_card(card)

    def delete_cards(self, card_list):
        '''
        Delete each of the cards in the list to this players hand. There must be 
        at lease one card and no more than MAX_DISCARD cards. Otherwise, we will 
        throw a HandFullError
        '''
        l = len(card_list)

        if l < 1:
            raise ValueError('must discard at least one card in the list')
        if l > cards.MAX_DISCARD:
            raise ValueError('cannot dicard more cards than allowed in a hand')
        
        card_list.sort(reverse = True)
        for card in card_list:
            self.hand.remove_card(card)

    def win_pool(self, amt):
        '''
        Adds betting pool winnings to this players wallet. Should only be called when
        the player wins a round. This would be highly insecure in real life!

        amt: int - the amount this player has won
        '''
        if amt < 0:
            raise ValueError('amount cannot be negative')

        self.wallet += amt

    def notify(self, message):
        '''
        Prints the given message to the player's terminal.

        message: str - a message to print
        '''
        # This method is not really needed, but here for completeness.
        # The client process could simply print the messages it receives to the
        # terminal.
        print(message)

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

    def ack_betting_info(self, pool_amt, max_bet, current_bet):
        '''
        Displays betting info gathered from the server including the 
        amount of money currently in the pool, how much the call amount is, 
        how much this player has bet so far, and the amount in this player's
        wallet.

        pool_amt: int - The money in the current bet pool.
        max_bet: int - The highest bet so far.
        current_bet: int - The amount this player has bet so far in the round.
        '''
        print('Pool: ', '$', pool_amt, sep='')
        print('Highest bet (call amount): ', '$', max_bet, sep='')
        print('Your current bet: ', '$', current_bet, sep='')
        print('Your wallet: ', '$', self.wallet, sep='')

    def reset(self):
        '''
        Reset the player hand
        '''
        self.hand = cards.Hand(cards.NUM_CARDS_IN_HAND)
