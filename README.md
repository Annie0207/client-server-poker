# client-server-poker
A poker game implemented using a client-server architecture and TCP level networking.

To start the server run 

```
poker_server.py <host> <port>
```

This will cause the server to wait for players. The first player to join must start the game using the command:

```
poker_client.py start <host> <port> <num_players> <wallet_amt> <ante> <name>
```

Both the server and this player will now wait until there are `num_players` number of players. `wallet_amt` is basically the buy in for players, `ante` is the amount players must ante before hands, `name` is the player's name.

Further players do not need to start another game, so they use a different command.

```
poker_client.py join <host> <port> <name>
```

After all players have joined, the game will start.

An important thing to note about our project: while we have a working implementation, it is not a full-featured game. We had trouble getting the fold mechanics to work correctly in time for the due date and ultimately had to settle for a fold causing a player to leave the game entirely. In this sense, each run of the server/clients resembles a single hand rather than a full game.
