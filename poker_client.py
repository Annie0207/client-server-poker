'''
The `poker_client` provides business logic to allow a client (player) to 
communicate with the poker server (game manager) and play a game of poker with
others.
'''
import sys
import socket

import player
import cards

# Possible command options
START = 'start'
JOIN = 'join'
BEGIN = 'begin'
NOTIFY = 'notify'
DISCARD = 'discard'

# Message buffer size (somewhat arbitrary, should be fine for all messages)
BUFF_SIZE = 512


def main(argv):
    # Parse command line args
    args = get_cmd_args(argv)
    cmd = args[0]
    server_addr = args[1]
    if cmd == START:
        num_players, wallet_amt, ante, name = args[2:]
        msg = '{} {} {} {} {}'.format(
            START, num_players, wallet_amt, ante, name)
    else:
        name = args[2]
        msg = '{} {}'.format(JOIN, name)

    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_addr)

    # Send message and wait for response
    sock.send(msg.encode())
    response = sock.recv(BUFF_SIZE).decode()
    print(response);

    # If successful, set name and wait for other players to join until game starts
    player = handle_start_and_join_response(response, name)

    print('Waiting for other players.')
    wait_for_start(sock)

    print('Players found, starting game')
    game_play(sock, player)


def game_play(sock, player):
    '''
    Primary gameplay functionality for the client.

    sock: socket - client socket object
    player: Player - the player object
    '''
    # Most of these should be in other functions:
    # Send Ante, if enough in wallet (allow player to leave if wanted?) // handle_ante() -> 
    # Get cards  //sock.recv(), player.add_cards()

    # Allow player to swap cards until ready (set time limit (1 min?)) //delete?

    # Wait until this player's turn, print notifications of other players' choices
    # On turn, get player choices until betting option chosen (check only allowed by first player to go)
    # Repeat ^ until betting round over
    # Choose cards to trade in, if any (set time limit (1 min?))
    # Second round of betting (unless round ended in last bet by all players folding but one)
    # If still in game, send hand to server for evaluation
    # Get game result
    # Start next hand

    # pass
    is_leave = False
    while not is_leave:  
        print("New game start")
        ante_true = handle_antes(sock, player)

        if not ante_true: 
            return

        handle_deal(sock, player)
        # Get first player id
        first_player_id = sock.recv(BUFF_SIZE).decode()
        first_player_id = first_player_id.strip().split()
        print('The first player is {}'.format(first_player_id[0]))

        # Handle first round of betting
        print("Start first round of betting") 
        is_leave = handle_betting(sock, player, int(first_player_id[0]))

        if is_leave:
            return

        # Check if the player leave the game or not
        # if not is_leave:

        # Check if has winner, start new game or continue a second round of betting 
        msg = sock.recv(BUFF_SIZE).decode()
        if msg == "Winner":
            winner_info = sock.recv(BUFF_SIZE).decode()
            print(winner_info)
        elif msg == "Betting":
            # Handle swap the cards in hand
            print("Swap the cards")
            handle_card_trade(sock, player)

            # Get first player id
            first_player_id = sock.recv(BUFF_SIZE).decode()
            first_player_id = first_player_id.strip().split()
            print('The first player is {}'.format(first_player_id[0]))

            # Handle second round betting
            print("Start second round of betting")
            is_leave = handle_betting(sock, player, int(first_player_id[0]))

            if is_leave:
                return

            # Get the winner information
            winner_info = sock.recv(BUFF_SIZE).decode()
            print(winner_info)

        # Add the bets to wallet if the player win the game
        msg = sock.recv(BUFF_SIZE).decode()
        print(msg)
        msg = msg.strip().split()

        if msg[0] == 'Win':
            player.win_pool(int(msg[1]))

        # Reset player
        player.reset()

        # Check with player if start new game
        resp = sock.recv(BUFF_SIZE).decode()
        print(resp)
        new_game = input()

        if new_game == 'N':
            #msg = 'Leave {}'.format(player.id)
            sock.send(new_game.encode())
            print('player {} leave game'.format(player.id))
            sock.close()
            is_leave = True
        else:
            msg = 'Start'
            sock.send(msg.encode())

        if is_leave:
            return 

        msg = sock.recv(BUFF_SIZE).decode()
        if msg == 'Over':
            print("Game Over... ")
            sock.close()
            is_leave = True

        else:
            print("Start new game...")


    

def handle_start_and_join_response(response, player_name):
    '''
    Handles the server response from a start or join call. If join successfull,
    gets the player ID, asks for a name, and returns a new player object.
    '''
    response = response.strip().split()

    # Ensure success
    if len(response) != 4 or response[0] != 'ack' or response[1] != 'join':
        print('fatal error:', ' '.join(response))
        sys.exit(1)

    # Get assigned ID and wallet amount (provided by server for join)
    p_id = int(response[2])
    wallet_amt = int(response[3])

    return player.Player(wallet_amt, p_id, player_name)


