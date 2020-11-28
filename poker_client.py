'''
The `poker_client` provides business logic to allow a client (player) to 
communicate with the poker server (game manager) and play a game of poker with
others.
'''

import sys
import socket

import player

# Possible command options
START = 'start'
JOIN = 'join'
BEGIN = 'begin'
NOTIFY = 'notify'

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

    # If successful, set name and wait for other players to join until game starts
    player = handle_start_and_join_response(response, name)
    print('Waiting for other players.')
    wait_for_start(sock)
    print('Players found, starting game')


def game_play():
    '''
    Primary gameplay functionality.
    '''
    # Send Ante, if enough in wallet (allow player to leave if wanted?)
    # Get cards
    # Allow player to swap cards until ready (set time limit (1 min?))
    # Wait until this player's turn, print notifications of other players' choices
    # On turn, get player choices until betting option chosen (check only allowed by first player to go)
    # Repeat ^ until betting round over
    # Choose cards to trade in, if any (set time limit (1 min?))
    # Second round of betting (unless round ended in last bet by all players folding but one)
    # If still in game, send hand to server for evaluation
    # Get game result
    # Start next hand
    pass


def get_cmd_args(argv):
    '''
    Validates and returns command line arguments.

    For `start` returns ('start', (host, port), num_players, wallet_amt, ante)
    For `join` returns ('join', (host, port))
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
    print('poker_client.py start <host> <port> <num_players> <wallet_amt> <ante>')
    print('or')
    print('poker_client.py join <host> <port>')


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

        if msg == BEGIN:
            break

        elif msg.startswith(NOTIFY):
            start = len(NOTIFY)
            print(msg[start:])
            continue

        else:
            print("Unexpected message:", msg)


if __name__ == '__main__':
    main(sys.argv)
