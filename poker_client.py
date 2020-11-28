'''
The `poker_client` provides business logic to allow a client (player) to 
communicate with the poker server (game manager) and play a game of poker with
others.
'''

def main():
    # Parse command line args & validate
    # Get server response for `start` or `join`
    # If successful, set name and wait for other players to join until game starts
    # Send Ante, if enough in wallet
    # Get cards
    # Allow player to swap cards until ready (set time limit (1 min?))
    # Wait until this player's turn, print notifications of other players' choices
    # On turn, get player choices until betting option chosen (check only allowed by first player to go)
    # Repeat ^ until betting round over
    # Choose cards to trade in, if any (set time limit (1 min?))
    # Second round of betting (unless round ended in last bet by all players folding but one)
    # If still in game, send hand to server for evaluation
    # Get game result
    pass

if __name__ == '__main__':
    main()