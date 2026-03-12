# Real-Time Stamina Chess

A fast-paced, real-time multiplayer chess game built with Python and Pygame. Unlike traditional turn-based chess, both players can move their pieces simultaneously, limited only by piece-specific stamina costs and movement cooldowns.

## Features

* **Real-Time Gameplay:** No waiting for turns. If you have the stamina and your piece isn't on cooldown, you can move.
* **Stamina System:** Every piece has a specific "energy" cost to move. Moving a Queen is much more taxing than moving a Pawn!
* **Cooldowns:** Prevents "spamming" moves with the same piece, adding a layer of tactical timing.
* **Multiplayer Networking:** Client-server architecture using Python sockets to handle concurrent moves and synchronization.
* **Dynamic UI:** Includes stamina bars for each player and visual feedback for cooldown states (Red/Green indicators).

## Piece Stamina Costs

Movement costs are balanced to reflect the power of the piece:
* King: 0.5
* Pawn: 1.0
* Knight/Bishop: 2.5
* Rook: 3.0
* Queen: 4.0

Stamina regenerates over time at a rate of 0.5 units per second, up to a maximum of 10.

## Installation & Setup

1. Clone the repository:
   ```
   git clone https://github.com/cupkejk/Chess.git
   cd Chess
   ```

2. Install dependencies:
   Make sure you have Python 3.x installed. You will also need the Pygame library:
   ```
   pip install pygame
   ```

## How to Run

### Automatic Launch (Windows)
Run the automated script to start the server and two clients simultaneously:
python run.py

### Manual Launch
1. Start the server first:
   ```
   python server.py
   ```
2. Launch two separate client instances:
   ```
   python client.py
   ```

Note: If running across different machines, pass the server's IP address as an argument to the client:
   ```
   python client.py 192.168.x.x
   ```
## How to Play

* Click and drag your pieces to move them.
* Watch your Stamina Bar (right side of the board). If the bar is Red, you are on cooldown. If it is Green, you are ready to move.
* If both players move at the exact same time, the server processes the moves based on a randomized priority system to ensure fairness.
* Win the game by capturing the opponent's King!

## Project Structure

* chess.py: Core game logic, piece movement rules (masks), and stamina/cooldown calculations.
* server.py: Handles network connections, move validation, and state synchronization between players.
* client.py: The Pygame GUI, handling user input and rendering the game state.
* run.py: Utility script for local testing.
