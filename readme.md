# NES Tetris Q-Learning Agent

# Introduction

NES Tetris is an old version of Tetris played on the Nintendo Entertainment System, and is gaining
in popularity worldwide, with events such as the Classic Tetris World Championship (CTWC). This
project aims to simulate the game of NES Tetris (with its various quirks) and create an AI agent
that is capable of playing the game at a somewhat competent level.

For the record, I play using an emulator (Retroarch) using a keyboard, and my personal best is barely
600k and I can't play past level 19 for long. Hopefully this agent can surpass my mediocre gameplay.

# Mechanics of NES Tetris

Tetris itself is a game where the player aims to stack different Tetromino (or pieces) of different
shapes. Each piece itself consists of 4 blocks, and there are 7 unique configurations. The player
is able to rotate pieces and place them in a board. When a line on the board is filled with parts
of pieces, then that line is deleted from the board. This continues as the player clears more lines
and eventually, given a set of pieces, the player will be unable to place a piece on the board and
thus lose the game (top off).

Conventional Tetris agents aim to play the game as long as possible, but this is not possible for
NES Tetris. The game of NES Tetris uses levels, which determine the speed at which pieces drop.
This creates a problem where the player or agent is limited to a set number of line clears due to
pieces being physically impossible to be moved to a desirable location, thus making the player top
off at some point.

As such, the game of NES Tetris is divided into 3 segments: level 18, levels 19-28 and level 29.
This is due to each segment having different frame delays before a piece drops (3, 2, 1 respectively).
To simplify game mechanics, the transitions between each segment occurs at 130 and 230 line clears.
At level 29, its generally impossible to continue playing for the majority of players.

Hence, the goal of NES Tetris (and this project) is to score as efficiently as possible. Like other
versions of Tetris, having more line clears at once results in more points. A Tetris (4 line clears
at once) is what players aim to get, which is only achievable by the 'I' piece). This project aims to 
create an agent that is capable of not only surviving the game of NES Tetris but to score as well
as possible. While other projects focus on the number of line clears (> 1000 lines), the point of
this project is not the quantity of line clears, but the quality or efficiency of line clears in
a restrictive enviroment. 

Compared to other versions, NES Tetris uses a completely random piece generation, showing the next
piece but not allowing for holding of pieces.

# Agent

## Typical Player Behavior

In order to score efficiently, players follow a general strategy which hinges on creating a board
state that accomodates many pieces as possible. This is to reduce the effect of bad piece luck.

This generally involves building on the left, and creating a sloped (sloping down from the left)
or a board that is 'relatively' flat with bumps. Such boards accomodate the more troublesome 'S'
or 'Z' pieces without creating overhangs, whilst being able to accomodate the flat pieces.

Of course, players may employ more advanced techniques in anticipation or response to bad luck
by doing actions like tucks (set a piece to the side before it is placed) or burns (clear lines
without making a Tetris). It is not expected that the agent can somehow learn these complex
techniques on its own, and it could be implemented by more specific actions or features.

Notes:
> For tucks and spins, they could be implemented at a later time by tweaking the move generation
> by checking if it is possible to perform them before the piece is set, and then adding them
> onto the pool of moves.

## Features

The agent uses several features which form the basis of general player behavior.

The goal of the agent is to stack efficiently and as low as possible, and then score Tetrises
if possible.

> 1. Landing Height - The height at which the piece will result in. Generally, the agent
> should place pieces lower on the board if possible to avoid topping off.

> 2. Board Height - The average height of all filled columns. Generally, the agent should
> try to place pieces evenly across the board so that a portion of the board does not
> become disproportionally stacked.

> 3. Bumpiness - The sum of absolute differences between heights of filled columns. The agent should
> stack such that bumpiness is low, but as mentioned previously, some bumpiness is needed.

> 4. Holes - The sum of empty cells that have a filled cell above it. Generally, the agent
> should minimise this as holes are hard to fill by moves.

> 5. Lines Cleared - The number of lines cleared by a move. Generally, the agent should
> try to maximise Tetris clears, although it should not keep making small line clears as there
> are a limited number of lines that can be cleared.

> 6. / 7. Column & Row Transitions - The sum of cells that are adjacent to the opposite cell (filled vs
> unfilled, vice versa). Generally, this should be lower as it suggests that the board has many
> potholes, either vertically or horizontally.

> 8. Proportion of Cells on the Left - The proportion of cells that are filled and at the left
> of the board. Generally, the agent should prioritise the left more than the right.

## Gameplay

Given a pre-generated set of pieces (even random), the game of Tetris can be modelled as a very 
large tree, with each subsequent level denoting a move (left, right, down, rotate) and being
represented by a board state. The end goal is to find a leaf with the best scores. Clearly,
this is a very huge search space, and thus we will need to find a way to reduce it.

Intuitively, the player should be moving the pieces one move at a time (left, right, down, rotate).
However, this isn't an effective way to play the game. As such, this is simplified into possible board
states and the moves needed to accomplish it.

In order to simulate the gameplay of NES Tetris, the agent is presented with many legal moves.
The resulting board of these moves is then evaluated before the best move is selected. The moves
are pre-generated as a permutation of general moves that can be performed (move up to 6 times,
rotate up to 3 times). This provides a wide range of moves and they are verified to be legal
before evaluation.

A breadth-first search might be able to generate more moves (including actions like tucks and spins),
but for simplicity and speed, we utilise this pre-generated permutation first.

### References:
https://github.com/nuno-faria/tetris-ai