# General Training Behavior

The agent is trained for 2000 episodes at 50 episode intervals, and the epsilon starts at 0.95
and decays linearly until 1500 episodes. Agent performs badly until about 1000 episodes as
expected, and then it should start improving from there.

The trend to observe in training would be of course, exponential improvement starting at around
1500 episodes. Improvements will plateau off eventually.

Expected training time would be around 4 to 5 hours.

## Performance

The agent performs decently, being able to clear around 50 lines on average.

However, agent fails primarily due to it being unable to clear certain lines, and thus
will slowly build up the board and top off eventually. Stacking ability is questionable
as the agent tends to prefer to clear lines at the expense of board state.

The board tends to have some holes, showing that the agent has some difficulty in stacking
super efficiently. For some odd reason, the agent sometimes stacks a well on the left side.

Example 'good' game:
> Score: 71370
> Lines cleared:96
> =========================
> Lines cleared:
> Single: 84
> Double: 6
> Triple: 0
> Tetris: 0

As can be seen, the agent tends to clear single lines instead of opting to make Tetrises.

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

# Pending Changes


2. Normalizing inputs
> Normalizing would help to standardize the features, especially since some grow large. 0 to 1 
> normalization would be done.

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