def wait_for_start(sock):
    '''
    Waits for the server to start a game. Prints any messages received while
    waiting.

    sock: socket - client socket object
    '''
    while True:
        msg = sock.recv(BUFF_SIZE).decode()
        print(msg)

        if msg == BEGIN:
            break

        elif msg.startswith(NOTIFY):
            start = len(NOTIFY) + 1  # +1 to get past space in message
            print(msg[start:])
            continue

        else:
            print("Unexpected message:", msg)
            break


def handle_antes(sock, player):
    '''
    Notifies the player that it is time to ante. 
    By default, the player will be asked if they want to ante (the alternative is leaving the game), 
    but this can be set to false if the ante should be automatic, such as at the start of the game. 
    When ante is invoked, it subtracts the ante amount from the player’s wallet and sends an ack to 
    the server so it can add the ante to the betting pool. If a player opts to leave the game, 
    the program invokes the leave API method on the server.

    sock: the socket
    player: the player
    
    return a bool ante result 
    '''
    # get the response from server and parse ante_amt and get_response 
    response = sock.recv(BUFF_SIZE).decode()
    response = response.strip().split()
    print(response)
    ante_amt = int(response[0])
    get_response = int(response[1])

    # get_response = 1, means give player the right to choose leave or ante the game
    if get_response == 1:
        while True:
            resp = input('Do you want to ante or leave the game？ \n')
            if resp == 'leave':
                msg = 'leave {}'.format(player.id)
                sock.send(msg.encode())
                print('player {} leave game'.format(player.id))
                sock.close()
                return False
            elif resp == 'ante':
                return ante_helper(sock, player, ante_amt)              
            else:
                continue
    else: # default get_response = 0, every player ante the game 
        return ante_helper(sock, player, ante_amt)  

def ante_helper(sock, player, ante_amt):
    '''
    Helper function for handle_ante(). If player ante successfully, send ante info to server side, 
    else, send leave info to server side

    sock: the socket
    player: the player
    ante_amt: ante amount 

    '''
    ante_result = player.ante(ante_amt)
    print(ante_result)
    if ante_result:
        msg = 'ante {} {}'.format(
        player.id, ante_amt)
        sock.send(msg.encode())
        print('player {} ante {}'.format(player.id, ante_amt))
    else:
        msg = 'leave {}'.format(player.id)
        sock.send(msg.encode())
        print('player {} ante failed and leave game'.format(player.id))
        sock.close()

    return ante_result

def handle_deal(sock, player):
    '''
    Get the cards from deck and add to the player. Five card draw is one of the most common types of poker hands. 
    Each player is dealt five cards, then a round of betting follows. 

    sock: the socket
    player: the player
    '''
    # receive deal from deck
    deal = sock.recv(BUFF_SIZE).decode()
    print(deal)
    deal = deal.strip().split()
    card_list = []

    # creat card from deal and add to card list
    for repr in deal:
        card = cards.Card(repr[0], repr[1:])
        print(card)
        card_list.append(card)

    # add card_list to player 
    player.add_cards(card_list)
    print('Player {} get cards from deck successfully'.format(player.id))

    # info server the player received cards
    msg = 'Received'
    sock.send(msg.encode())


def handle_betting(sock, player, first_player_id):
    '''
    Handle the betting process. The first player will check, and then next player could choose 
    one of the four call/raise/fold/leave action until the round of betting is over

    sock: the socket
    player: the player
    first_player_id: the first player. Only the first player could do check action
    '''
    is_leave = False
    while not is_leave:
        # Get the bet info from server
        bet_info = sock.recv(BUFF_SIZE).decode()
        if bet_info == "Over":
            break; 

        bet_info = bet_info.strip().split()   
        print(bet_info)

        # Get the call amount to deduct from player's wallet
        max_bet = int(bet_info[0])
        cur_bet = int(bet_info[1])
        call_amt = max_bet - cur_bet 
        first_player = True if bet_info[2] == "True" else False

        while True: 
            # Get player's action from command line       
            action = player.get_action()
            print(action)
            action = action.strip().split()
            if action[0] != 'check' and first_player:
                print("First player must check.")
                continue

            # handle the action 
            if action[0] == 'check' and first_player:
                if handle_check(sock, player, cur_bet):
                    break
            elif action[0] == 'call':
                if handle_call(sock, player, call_amt):
                    break
            elif action[0] == 'raise':
                raise_amt = int(action[2])
                if handle_raise(sock, player, raise_amt):
                    break
            elif action[0] == 'fold':
                msg = "Fold {}".format(player.id)
                sock.send(msg.encode())
                break
            elif action[0] == 'leave':
                if handle_leave(player, sock):
                    is_leave = True
                    break
            else:
                continue
    return is_leave

