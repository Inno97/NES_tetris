# General Training Behavior

The agent is trained for 3000 episodes at 50 episode intervals, and the epsilon starts at 0.95
and decays linearly until 2000 episodes. Agent performs badly until about 1500 episodes as
expected, and then it should start improving from there.

The trend to observe in training would be of course, exponential improvement starting at around
1500 episodes. Improvements will plateau off eventually.

## Current Progress

Train agent / tune features -> Add on levels / delays -> Train agent

## The Basics of the Agent

The end goal is to produce an agent that stacks efficiently without dying. Hence, we select multiple
features that encourage this.

Through user testing, the game can be played efficiently without having too complex behavior.

Generally, the agent should:

1. Stack the board nicely to make Tetrises
2. Clear Tetrises when possible
3. Avoid making holes
4. Clear holes if they are made

This means that there are 2 categories of actions that the agent should perform. Being to stack 
or clear. Thus, several features are used:

1. board_height
> The overall height of every filled column.
> Ideally, this should not be too high as it will just be dangerous for the agent.

2. bumpiness
> The sum of absolute differences in height between adjacent columns, except for the rightmost one.
> Ideally, this should be relatively low, as it means that the board isn't a haphazard mess and
> pieces have the space to fit in.

3. valleys
> The number of columns where the absolute difference in height is more than 3, except for the 
> rightmost.
> Ideally, this should be 0, as the only piece that can fit into these is the I piece, if a
> column has adjacent columns whose height is taller by 3. Even if it is only one side, it is better
> to not have it, as it means that the board is bumpy.

4. holes
> The number of empty cells that have a filled cell above.
> Ideally, this should be 0, as holes prevent Tetrises and are hard to clear.

5. holes_created
> The number of holes created by a move.
> Ideally, this should be 0, as we should not be making more holes.

6. lines_cleared
> The number of lines cleared by a move.
> Ideally, this should either be 0, or as high as possible (line efficiency).

7. lines_ready_to_clear
> The number of lines that are filled except the rightmost column, that are created by a move.
> Ideally, this should be as high as possible, as the agent is stacking well to make Tetrises.

8. row_transitions
> 

9. col_transitions
> 

10. right_well
> 

11. holes_covered
> 


## Performance


# Notes

## The Original Agent

We start off with a few key features that were used in other projects and papers:

> landing_height, board_height, bumpiness, holes, lines_cleared, row_transitions, column transitions

The agent performs decently, being able to clear around 50 lines on average.

However, agent fails primarily due to it being unable to clear certain lines, and thus
will slowly build up the board and top off eventually. Stacking ability is questionable
as the agent tends to prefer to clear lines at the expense of board state.

The board tends to have some holes, showing that the agent has some difficulty in stacking
super efficiently. For some odd reason, the agent sometimes stacks a well on the left side.
Moreover, the agent learns to simply clear lines when it can, which can result in games
like these:

Example 'good' game:
> Score: 71370
> Lines cleared: 96
> =========================
> Lines cleared:
> Single: 84
> Double: 6
> Triple: 0
> Tetris: 0

The agent stacks decently, but ends up with potholes which it doesn't cover. As such, the agent
is unable to clear these lines, which result in the board getting higher and higher. Due to the
overzealous nature of the agent to clear lines, this results in non-ideal board states after
clearing a line. The agent may be clearing lines, but it is not doing so smartly at all.

## Tucks and Spins

Tucks and spins are then implemented. After validating that a move is legal and generating the 
board state, additional 4 moves are validated (left / right tuck / spin), and then they are added
to the List of legal moves after validation. Although this does not account for all tucks
(sometimes, you can tuck while the piece is still falling), it should be enough for the most part.
Implementing the additional tucks would vastly increase the search space of the agent and thus make
things too complicated and slow to run.

This fixes one of the bigger issues with the agent, which is that it cannot easily get itself out
of a bad board state due to bad luck or after clearing lines.

### The S and Z problems

These pieces are problematic as the agent is generally unable to rectify the damage caused by them 
on the board state. These 4 board states shows the issue. Mainly, a hole is created (states 1 / 2), or
an overhang is created (states 2 / 3).

The agent can attempt (but fails to anyway) to fix the hole, but at the end state (4), the hole 
isn't fixed. While the overhang is cleared eventually (2 / 4), it's just probably due to dumb
luck that the agent burned the overhang successfully.

