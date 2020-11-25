'''
The `player` module contains a class describing a player (Player) in a game 
of poker. It also contains a class for a hand of cards (Hand) that is used by
the player. The Player class implements the poker API created for this project.
The API can be viewed in Google Docs here: 
https://docs.google.com/document/d/1p03ydY3g0QY7WARs0TSkFAcQ-Ut0rUP-xKc40t47tTs/edit?usp=sharing
'''


# Char representations of suits
# Hearts, Diamonds, Clubs, Spades
SUITS = set(['H', 'D', 'C', 'S'])

# Char representations of rank including numbers and Jack, Queen, King, Ace
RANKS = set(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])

# Player

# Hand