def handle_check(sock, player, cur_bet):
    '''
    Handle the check action. Check is basically a call action, which is allowed only for the first player 
    when the player own nothing to the pot, the check amount is default to the ante amount. 

    sock: the socket
    player: the first player
    cur_bet: the ante amount
    '''
    checked = player.ack_call(cur_bet)
    if checked:
        msg = "Check {} {}".format(player.id, cur_bet)
        sock.send(msg.encode())
        return True
    
    print("Checked failed, please choose another action!")
    return False


def handle_call(sock, player, call_amt):
    '''
    Handle the call action. When you call, you bet enough to match what has been bet since the last time 
    you bet (for instance, if you bet a dime last time, and someone else bet a quarter, you would owe fifteen cents).

    sock: the socket
    player: the player
    call_amt: the call amount to deduct from wallet
    '''
    called = player.ack_call(call_amt)
    if called:
        msg = "Call {} {}".format(player.id, call_amt)
        sock.send(msg.encode())
        return True
    
    print("Call failed, please choose another action!")
    return False


def handle_raise(sock, player, raise_amt):
    '''
    Handle the raise action. When you raise, you first bet enough to match what has been bet since the last time 
    you bet (as in calling), then you 'raise' the bet another amount (up to you, but there is typically a limit.) 
    Continuing the above example, if you had bet a dime, the other person raised you fifteen cents (up to a quarter), 
    you might raise a quarter (up to fifty cents). Since you owed the pot 15 cents for calling and 25 for your raise, 
    you would put 40 cents into the pot.

    sock: the socket
    player: the player
    raise_amt: the raise amount
    '''
    raised = player.ack_call(raise_amt)
    if raised:
        msg = "Raise {} {}".format(player.id, raise_amt)
        sock.send(msg.encode())
        return True
    
    valid_amt = player.wallet - call_amt
    print("Raise failed, please raise valid amount between 1 to {}".format(valid_amt))
    return False

def handle_leave(player, sock):
    player.ack_player_left(player.name)
    msg = "Leave {}".format(player.id)
    sock.send(msg.encode())
    sock.close()
    return True


def handle_betting_info():
    pass


def handle_card_trade(sock, player):
    resp = sock.recv(BUFF_SIZE).decode()
    if resp.startswith(DISCARD):
        print("Your current card is \n")
        player.hand.print_hand()
        start = len(DISCARD) + 1  # +1 to get past space in message
        discard = input("Are you going to swap cards? Y/N: \n")
        while discard != 'Y' :
            if discard == 'N':
                sock.send("N".encode())
                return
            discard = input("Are you going to swap cards? Y/N: \n")
        print(resp[start:])
        print("Please choose which card index to discard. The card index is 1-indexed. You can discard at most 3 cards. \n" + 
               "Example: If you want to discard card 1 and 3, type in '1 3'")
        discard_cards = input()
        if len(discard_cards) == '':
            return
        discard_list = discard_cards.split()
        card_list = []
        for card in discard_list:
            card_list.append(int(card))
        player.delete_cards(card_list)
        msg = "{}".format(len(card_list))
        sock.send(msg.encode())
        handle_deal(sock, player)



        


def get_cmd_args(argv):
    '''
    Validates and returns command line arguments.

    For `start` returns ('start', (host, port), num_players, wallet_amt, ante, name)
    For `join` returns ('join', (host, port), name)
    '''
    possible_cmds = set([START, JOIN])
    cmd = argv[1]

    # Ensure valid command
    if cmd not in possible_cmds:
        print('unknown command', cmd)
        help()
        sys.exit(1)

    # Extract host, port
    try:
        host = argv[2]
        port = int(argv[3])
        server_addr = (host, port)
    except IndexError:
        print("host and port of server are required")
        help()
        sys.exit(1)

    # Get `start` args
    if cmd == START:
        try:
            # Extract the args
            num_players = argv[4]
            wallet_amt = argv[5]
            ante = argv[6]
            name = argv[7]

            # Convert to ints
            num_players = int(num_players)
            wallet_amt = int(wallet_amt)
            ante = int(ante)

            return (cmd, server_addr, num_players, wallet_amt, ante, name)
        except IndexError:
            print("required arguments missing")
            help()
            sys.exit(1)
        except ValueError:
            print("num_players, wallet_amt and ante must be integers")
            help()
            sys.exit(1)

    # Get `join` args
    if cmd == JOIN:
        name = argv[4]
        return (cmd, server_addr, name)

    # Unexpected error if this is reached
    print("something unexpected happened, please try again")
    help()
    sys.exit(1)


def help():
    '''
    Prints a usage help message.
    '''
    print('usage:')
    print('poker_client.py start <host> <port> <num_players> <wallet_amt> <ante> <player_name>')
    print('or')
    print('poker_client.py join <host> <port> <palyer_name>')


if __name__ == '__main__':
    main(sys.argv)
