'''
The `poker_server` module contains the business logic that allows the server
to communicate with poker clients and allow gameplay.
'''

import sys
import socket
import time

import game_state_manager as gsm

BUFF_SIZE = 512

BEGIN = 'begin'
NOTIFY = 'notify'


def main(argv):
    # Parse command line arguments
    addr = get_cmd_args(argv)

    # Setup server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen()

    print('Server started, waiting for first player.')

    # Wait for `start` from a player and set-up game
    manager = wait_for_start(sock)

    print("First player found. Waiting for other players to join.")

    # Wait for players to join and start game
    wait_for_players(sock, manager)

    print("Players joined. Starting game.")
    game_play(sock, manager)


def game_play(sock, manager):
    '''
    Primary gameplay functionality for the client.

    sock: socket - server socket
    manager: GameStateManager - the game manager object
    '''
    # Get antes 
    # Deal cards to all players // manager.get_cards sock.send()
    # Set first player turn //
    # Repeat: //
    #   Notify player, wait for choice // call||fold||leave, call||raise||fold||leave
    #   Handle choice
    #   Cycle turn
    #   Until betting ends
    # Notify betting round over  //check_win
    # Wait for clients to choose cards to swap //repeat player_num times
    #   assuming more than one player still in the game 
    # Second betting round
    # Get remaining players hands and evaluate winner
    # Notify players of winner, show hands (unless all but one folded)
    # Repeat steps until all players have left but one
    # pass
    handle_antes(sock, manager)


def wait_for_start(sock):
    '''
    Makes the server wait until it gets a successful start command from a 
    client, then creates a GameStateManager and returns it.

    sock: socket - server socket
    '''
    while True:
        # Get connection
        start = 'start'
        conn, addr = sock.accept()
        msg = conn.recv(512).decode()
        parts = msg.split()

        # Ensure start message
        if parts[0] != start:
            err = 'err start waiting for start but received: ' + msg
            conn.send(err.encode())
            continue

        # Extract provided args
        try:
            # Extract
            num_players, wallet_amt, ante_amt, name = parts[1:]
            num_players = int(num_players)
            wallet_amt = int(wallet_amt)
            ante_amt = int(ante_amt)

            # Validate
            if (not (2 <= num_players <= 5)) or (wallet_amt < 5):
                raise ValueError()
        except:
            err = 'err start invalid arguments'
            conn.send(err.encode())
            continue

        # Create game manager and add the first player
        manager = gsm.GameStateManager(num_players, wallet_amt, ante_amt)
        p_id = manager.join(conn, addr, name)

        # Send ack to player
        ack = 'ack join ' + str(p_id) + ' ' + str(wallet_amt)
        manager.get_player_conn(p_id).send(ack.encode())

        return manager  # breaks loop


def wait_for_players(sock, manager):
    '''
    Makes server wait for players to join until the number of players is the 
    same as that specified during the start.

    sock: socket - server socket
    manager: GameStateManager - a game state manager
    '''
    max_players = manager.num_players
    while manager.get_curr_num_players() < max_players:
        # Get connection
        join = 'join'
        conn, addr = sock.accept()
        msg = conn.recv(BUFF_SIZE).decode()
        parts = msg.split()

        # Ensure join message
        if parts[0] != join:
            err = 'err join waiting for join but got ' + msg
            conn.send(err.encode())
            continue

        # Add player
        name = parts[1]
        p_id = manager.join(conn, addr, name)

        # Send ack to player
        ack = 'ack join ' + str(p_id) + ' ' + str(manager.wallet_amt)
        manager.get_player_conn(p_id).send(ack.encode())

        # Sleeping here to ensure the ack message does not get concatenated
        # with the notify message below. Since TCP is a stream, need to build
        # in some seperation or else they will become a single message and
        # cause errors.
        time.sleep(0.1)

        # Notify other players
        num = manager.get_curr_num_players()
        num_left = max_players - num
        msg = NOTIFY + ' Player {} has joined the game. Waiting for {} more players.'.format(
            name, num_left)
        manager.notify_all(msg)
        time.sleep(0.1)

    manager.notify_all(BEGIN)
    time.sleep(0.1)


def handle_antes(sock, manager):
    '''
    Call manager
    '''
    # wallet_amt = manager.wallet_amt # need implementation
    ante_amt = manager.ante_amt # need implementation
    get_response = 0
    msg = str(ante_amt) + " " + str(get_response)
    manager.notify_all(msg)
    time.sleep(0.1)
    
    count = manager.num_players
    for id in range(1, count + 1):
        conn = manager.players[id]['conn']
        msg = conn.recv(BUFF_SIZE).decode()
        parts = msg.split()

        if get_response == 1 and parts[0] == 'leave':
            p_id = int(parts[1])
            player = manager.leave(p_id)
        elif parts[0] == 'ante':
            p_id = int(parts[1])
            ante = int(parts[2])
            manager.ack_ante(ante)
            print('acknowledge player {} ante'.format(p_id))



def handle_deal():
    pass


def handle_betting():

    pass


def handle_check():
    pass


def handle_call():
    pass


def handle_raise():
    pass


def handle_betting_info():
    pass


def handle_card_trade():
    pass


def handle_evaluate_winner():
    pass


def get_cmd_args(argv):
    '''
    Validates command line arguments and returns a tuple of (host, port) to
    start the server on.
    '''
    if len(argv) != 3:
        print('missing required arguments')
        help()
        sys.exit(1)

    host = argv[1]
    port = int(argv[2])
    return (host, port)


def help():
    '''
    Prints a usage help message.
    '''
    print('usage:')
    print('poker_server.py <host> <port>')


if __name__ == '__main__':
    main(sys.argv)
