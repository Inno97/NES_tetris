# gym environment that follows gym interface
import gym
import numpy as np

from board import Board
import constants

class NesTetrisEnv(gym.Env):
  metadata = {'render.modes': ['console']}

  def __init__(self):
    super(NesTetrisEnv, self).__init__()
    self.action_space = gym.spaces.Discrete(constants.ACTION_SIZE)
    self.observation_space = gym.spaces.Discrete(constants.STATE_SIZE)

  def step(self, action, verbose=False):
    '''Executes one time step within the environment.
    
    Args:
      action (tuple): Tuple of (x, y, rotation).
    '''
    self.board.move_piece(action, verbose=verbose)
    moves = self.board.get_available_moves_state_info()
    done = self.board.is_game_over()

    reward = 1
    #reward += self.board.get_reward_holes()
    reward += self.board.update_and_get_reward_holes()
    reward += self.board.get_reward_increase(self.board.get_lines_cleared_recently())
    if done:
      reward -= 5

    return np.array(moves), reward, done, {}
    
  def reset(self, verbose=False):
    '''Reset the state of the environment to an initial state and return initial observation
    '''
    self.board = Board(constants.BOARD_HEIGHT, constants.BOARD_WIDTH)
    self.board.place_new_piece()
    
    if verbose:
      self.board.render_board()
      self.board.print_current_piece_state()

    return np.array(self.board.get_available_moves_state_info())
    
  def render(self, mode='human', close=False):
    '''Render the environment to the screen
    '''
    self.board.render_board()
	