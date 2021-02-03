# gym environment that follows gym interface"""
class NesTetrisEnv(gym.Env):
  metadata = {'render.modes': ['console']}

  def __init__(self):
    super(NesTetrisEnv, self).__init__()
    # Define action and observation space

    # left / right / down / rotate clockwise / anti-clockwise
    self.action_space = spaces.Discrete(ACTION_SIZE)

    # [lines_cleared, wells, board_height, bumpiness, holes, coord_x_new, coord_y_new, coord_x, coord_y, piece_id, piece_rotation]
    self.observation_space = spaces.Discrete(STATE_SIZE)

  # Execute one time step within the environment
  # action takes in move data (x, y, rotation)
  def step(self, action):
    # run the action
    self.board.move_piece(action, verbose = False)

    # return available moves with state info
    moves = self.board.get_available_moves_state_info()

    done = self.board.is_game_over()

    reward = 1
    reward += self.board.get_score_increase(self.board.get_lines_cleared_recently())
    if done:
      reward -= 5

    return np.array(moves), reward, done, {}
    
  # reset the state of the environment to an initial state and return initial observation
  def reset(self, verbose = False):
    self.board = Board(BOARD_HEIGHT, BOARD_WIDTH)
    self.board.place_new_piece()
    
    if verbose:
      self.board.render_board()
      self.board.print_current_piece_state()

    return np.array(self.board.get_available_moves_state_info())
    
  # Render the environment to the screen
  def render(self, mode='human', close=False):
    self.board.render_board()
	