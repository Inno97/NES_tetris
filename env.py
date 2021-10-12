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

    self.__feature_lines_cleared = 0.0
    self.__feature_lines_ready_to_clear = 0.0
    self.__feature_board_height = 0.0
    self.__feature_height_below_median_height = 0.0
    self.__feature_fit = 0.0
    self.__feature_pieces_fittable = 0.0
    self.__feature_bumpiness = 0.0
    self.__feature_valleys = 0.0
    self.__feature_valley_depth = 0.0
    self.__feature_max_height_diff = 0.0
    self.__feature_holes = 0.0
    self.__feature_holes_created = 0.0
    self.__feature_holes_covered = 0.0
    self.__feature_row_transitions = 0.0
    self.__feature_column_transitions = 0.0
    self.__feature_right_well = 0.0

  def step(self, action, verbose=False):
    '''Executes one time step within the environment.
    
    Args:
      action (tuple): Tuple of (x, y, rotation).
    '''
    self.board.move_piece(action, verbose=verbose)
    moves = self.board.get_available_moves_state_info()
    done = self.board.is_game_over()

    reward = 1

    self.board.update_max_height_diff()
    reward += self.board.update_and_get_reward_holes()
    reward += self.board.get_reward_increase(self.board.get_lines_cleared_recently())
    reward += self.board.get_reward_increase(self.board.get_lines_ready_to_clear_recently())

    reward += self.__feature_fit
    reward += self.__feature_pieces_fittable

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

  def update_state(self, state):
    """Updates the state of the board from the state given by the move.
    """
    self.__feature_lines_cleared = state[0]
    self.__feature_lines_ready_to_clear = state[1]
    self.__feature_board_height = state[2]
    self.__feature_height_below_median_height = state[3]
    self.__feature_fit = state[4]
    self.__feature_pieces_fittable = state[5]
    self.__feature_bumpiness = state[6]
    self.__feature_valleys = state[7]
    self.__feature_valley_depth = state[8]
    self.__feature_max_height_diff = state[9]
    self.__feature_holes = state[10]
    self.__feature_holes_created = state[11]
    self.__feature_holes_covered = state[12]
    self.__feature_row_transitions = state[13]
    self.__feature_column_transitions = state[14]
    self.__feature_right_well = state[15]