One way to fix this would be to implement tucks and spins. Although this gives the agent the
ability to fix these problems rather than prevent it from doing it in the first place. It's not
going to (and didn't) dramatically improve the agent's performance.

> 1. Initial board state   2. After dropping a Z    3. After dropping a S   4. The end state, 
>                          piece, a hole is         piece, an overhang is   where the hole is not 
>                          created                  created                 fixed, but the overhang is
> =====================    =====================    =====================   =====================
> | | | | | |=|=| | | |    | | | | | | |=|=| | |    | | | | | |=|=| | | |   | | | | | |=|=| | | |
> | | | | | | |=|=| | |    | | | | | |=|=| | | |    | | | | | |=|=| | | |   | | | | | |=|=| | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | | | | |X| |X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | | |X|X|X| | |X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | | |X|X|X|X|X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X|X|X| |X|X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X|X|X|X| |X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X|X| |X| |X|X| |X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X| |X|X|X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X|X|X|X| |X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X|X|X|X|X|X|X| |X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X| |X|X|X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X|X| |X|X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X|X|X| |X|X|X|X|X|
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X| | |X|X|X| |X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   |X|X|X|X|X|X|X|X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |   | |X|X|X|X|X|X|X|X| |
> | | | | | | | | | | |    | |X| | | | | | | | |    | |X| | |X|X| | | | |   |X|X|X|X|X| |X|X|X|X|
> | | |X| | | | | | | |    |X|X|X| | | | | | | |    |X|X|X|X|X| | | | | |   |X|X|X|X|X| |X|X|X|X|
> | | |X|X|X|X|X|X|X| |    |X| |X|X|X|X|X|X|X| |    |X| |X|X|X|X|X|X|X| |   |X| |X|X|X|X|X|X|X|X|
> =====================    =====================    =====================   =====================

After implementing a way to create tucks and spins, the agent is able to use this to rectify the
overhangs (if it chooses to). Below are 2 board states that show this. Although this trained 
model does not care about holes and transitions, so it makes pretty bad decisions.

> 1. An overhang is        2. Overhang is fixed     3. Overhang after        4. Overhang is 
> created after a Z        by a tuck                placing a Z piece.       fixed by a spin
> piece is placed.         
> =====================    =====================    =====================    =====================
> | | | | | |=|=|=| | |    | | | | | |=|=| | | |    | | | | | |=|=|=| | |    | | | | | |=|=| | | |
> | | | | | | | |=| | |    | | | | | |=|=| | | |    | | | | | | |=| | | |    | | | | | |=|=| | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | |X|X| | | | |    | | | | |X|X| | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | |X|X|X| | |    | | |X|X|X|X|X|X| | |
> | | | | | | | | | | |    | | | | | | | | | | |    | |X|X| |X|X|X|X|X| |    | |X|X|X|X|X|X|X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | |X|X|X|X|X|X|X|X| |    | |X|X|X|X|X|X|X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    | |X|X|X|X|X|X|X|X| |    | |X|X|X|X|X|X|X|X| |
> | | | | | | | | | | |    | | | | | | | | | | |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | | | | | |X|X| | | |    | | | |X| |X|X| | | |    |X| |X| |X|X|X|X|X| |    |X| |X| |X|X|X|X|X| |
> | | | | | | |X|X| | |    | | | |X|X|X|X|X| | |    |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X| | |
> =====================    =====================    =====================    =====================

## Right Well

As mentioned previously, the agent tends to just clear lines for the sake of clearing lines.
Based on the rewards for clearing lines, the agent will be heavily incentivised to do so.
This tends to result in mediocre board states after clearing lines, as the agent creates
holes and overhangs as it clears a line.

There are thus two things to focus on: Creating a good board state and maintaining a right well.

### Adding a right well feature

After adding in the right well feature, it seems that the agent does make use of it very well.
An attempt is made to maintain a right well, although the stacking ability is not as good
to allow the agent to perform a Tetris. The two moves below show the right well and an attempt
to make a Tetris. Since the stacking isn't perfect, the agent doesn't get a Tetris, but the idea
is there.

> 1. The board state has   2. Which immediately
> a right well             gets covered...
> =====================    =====================
> | | | | | |=|=|=|=| |    | | | | | |=|=| | | |
> | | | | | | | | | | |    | | | | | |=|=| | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |
> |X|X| | | | | | | | |    | | | | | | | | | | |
> | |X|X|X|X| | | | | |    | | | | | | | | | | |
> |X|X|X|X|X|X|X|X| | |    |X|X| | | | | | | | |
> |X|X|X|X|X|X|X|X| | |    | |X|X|X|X| | | | | |
> |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X| | |
> |X|X|X|X|X| |X|X|X| |    |X|X|X|X|X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X| | |
> |X|X|X| |X|X|X|X|X| |    |X|X|X|X|X| |X|X|X|X|
> |X|X|X|X|X|X|X|X|X| |    |X|X|X| |X|X|X|X|X|X|
> =====================    =====================

### Tweaking rewards for right well

Given any move, we ideally want the agent to either maintain a good board state, or clear lines.
The former means the agent should be maintaining a right well, before the latter can occur. As
such, we try to tweak the reward to incentivise maintaining a right well.

Extra rewards and features can be added later.

The end goal is to make sure that the agent stacks properly instead of trying to clear lines.
The agent has to want to only clear lines when necessary.

The reward for maintaining a right well is set to the same as a line clear.
After some training, it seems that the agent does a good job at maintaining a right well, but
at the expense of holes in the board.

> ======================================================================================
>  * Total Games: 1750
>  * Took total / per game (seconds): 311.61441588401794 / 6.232288317680359
>  * Total Steps: 55342
>  * Epsilon: 0.0001
>  * (Reward / Score / Lines Cleared)
>  * Median: 382.0 / 0.0 / 0.0
>  * Mean: 419.68 / 1958.4 / 1.64
>  * Min: 369 / 0 / 0
>  * Max: 1501 / 21600 / 23
> ======================================================================================
>  * Lines Cleared Statistics (Single / Double / Triple / Tetris):
>  * Median: 0.0 / 0.0 / 0.0 / 0.0
>  * Mean: 0.82 / 0.22 / 0.1 / 0.02
>  * Min: 0 / 0 / 0 / 0
>  * Max: 16 / 3 / 1 / 1
> ======================================================================================
> | | | | | | | | | | |
> | | | | |X|X|X|X| | |
> | | | |X|X|X| | | | |
> | | |X|X|X|X|X|X|X| |
> | | |X|X|X|X|X|X|X| |
> | |X|X|X|X|X| | |X| |
> |X|X|X|X|X|X|X|X| | |
> | |X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X| |X| |
> |X|X|X|X|X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X| | |
> |X|X| | |X|X| |X|X| |
> |X| |X|X|X|X|X|X|X| |

In an example game, only 1 line was scored, but we can see the 2 board states below. The right 
well is avoided but the stacking was bad. In the end, the agent is able to score 1 paltry line
but this seems to be the right direction. The agent just fails due to it stacking like an idiot.

> =====================    =====================
> | | | | | |=|=|=|=| |    | | | | | |=|=|=| | |
> | | | | | | | | | | |    | | | | | | | |=| | |
> | | | |X|X|X| | | | |    | | | | | | | | | | |
> | | | |X|X|X|X|X|X| |    | | | |X|X|X| | | | |
> | |X|X|X| | |X|X|X| |    | | | |X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    | |X|X|X| | |X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X| |X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X| |X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X| |X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X| |X|X|X| |    |X| |X|X|X|X|X|X|X| |
> |X| |X|X|X|X|X|X| | |    |X|X|X|X|X| |X|X|X| |
> |X|X|X|X|X|X|X|X| | |    |X| |X|X|X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    | |X|X|X|X|X|X|X|X|X|
> |X| |X| |X|X|X|X|X| |    |X| |X| |X|X|X|X|X|X|
> |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X| |X|
> =====================    =====================

Furthermore, after training, the agent sometimes performs very well, suggesting that it
is capable at times if it is lucky.

> ======================================================================================
>  * Total Games: 2000
>  * Took total / per game (seconds): 801.948778629303 / 16.03897557258606
>  * Total Steps: 79176
>  * Epsilon: 0.0001
>  * (Reward / Score / Lines Cleared)
>  * Median: 594.0 / 15120.0 / 20.5
>  * Mean: 762.86 / 19612.8 / 26.02
>  * Min: 235 / 720 / 1
>  * Max: 2116 / 81360 / 110
> ======================================================================================
>  * Lines Cleared Statistics (Single / Double / Triple / Tetris):
>  * Median: 17.5 / 1.0 / 0.0 / 0.0
>  * Mean: 21.74 / 2.08 / 0.04 / 0
>  * Min: 1 / 0 / 0 / 0
>  * Max: 98 / 9 / 1 / 0
> ======================================================================================

### Scaling down the rewards

After testing with right well reward +1, we can see that the agent stacks (decently), but is greedy
and attempts to only score Tetrises. As shown below, the only time that the agent scores, is when
there really is no other move. The long bar is thrown to the right well to prevent the agent
from losing. Since the agent does not stack perfectly, then the agent blocks the right well and
is unable to dig itself out of the situation.

During training, the agent performs pretty badly in terms of line clears, but occassionally has a
good game. The agent right now is good at maintaining a right well at the expense of board state.

> =====================    =====================    =====================
> | | | | | |=|=|=|=| |    | | | | | |=|=|=|=| |    | | | | | |=|=|=| | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | |=| | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | |X| | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | |X|X|X|X| | |X| |    | | | | | | | | |X| |    | | | | | | | | | | |
> | | |X|X|X|X| |X|X| |    |X|X| |X|X| |X| |X| |    | | | | | | | | |X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X| |X|X| |X| |X| |
> |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X| | |    | |X|X|X|X|X| |X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    | |X|X|X|X|X| |X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X| | |    |X|X|X|X|X|X|X|X| | |
> |X|X|X|X|X|X|X| |X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X| | |
> |X|X|X| |X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X| |X|X|X|X|X|X| |    |X|X|X|X|X|X|X| |X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X| |X|X|X|X|X| |    |X|X|X|X|X|X|X| |X|X|
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X| |X|X|X|X|X|X|
> |X|X|X|X| |X|X|X|X| |    |X|X| |X|X|X|X|X|X| |    |X|X| |X|X|X|X|X|X|X|
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X| |X|X|X|X|X|    |X|X|X|X| |X|X|X|X|X|
> =====================    =====================    =====================

## Re-evaluating Features

As mentioned previously, the agent needs to stack efficiently and maintain a right well. While
it is capable of doing the latter, the former is preventing the agent from being good. Hence,
we need to re-evaluate the features to see what can be done for the agent.

### Changing Transitions and Height Features

The features can be categorised into hole, height and right well related features. Perhaps by
cutting down on some features and introducing new ones, we can make the agent stack better.

For the hole features (holes / transitions / bumpiness), there is an overlap between transitions
and holes. As such, we removed column transitions. Generally, the agent should aim to minimise
these features.

The height features (board / landing height) are removed. After consideration, the agent doesn't
need to care about height as much, as the agent will need to stack higher if it cannot clear lines
efficiently. These features are important for conventional Tetris projects as they aim to clear
many lines, and keeping a low board is important.

A new right well related feature (lines_ready_to_clear) is added. Hopefully, this encourages better
stacking.

After training, it seemed like the agent generally does two things:

> Maintain a right well, stack badly, and lose the game
> Be unable to maintain a right well, never re-open it and continue scoring

Perhaps removing the rewards for a right well would be good, as it seems to produce games where
the agent does spectacularly bad or good.

> ======================================================================================
>  * Total Games: 1850
>  * Took total / per game (seconds): 823.3241136074066 / 16.46648227214813
>  * Total Steps: 71310
>  * Epsilon: 0.0001
>  * (Reward / Score / Lines Cleared)
>  * Median: 6695.0 / 27540.0 / 36.0
>  * Mean: 15026.22 / 26913.6 / 32.9
>  * Min: 59 / 0 / 0
>  * Max: 164546 / 114120 / 143
> ======================================================================================
>  * Lines Cleared Statistics (Single / Double / Triple / Tetris):
>  * Median: 28.5 / 2.5 / 0.0 / 0.0
>  * Mean: 26.68 / 2.42 / 0.38 / 0.06
>  * Min: 0 / 0 / 0 / 0
>  * Max: 126 / 7 / 5 / 1
> ======================================================================================
> | | | | | | |=|=| | |
> | | | | | |=|=|X| | |
> | | | | | |X|X|X|X| |
> | | | | |X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X| |X|X|X|X| | |
> |X|X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X| | | |
> | |X|X|X|X| |X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X| |X| |X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X| |X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X| |X|X|X|X|X|X|X| |
> |X|X|X| | |X|X|X|X| |

### Remove Rewards for Right Well

It seems like giving rewards for maintaining a right well causes more problems than it fixes.
As such, it is removed, and we will continue trying to work on features rather than tweak
rewards.

An example board state with pretty good stacking is shown below, before it gets messed up
due to a triple that was scored.

> | | | | | |=|=|=|=| |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> |X| | | | | | | | | |
> |X|X| | | | | | | | |
> | |X| | | | | | | | |
> |X|X|X| | | | | | | |
> |X|X|X| | | | | | | |
> |X|X|X|X|X|X|X| | | |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X| | |X|X|X|X| |

Seems like we'll just stick to not giving rewards for a right well.

The general strategy that the agent should use when making a move:

1. Don't make holes unless necessary
2. Stack within the first 9 columns evenly
3. If clearing lines, clear as many lines as possible

And how the features work in these strategies:

1. Holes / transitions
2. Right well / bumpiness / landing height / board height / lines ready to clear
3. Lines cleared / right well / lines ready to clear

Changed lines ready to clear feature to include only the lines that are affected by the move 
(similar to lines cleared). As clearing lines reduces the number of lines ready to clear, it is 
counter-intuitive.

New feature:
Valleys (there is no actual term for this) - A column that is surrounded by other columns whose 
height is taller than it by 3 or more. This is something to avoid as the only way to fill
in this without making a hole, is to use an I piece (which is something that doesn't come)
that often.

## Reward for less holes / penalty for holes

Actively disincentivise moves that create holes. There will be situations where holes are mandatory.

When rewards were given for maintaining a right well, the agent makes sure it does so at the expense
of board states. Hence, rewards for holes is tested to see if it is good enough to force the agent
to stack well.

> ======================================================================================
>  * Total Games: 2000
>  * Took total / per game (seconds): 1963.1788094043732 / 39.26357618808746
>  * Total Steps: 161671
>  * Epsilon: 0.0001
>  * (Reward / Score / Lines Cleared)
>  * Median: 18572.755000000005 / 61740.0 / 82.5
>  * Mean: 26791.951399999994 / 66232.8 / 84.42
>  * Min: 2830.1000000000004 / 14760 / 20
>  * Max: 221211.8 / 130680 / 169
> ======================================================================================
>  * Lines Cleared Statistics (Single / Double / Triple / Tetris):
>  * Median: 69.5 / 5.0 / 0.0 / 0.0
>  * Mean: 71.14 / 5.58 / 0.6 / 0.08
>  * Min: 18 / 1 / 0 / 0
>  * Max: 149 / 13 / 4 / 2
> ======================================================================================

With this, we have managed to return to a rather stable agent. However, as can still be seen,
the majority of line clears are still single line clears. That said, it is not 100% indicative of
what the result will be. The main thing to look out for, is how the agent maintains a proper board.

We now add in rewards for 3 factors:
1. Presence of a right well
2. Presence of lines that are ready to clear
3. Number of line clears

And tweaked the features as:
board_height, bumpiness, holes, holes_created
lines_cleared, lines_ready_to_clear, row_transitions, col_transitions, right_well

Along with changing the layers used:
tf.keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
tf.keras.layers.Dense(64, activation='relu'),
tf.keras.layers.Dense(32, activation='relu'),
tf.keras.layers.Dense(1, activation='linear'),

Finally with some minor changes to the learning (add in move data in experience buffer).

With now an agent that is pretty good?

> ======================================================================================
>  * Total Games: 2150
>  * Took total / per game (seconds): 26940.668691396713 / 538.8133738279342
>  * Total Steps: 408542
>  * Epsilon: 0
>  * (Reward / Score / Lines Cleared)
>  * Median: 49019.0 / 540180.0 / 669.5
>  * Mean: 112330.38 / 1264629.6 / 1487.48
>  * Min: 2818 / 41760 / 51
>  * Max: 600341 / 6754320 / 8077
> ======================================================================================
>  * Lines Cleared Statistics (Single / Double / Triple / Tetris):
>  * Median: 511.0 / 57.0 / 8.5 / 2.0
>  * Mean: 1152.78 / 131 / 17.94 / 4.72
>  * Min: 38 / 5 / 0 / 0
>  * Max: 6281 / 724 / 101 / 25
> ======================================================================================

Amazing progress, but that's an unreasonable number of lines to clear in NES Tetris, so
we'll prematurely end the game at 300 line clears to speed things up, and to see if the
agent can score better.

> =====================
> | | | | | |=|=|=| | |
> | | | | | | |=| | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> | | | | | | | | | | |
> |X| | | | | | | | | |
> |X|X| | | | | | | |X|
> |X|X| | | | | | | |X|
> |X|X| | | | | | | |X|
> |X|X|X|X|X|X|X| | |X|
> |X|X|X|X| |X|X|X|X|X|
> |X|X|X|X|X|X|X| |X|X|
> =====================

This is a sample game at 300 line clears. The board may not be ideal, but it definitely
is performing pretty well compared to previous attempts. This is after 2150 games, which 
is barely after the agent stops exploring. (Performance increases exponentially after 
2000 games, but we should expect it to not maintain it after a while)

We will continue training but cap the number of line clears to see how well the agent
performs with even more training. This will definitely limit the performance at some
point, but then it'll mean that the agent will need to optimize instead of trying
to blindly score.

## Capping The game

After capping the game at 300 lines, we observe that during non-exploratory training, the
performance tends to increase before sharply dropping and increasing again.

> 2100 games               2300 games               2450 games               2600 games
> =====================    =====================    =====================    =====================
> | | | | | |=|=|=| | |    | | | | | | |X| | | |    | | | | | |=|=|=| | |    | | | | | | | | |X| |
> | | | | | |=|X|X| | |    | | | | | |X|X|X|X| |    | | | | | | |=| | | |    | | | | | | | |X|X| |
> | | | | | |X|X|X|X| |    | | |X|X| |X|X|X|X|X|    | | | | | |X|X|X|X| |    | | | | | |X|X|X|X| |
> | | | |X|X|X|X|X|X| |    | | |X|X|X| |X|X|X|X|    | | |X|X|X|X|X|X|X| |    | | | |X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X| | | |    | |X|X|X|X|X|X|X|X| |    |X|X| |X|X|X|X|X|X| |
> |X|X|X|X|X|X|X| |X|X|    | |X|X|X| | | | | | |    | |X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X|X|    | | | |X| | | | | | |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X| |X|X|X|X|X|X|    | | | |X|X| | | | | |    | |X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X| |X|X|X|X|X|X|    | | | |X|X| | | | | |    |X|X|X|X|X|X|X| |X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X| |X|X|X|X|X|X|    | | | | |X|X| | | | |    |X| |X|X|X|X|X|X|X| |    |X|X|X|X|X| |X|X| | |
> | |X|X|X|X|X|X|X|X|X|    | | | | | |X|X| | | |    |X|X|X|X|X| |X|X|X|X|    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X| |X|X|X|X|    | | | | | | |X|X| | |    |X|X|X|X| |X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X| |X|    | |X| | | | |X|X| | |    |X|X|X|X| |X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    | |X| | | | | |X|X| |    |X|X|X|X|X|X|X|X| |X|    |X|X|X|X|X|X|X|X|X| |
> |X| |X|X|X|X|X|X|X|X|    |X|X|X| | | | | |X|X|    | |X|X|X|X|X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |
> |X| | |X|X|X|X|X|X|X|    |X|X| | | | | | |X| |    |X|X|X| |X|X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X| |X|X|X|X|X|    | |X|X| | | | | |X|X|    |X|X|X|X|X|X|X| |X|X|    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X| |X|X|    |X|X| |X|X|X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X| |X|X|X|X|X|X|X|X|    | |X|X|X|X|X|X|X|X|X|    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X| |X|X|X| |
> | |X|X|X|X|X|X|X|X|X|    | |X|X|X|X| |X|X|X|X|    |X|X|X|X|X|X|X|X|X| |    | |X|X|X|X|X|X|X|X| |
> =====================    =====================    =====================    =====================

There is a sudden drop in performance at around 2250 games, before the agent starts playing weirdly
at 2300 games. Although the performance drops again after 2500 games, the sample game from 2600
episodes demonstrates what the agent can be capable of.

Due to a mistake in the code, the agent was stopped only if it reached exactly 300 lines. This
may cause some difference in training than intended (and we will train again to make sure).

During training, it seems that the agent improves steadily, before experiencing a sharp drop before 
rising again. The overall strategy employed is not guaranteed to be perfect even with high scores.

The rise / drop during training seems to occur every 400-500 episodes.

The current 'best' agent to be used is taken at 2700 episodes. The agent stacks pretty well, 
lasting past 300 lines easily. The agent tends to score somewhat efficiently, where half of the 
line clears are not single lines. The agent doesn't perfectly keep
a right well, although it is able to dig itself out (slowly) from any board state that it creates.

The main thing to 

Sample Game Scores:
> Score: 368640
09:02:14,608 root INFO Lines cleared: 300
09:02:14,608 root INFO ===============================================================
09:02:14,608 root INFO Lines cleared: 
09:02:14,608 root INFO Single: 172
09:02:14,609 root INFO Double: 40
09:02:14,609 root INFO Triple: 8
09:02:14,609 root INFO Tetris: 6

## Explicit Moves and Stop Making Holes

One thing that we can do, is to explicity make the agent perform certain moves (like making a 
Tetris if possible). This can be extended to prevent the agent from making potentially stupid
moves.

In this way, the agent has several action groups that it can do:

1. Stack but not touch the well
2. Burn lines
3. Tetris

One other thing to do is to actively prevent the agent from making holes. While this is not ideal,
moves generated can be separated into ones that make holes, and ones that don't. There are situations
where holes have to be made, and we will thus use the group of moves that generate holes.

During state generation for moves, they are split into 3 different groups (low / mid / high) of
priorities, where the higher priority groups are used. The idea is to have some form of forced
control over moves, to ensure that the agent does what it should do.

We will now train agents based on this logic.

2650 is good.

Agent is capable of stacking efficiently, although it doesn't score the best (likes to score doubles 
and triples). Agent can maintain a right well and clean up messy board states to a competent degree.

Perhaps a more robust system could be put in place to prevent this.

## Trying to Clear Holes Effectively

Now that the agent can stack well, the next thing is to clear holes. The most important thing is to 
clear holes once they are made, else the board will keep piling up and the hole will take more moves 
to clear.

And the hole-related features will be based on the filled columns instead of all.

Hence, we introduce a new feature: 

> Holes Covered - How many holes does a move end up affecting / adding on more cells

The idea behind this is to try to clear the holes, or avoid adding on more filled cells as they 
will only make the holes harder to clear.

Another feature was explored:

> Overhang Height - How many cells are filled above a hole.

This feature calculates how many extra cells (across all holes) are filled.

However, after testing, this seems to be rather problematic and is not used.

## Giving Leeway to the Right Well

> We now give some leeway to the right well and hole related features for the 
rightmost column. The idea is to simulate the ability to use the right well
as a temporary place for 'bad' moves so that we can burn off lines.

In this way, we can potentially avoid disastrous moves by making holes in other columns
(presumably well stacked).

Below, we can see the effects of burning. Note that if the S piece was placed anywhere else, it would
be rather problematic to clear, even for experienced players.

> | | | | | | |=|=| | |    | | | | | |=|=|=|=| |    | | | | | |=|=|=| | |    | | | | | |=|=|=| | |
> | | | | | |=|=| | | |    | | | | | | | | | | |    | | | | | | | |=| | |    | | | | | |=| | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | | | | | |X| | |    | | | | | | | | | | |
> | | | | | | | | | | |    | | | | | | | | | | |    | | | |X| | | |X|X| |    | | | | | | | |X| | |
> | | | | | | | | | | |    | | | | | | | | | | |    |X| | |X|X|X|X|X|X| |    | | | |X| | | |X|X| |
> | | | | | | | | | | |    | | | | | | | | |X|X|    |X| | |X|X|X|X|X|X|X|    |X| | |X|X|X|X|X|X| |
> | | | | | | | | | | |    | | | | | | | |X|X| |    |X| |X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | | | | | |X|X|X|X| |    | | | | | |X|X|X|X| |    |X| |X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | | | |X| |X|X|X|X| |    | | | |X| |X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | | |X|X| |X|X|X|X| |    | | |X|X| |X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> | | |X|X|X|X|X|X|X| |    | | |X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |

Issues:

Generally tops off with a good board, as it does not clear enough lines on time

Fails to burn and ends up with bad holes

Makes too steep valleys and can't plug them with enough I pieces and clear lines

> | | | | | |=|=| | | |
> | | | | | |=|=| | | |
> | | | | |X|X|X| | |X|
> | | | | |X|X|X| |X|X|
> | | |X|X|X|X|X| |X| |
> | | |X|X|X|X|X| |X| |
> | |X|X|X|X|X|X| |X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> | |X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |
> |X|X|X|X|X|X|X|X|X| |

Move priorities:

1. Makes Tetris
2. Clears holes (needs line clears)
3. Clears lines (if board is high)
4. Does not make holes and valleys

New Feature:
Fit - How many positions can the next piece fit on the board, without making holes.

Ideally, there should at least be more positions that the next piece can fit in.

This is introduced to tackle the problem of topping off due to not being able to place the next
piece well. While the agent is capable of stacking the board properly now, there are issues
where the agent just isnt able to fit everything nicely

### Changes to Implement

Change the valley system to be more robust: Split into 2 features: number of valleys and height
of valleys. This is needed to make sure that valleys are not created AND not deepened.

Change holes covered to only be for the highest hole. This is so that we can tackle multiple holes.
When there is multiple holes, we need to clear the one at the highest, before we can clear the other ones.

In addition to a right well, make sure that the third most right column is higher than the second by 1.
This is a very useful corner to have, as it allows for the easy burning of S, Z, O, L, J pieces. T
pieces can be burned, leaving behind one cell of overhang, which is not hard to burn off again.

The main issue is that it stacks well, but stacks high and eventually can top off due to overhangs.
If the agent doesn't end up with a bad piece sequence and make too many valleys, then it can perform
very well. But, it struggles to deal with 2 holes at once. The 'holes covered' feature was implemented
to prevent stacking onto holes as it means that we need to clear more lines. However, if there are 2 holes
(or more), then it becomes more important to clear the hole at a higher height, than to avoid
stacking on other holes.

If anything, if holes are to be made, they should be done at the right well. It is easier to clear holes
made at the right well (since they mean that line clears will be at the highest row possible).

For reference, the agent can achieve 60% Tetris rate, which is really good (slightly above 60% rate is
stable enough for a max out score of 9999999).

16/9:
Agent stacks well, but dies due to topping off (stacks in the middle and dies)

This mainly happens as the agent does not give itself space to play.

After changing the priority logic, agent now stacks very well, but tops off due to not clearing
enough lines.

Issue: By move priority, only the I piece can fix the left side of the board.
L or J piece can cover one side, but leave a valley on the other.

This is a big issue as the agent does not seem to stack super efficiently.

| | | | | |=|=|=|=| |    | | | | | |=|=|=| | |
| | | | | | | | | | |    | | | | | | |=| | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | |X| | | | | |    | | | | |X|X|X|X|X| |
| | | |X|X|X|X|X|X|X|    | | | |X|X|X|X|X|X|X|
| | | |X|X|X|X|X|X|X|    | | | |X|X|X|X|X|X|X|
| |X| |X|X|X|X|X|X| |    | |X| |X|X|X|X|X|X| |
| |X| |X|X|X|X|X|X| |    | |X| |X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |

Bumpiness is normally used to differentiate between boards. However, since it is the absolute
difference, it cannot differentiate between these 2 boards:

| | | | | |=|=|=|=| |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | | | | | | | |    | | | | | | | | | | |
| | | | |X| | | | | |    | | | | |X| | | | | |
| | | |X|X|X|X|X|X|X|    |X| | |X|X|X|X|X|X|X|
| | | |X|X|X|X|X|X|X|    |X| | |X|X|X|X|X|X|X|
| |X| |X|X|X|X|X|X| |    |X|X| |X|X|X|X|X|X| |
| |X| |X|X|X|X|X|X| |    |X|X| |X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |
|X|X|X|X|X|X|X|X|X| |    |X|X|X|X|X|X|X|X|X| |

Hence, we can try to define a new feature:

height_below_median_height - squared difference in height of columns below the median height






















# Changelog

13/8/21

1. Tidy up repo and make things work
> Previously, the repo was in a mess due to it originally being run in Colab and the code was 
> hastily ported over. Repo is functional but will need to be tidied up more.

2. Removed hard_drop_value from features
> Redundant feature that was originally added in to make each move set a piece (by providing
> this value in the features and then referencing this feature). This is similar to landing height
> and also provides an annoyance in the future when normalizing data. Hence, this is removed and 
> instead we directly modify the move for hard drop as python passes args by reference.

3. Edited training and game statistics
> More relevant information will be displayed during training and running the agent. Additionally,
> a sample game will be played after each training interval.

4. Separated scoring and reward system
> Originally, the reward system follows the NES Tetris scoring system, but this produced a behavior
> of incentivising single line clears due to the sheer reward difference (1 for no clears vs 721 for
> 1 line). This has been set to 1 / 10 / 100 / 1000 * level for the time being to test out.

5. Normalizing inputs
> Normalizing would help to standardize the features, especially since some grow large. 0 to 1 
> normalization would be done.

1/9/21

1. Implement tucks and spins
> Tucks and spins are added to make the agent play better. These moves only occur when the piece
> is supposed to be set. There are cases where tucks can occur before the piece is set (when it
> is falling halfway), but that vastly increases the search space that the agent can do, over
> an already inflated search space, hence we are not doing that.

2. Updated the notebook
> Updated the notebook with the current code. The notebook does not rely on external scripts, and
> code will need to be ported over without referencing other local scripts or config. Verified on
> Colab.

3. Changed features and rewards
> Changed features and rewards as per the rough notes, in order to experiment and play around to
> get a better performing agent.

4. Add some plots for training
> Added some simple graph plots of the data to visualize lines cleared, rewards and score.

# Pending Changes


## Stuff to Implement

1. Proper frame drop delay
> At the moment, the moves assume that pieces fall one cell per move (left / right / rotate). A proper
> tick system is in place, but the calculation of how much a piece falls per move is not done due to
> computation time and make the game easier for the agent while the agent is being tweaked.

2. Level system
> The level system is in place, but does nothing as 1. is not being used at the moment.

3. Actual rendered game
> Simulate the game in a proper application instead of printing to the cmd line.

4. Plot the training statistics or use Tensorboard
> Maybe we can figure out Tensorboard.

5. Save training so that we can stop and restart again
> Save the experience buffer and have a way to load it, by setting an option in the config.