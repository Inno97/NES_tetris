# the board contains the playing field
import random, yaml, copy, statistics
from tensorflow.python.ops.gen_array_ops import const
import constants, shape
from piece import Piece
from logger import get_logger

log = get_logger()
config = yaml.safe_load(open('config.yml'))

class Board:
  """The Class representing a NES Tetris board.
  """
  def __init__(self, height, width):
    """
    Args:
      height (int): The height of the board.
      width (int): The width of the board.
    """
    self.height = height
    self.width = width

    self.pieces_table = [[0 for i in range(width)] for j in range(height)]

    self.piece = None
    self.piece_next = None

    self.ticks = 0 # the current frame count
    self.level = config['SETTINGS']['STARTING_LEVEL']
    self.move_count = 0
    self.piece_count = 0
    self.line_clears = 0
    self.line_clears_for_next_level = constants.LINES_FIRST_LEVEL_JUMP[0][self.level]

    self.line_clear_single = 0
    self.line_clear_double = 0
    self.line_clear_triple = 0
    self.line_clear_tetris = 0

    self.scoring_system = self.generate_scoring_system()
    self.reward_system = self.generate_reward_system()
    self.score = 0
    self.game_over = False

    # NOTE: unused as holding pieces are not allowed in NES tetris, but can be configured later on
    self.piece_holding = None
    self.piece_last = None
    self.can_hold = False

    # generate the random bag of pieces
    self.bag = self.generate_bag()
    self.piece = self.create_piece()
    self.piece_next = self.create_piece()

    self.holes = 0
    self.valleys = 0
    self.right_well = 1
    self.max_height_diff = 1

  def generate_bag(self):
    """Returns a List of Piece objects.

    NOTE: If IS_TRUE_RANDOM_PIECES is set to True, then the bag is randomly generated, 
    otherwise it is guaranteed to have all 7 unique pieces returned.
    """
    random_shapes = list(shape.SHAPES)
    random.shuffle(random_shapes)

    bag = []
    # generate bag based on whether true random or fixed
    if config['SETTINGS']['IS_TRUE_RANDOM_PIECES']:
      for i in range(7):
        id = random_shapes[random.randint(0, 6)].get_id()
        bag.append(Piece(id))
    else:
      for shapes in random_shapes:
        bag.append(Piece(shapes.get_id()))

    return bag

  def create_piece(self):
    """Returns the first piece in the List representing the bag.
    If the bag is non-existent, then a new one is created.
    """
    if not self.bag:
      self.bag = self.generate_bag()
    return self.bag.pop()

  def place_new_piece(self):
    """Put the new piece on the board and then update the next piece.
    """
    self.piece = self.piece_next
    self.piece_next = self.create_piece()

    # place the piece in the middle of the board
    self.piece.move(int(self.width / 2), 0 - constants.PIECE_Y_OFFSET_INITIAL[self.piece.get_id()], 0)

    if not self.update_board() or self.line_clears >= 100:
      self.game_over = True
      return

    self.piece_count += 1
    self.ticks = 0

  def move_piece(self, move, verbose = False):
    """Moves the piece, assumes that move is legal and expects a tuple of (x, y, rotation).
    The move is assumed to be legal and checked beforehand.

    Args:
      move (tuple): A tuple of (x, y, rotation) representing the movement in x / y dimension
      and the rotation of the piece.
      verbose (Boolean): Prints the current piece state and render the board if True.
    """
    self.get_current_piece().move(move[0], move[1], move[2])
    self.update_board()
    self.lines_cleared_recently = 0

    if self.is_piece_set():
      self.set_piece()
      self.lines_cleared_recently = self.update_line_clear()
      self.update_score(self.lines_cleared_recently)      
      self.place_new_piece()

      if verbose:
        log.info('========================================')
        self.render_board()
    elif verbose:
      self.print_current_piece_state()
      self.render_board()

  def set_piece(self):
    """Sets the piece on the board.
    It is assumed that piece can be set and is checked beforehand.
    """
    for coord in self.piece.get_coords():
      self.pieces_table[coord[0]][coord[1]] = self.piece.get_id()

  def force_set_next_piece(self):
    """Manually sets the next piece, only done when the next piece has no 
    Available moves, and cannot be set because of this
    """
    if self.is_piece_set():
      self.set_piece()

  def update_board(self):
    """Updates the current piece's coords on the board, and returns True if successful.
    """
    try:
      # remove the old piece from the board
      for coord in self.piece.get_prev_coords():
        if self.pieces_table[coord[0]][coord[1]] == constants.PIECE_ID_CURRENT:
          self.pieces_table[coord[0]][coord[1]] = constants.PIECE_ID_EMPTY
        else:
          #self.reset_move(self.piece.get_coords(), self.piece.get_prev_coords())
          return False

      # add the new position of the piece
      for coord in self.piece.get_coords():
        if self.pieces_table[coord[0]][coord[1]] > constants.PIECE_ID_EMPTY and \
          self.pieces_table[coord[0]][coord[1]] < constants.PIECE_ID_CURRENT:
          self.reset_move(self.piece.get_coords(), self.piece.get_prev_coords())
          return False
        else:
          self.pieces_table[coord[0]][coord[1]] = constants.PIECE_ID_CURRENT

      self.move_count += 1
      return True
    except IndexError:
      log.warn('Out of bounds when updating board')
      log.warn(self.piece.get_coords())

  def update_line_clear(self):
    """Runs through the board, clears any filled lines and returns how many that were cleared
    """
    lines_to_clear = [] # keep track of previous lines cleared to prevent double-count
    lines_cleared = []

    # run through all coords of the current piece to get the lines to clear
    for coord in self.piece.get_coords():
      if self.is_line_clear(coord[0]) and coord[0] not in lines_to_clear:
        lines_to_clear.append(coord[0])

    # clear the lines
    lines_to_clear.reverse()
    for line in lines_to_clear:
      lines_cleared.append(self.clear_line(line))

    no_of_lines_cleared = len(lines_to_clear)

    # add back lines
    self.add_empty_lines(no_of_lines_cleared)

    self.line_clears += no_of_lines_cleared

    if no_of_lines_cleared == 1:
      self.line_clear_single += 1
    elif no_of_lines_cleared == 2:
      self.line_clear_double += 1
    elif no_of_lines_cleared == 3:
      self.line_clear_triple += 1
    elif no_of_lines_cleared == 4:
      self.line_clear_tetris += 1

    return len(lines_to_clear)

  def clear_line(self, line_number):
    """Clears the specified line.
    """
    return self.pieces_table.pop(line_number)

  def add_empty_lines(self, lines_to_add):
    """Adds an empty line at the top of the board.
    """
    for i in range(lines_to_add):
      self.pieces_table.insert(0, [0 for i in range(self.width)])

  def update_level(self):
    """Checks and updates level according to line clears.
    """
    if self.lines >= self.line_clears_for_next_level:
      self.level += 1
      self.line_clears_for_next_level += 10

  def reset_move(self, coords, prev_coords):
    """Resets the previous move made, because it was illegal and executed halfway
    This does not revert any overwritten cells that were previously occupied by a piece
    """
    # revert new state
    for coord in coords:
      if self.pieces_table[coord[0]][coord[1]] == constants.PIECE_ID_CURRENT:
        self.pieces_table[coord[0]][coord[1]] = constants.PIECE_ID_EMPTY

    # restore previous state
    for coords in prev_coords:
      self.pieces_table[coord[0]][coord[1]] = constants.PIECE_ID_CURRENT

  def update_frame_count(self):
    """Update frame tick count and move the piece down.

    If 'IS_DAS_ON' is True in the config, then the first move will receive DAS delay.
    This assumes that the move only gets the delay at the first instance.
    """
    if config['BEHAVIOR']['IS_DAS_ON'] and self.ticks == 0:
      self.ticks += constants.DAS_DELAY
    self.ticks += constants.FRAME_DELAY

  def update_score(self, lines_cleared):
    """pdates the score based on the level
    """
    self.score += self.scoring_system[lines_cleared]

  def generate_scoring_system(self):
    """Returns a list of points given for line clears for the current level
    """
    return [0, (40 * self.level), (100 * self.level), (300 * self.level), (1200 * self.level)]

  def generate_reward_system(self):
    """Returns a list of points given for line clears for the current level
    """
    return [0, 10, 100, 10000, 1000000]

  def render_board(self):
    """Prints out the entire board
    """
    for i in range(self.height):
      line_to_print = "|"
      for j in range(self.width):
        id = self.pieces_table[i][j]
        if id == constants.PIECE_ID_EMPTY:
          line_to_print += " |"
        elif id == constants.PIECE_ID_CURRENT:
          line_to_print += "=|"
        else:
          line_to_print += "X|"
      
      print(line_to_print)

  def render_given_board(self, board):
    """Prints out the entire board that is given as args.
    """
    for i in range(len(board)):
      line_to_print = "|"
      for j in range(len(board[0])):
        id = board[i][j]
        if id == constants.PIECE_ID_EMPTY:
          line_to_print += " |"
        elif id == constants.PIECE_ID_CURRENT:
          line_to_print += "=|"
        else:
          line_to_print += "X|"
      
      log.info(line_to_print)

  def render_move(self, piece, move, verbose=False):
    """Prints out the board based off a move, to preview.
    """
    board = copy.deepcopy(self.pieces_table)

    log.info('before')
    # remove the original coordinates
    for coord in piece.get_coords():
      log.info(coord)
      board[coord[0]][coord[1]] = constants.PIECE_ID_EMPTY

    coords = piece.simulate_move(move[0], move[1], move[2])

    if verbose:
      piece.print_simulated_move(move[0], move[1], move[2])

    log.info('after')

    for coord in coords:
      log.info(coord)
      board[coord[0]][coord[1]] = piece.get_id()

    self.render_given_board(board)

  def print_current_piece_state(self):
    self.piece.print_info()

  def print_next_piece_state(self):
    self.piece_next.print_info()

  def is_valid_move(self, piece, move, board, verbose=False):
    """Returns True if the move is legal, False otherwise.
    """
    # ignore the elusive O spin
    if piece.get_id == 2 and move[2] != 0:
      return False

    coords = piece.simulate_move(move[0], move[1], move[2])
    if verbose:
      piece.print_simulated_move(move[0], move[1], move[2])
    for coord in coords:
      x = coord[1]
      y = coord[0]

      if x < 0 or x >= self.width or y < 0 or y >= self.height:
        return False
      if board[y][x] != 0 and board[y][x] != 8:
        return False

    return True

  def is_piece_set(self):
    """Returns if the piece should be set into the board
    Piece is considered set if it touches another piece on the board
    """
    for coord in self.piece.get_coords():
      if coord[0] == (self.height - 1):
        return True
      elif self.pieces_table[coord[0] + 1][coord[1]] > constants.PIECE_ID_EMPTY and \
        self.pieces_table[coord[0] + 1][coord[1]] < constants.PIECE_ID_CURRENT:
        return True

    return False

  def is_game_over(self):
    """Returns if the game is over.
    """
    return self.game_over

  def is_natural_drop(self):
    """Returns whether the piece should drop on its own and reset tick count if true.
    """
    if self.ticks > constants.FRAMES_PER_GRIDCELL_Y[0][self.level]:
      self.ticks = self.ticks % constants.FRAMES_PER_GRIDCELL_Y[0][self.level]
      return True

    return False

  # returns if a given line in the board is to be cleared
  def is_line_clear(self, line_number):
    for i in range(len(self.pieces_table[line_number])):
      if self.pieces_table[line_number][i] == constants.PIECE_ID_EMPTY:
        return False 
    return True

  def get_available_moves_state_info(self, verbose = False):
    """Returns a list of tuples of move and state info of each possible move.
    Each move is a tuple of 3 values (x offset, y offset, rotation).
    State info is a tuple of values corresponding to information of the resulting board.
    """
    # TODO: frame delay system
    self.update_frame_count() # will move piece down naturally if needed

    moves = [[-1, 1, 0],  [-2, 2, 0], [-3, 3, 0], [-4, 4, 0], [-5, 5, 0], [-6, 6, 0], \
      [-1, 1, -1], [-1, 1, 1], [-2, 2, -1], [-2, 2, 1], [-3, 3, -1], [-3, 3, 1], \
        [-4, 4, -1], [-4, 4, 1], [-5, 5, -1], [-5, 5, 1], [-6, 6, -1], [-6, 6, 1], \
          [-1, 2, -2], [-1, 2, 2], [-2, 2, -2], [-2, 2, 2], [-3, 3, -2], [-3, 3, 2], \
            [-4, 4, -2], [-4, 4, 2], [-5, 5, -2], [-5, 5, 2], [-6, 6, -2], [-6, 6, 2], \
              [-1, 2, -3], [-1, 2, 3], [-2, 2, -3], [-2, 2, 3], [-3, 3, -3], [-3, 3, 3], \
                [-4, 4, -3], [-4, 4, 3], [-5, 5, -3], [-5, 5, 3], [-6, 6, -3], [-6, 6, 3], \
                  [1, 1, 0], [2, 2, 0], [3, 3, 0],  [4, 4, 0], [5, 5, 0], [6, 6, 0], \
                    [1, 1, -1], [1, 1, 1], [2, 2, -1], [2, 2, 1], [3, 3, -1], [3, 3, 1], \
                      [4, 4, -1], [4, 4, 1], [5, 5, -1], [5, 5, 1], [6, 6, -1], [6, 6, 1], \
                        [1, 2, -2], [1, 2, 2], [2, 2, -2], [2, 2, 2], [3, 3, -2], [3, 3, 2], \
                          [4, 4, -2], [4, 4, 2], [5, 5, -2], [5, 5, 2], [6, 6, -2], [6, 6, 2], \
                            [1, 2, -3], [1, 2, 3], [2, 2, -3], [2, 2, 3], [3, 3, -3], [3, 3, 3], \
                              [4, 4, -3], [4, 4, 3], [5, 5, -3], [5, 5, 3], [6, 6, -3], [6, 6, 3], \
                                [0, 1, 0], [0, 1, 1], [0, 1, -1], [0, 2, 2], [0, 2, -2], [0, 3, 3], [0, 3, -3], \
                                  [-7, 7, 0], [-7, 7, 1], [-7, 7, -1], [7, 7, 0], [7, 7, 1], [7, 7, -1]]
    
    legal_moves_priority_1 = []
    legal_moves_priority_2 = []
    legal_moves_priority_3 = []
    legal_moves_priority_4 = []
    legal_moves_priority_5 = []
    legal_moves_priority_6 = []
    legal_moves_tetris = []

    test_pieces_table = copy.deepcopy(self.pieces_table)
    for move in moves:
      move_metadata = []
      move_metadata.append(0) # fit
      if self.is_valid_move(self.piece, move, test_pieces_table, verbose=verbose):
        test_pieces_table = copy.deepcopy(self.pieces_table)
        move_to_append = [move, self.get_board_info(move, test_pieces_table, move_metadata, verbose=verbose)]

        feature_lines_cleared = move_to_append[1][0]
        feature_lines_ready_to_clear = move_to_append[1][1]
        feature_board_height = move_to_append[1][2]
        feature_height_below_median_height = move_to_append[1][3]
        feature_fit = move_to_append[1][4]
        feature_pieces_fittable = move_to_append[1][5]
        feature_bumpiness = move_to_append[1][6]
        feature_valleys = move_to_append[1][7]
        feature_valley_depth = move_to_append[1][8]
        feature_max_height_diff = move_to_append[1][9]
        feature_holes = move_to_append[1][10]
        feature_holes_created = move_to_append[1][11]
        feature_holes_covered = move_to_append[1][12]
        feature_row_transitions = move_to_append[1][13]
        feature_column_transitions = move_to_append[1][14]
        feature_right_well = move_to_append[1][15]

        # score Tetris
        if feature_lines_cleared >= 1.0:
          legal_moves_tetris.append(move_to_append)
          break

        elif self.piece.get_id() == 1 and feature_holes < 1.0:
          if move == [4, 4, 1]:
            legal_moves_priority_1.append(move_to_append)

        # board high, scores lines and does not make holes
        elif feature_board_height >= 0.5 and feature_lines_cleared > 0 and feature_holes_created >= 0.5 or\
          feature_holes_created > 0.5:
          legal_moves_priority_1.append(move_to_append)

        # priority 6 - makes holes or next move makes holes
        elif feature_holes_created < 0.5:
        #elif (feature_holes_created < 0.5 or feature_fit < 0.1 or feature_valleys - self.valleys < 0) and\
        #  feature_right_well - self.right_well <= 0:
          legal_moves_priority_6.append(move_to_append)        

        # priority 5 - makes holes, valleys, next move makes holes, and doesn't make use of the right well
        elif (feature_valleys < self.valleys and feature_right_well == self.right_well) or \
          (feature_fit < 0.1 and feature_right_well <= self.right_well) or feature_height_below_median_height <= 0.5:
        #elif (feature_holes_created < 0.5 or feature_fit < 0.1 or feature_valleys - self.valleys < 0) and\
        #  feature_right_well - self.right_well <= 0:
          legal_moves_priority_5.append(move_to_append)

        ## priority 4 - covers holes without clearing lines
        #elif feature_holes_covered < 1.0 and feature_lines_cleared == 0.0:
        ##elif feature_holes_covered < 1.0 and feature_lines_cleared == 0.0 or feature_holes_created < 0.5:
        #  legal_moves_priority_4.append(move_to_append)

        # priority 3 - doesn't maintain right well or makes too high of a difference in height
        elif (feature_right_well < self.right_well and feature_holes_created == 0.5) or feature_max_height_diff < 0.6:
        #elif (feature_right_well - self.right_well < 0 and feature_holes_created == 0.5) or\
        #  (feature_board_height <= 0.35 and feature_holes_created == 0.5 and feature_lines_cleared != 0.0) or\
        #    feature_max_height_diff < 0.6:
          legal_moves_priority_3.append(move_to_append)

        # priority 2 - doesn't clear holes or board is high and doesn't clear lines
        elif (feature_holes_created == 0.5 and feature_board_height <= 0.35) or \
          (feature_board_height > 0.35 and feature_lines_cleared == 0.0):
          legal_moves_priority_2.append(move_to_append)

        # priority 1 - everything else
        else:
          legal_moves_priority_1.append(move_to_append)
          
        # generate tucks / spins
        for tuck_or_spin in self.generate_tucks_and_spins(move, test_pieces_table, verbose=verbose):
          tuck_or_spin_metadata = []
          tuck_or_spin_metadata.append(0) # fit
          tuck_or_spin_to_append = [tuck_or_spin, self.get_board_info(tuck_or_spin, \
            copy.deepcopy(self.pieces_table), tuck_or_spin_metadata, verbose=verbose)]

          feature_lines_cleared = tuck_or_spin_to_append[1][0]
          feature_lines_ready_to_clear = tuck_or_spin_to_append[1][1]
          feature_board_height = tuck_or_spin_to_append[1][2]
          feature_height_below_median_height = tuck_or_spin_to_append[1][3]
          feature_fit = tuck_or_spin_to_append[1][4]
          feature_pieces_fittable = tuck_or_spin_to_append[1][5]
          feature_bumpiness = tuck_or_spin_to_append[1][6]
          feature_valleys = tuck_or_spin_to_append[1][7]
          feature_valley_depth = tuck_or_spin_to_append[1][8]
          feature_max_height_diff = tuck_or_spin_to_append[1][9]
          feature_holes = tuck_or_spin_to_append[1][10]
          feature_holes_created = tuck_or_spin_to_append[1][11]
          feature_holes_covered = tuck_or_spin_to_append[1][12]
          feature_row_transitions = tuck_or_spin_to_append[1][13]
          feature_column_transitions = tuck_or_spin_to_append[1][14]
          feature_right_well = tuck_or_spin_to_append[1][15]

          # score Tetris
          if feature_lines_cleared >= 1.0:
            legal_moves_tetris.append(tuck_or_spin_to_append)
            break
          
          # board high, scores lines and does not make holes
          elif feature_board_height >= 0.5 and feature_lines_cleared > 0 and feature_holes_created >= 0.5 or\
            feature_holes_created > 0.5:
            legal_moves_priority_1.append(tuck_or_spin_to_append)

          # priority 6 - makes holes or next move makes holes
          elif feature_holes_created < 0.5:
          #elif (feature_holes_created < 0.5 or feature_fit < 0.1 or feature_valleys - self.valleys < 0) and\
          #  feature_right_well - self.right_well <= 0:
            legal_moves_priority_6.append(tuck_or_spin_to_append)        

          # priority 5 - makes holes, valleys, next move makes holes, and doesn't make use of the right well
          elif (feature_valleys < self.valleys and feature_right_well == self.right_well) or \
            (feature_fit < 0.1 and feature_right_well <= self.right_well) or feature_height_below_median_height <= 0.5:
          #elif (feature_valleys < self.valleys or feature_fit < 0.1) and feature_right_well <= self.right_well or\
          #  feature_height_below_median_height <= 0.5:
            legal_moves_priority_5.append(tuck_or_spin_to_append)

          ## priority 4 - covers holes without clearing lines
          #elif feature_holes_covered < 1.0 and feature_lines_cleared == 0.0:
          ##elif feature_holes_covered < 1.0 and feature_lines_cleared == 0.0 or feature_holes_created < 0.5:
          #  legal_moves_priority_4.append(tuck_or_spin_to_append)

          # priority 3 - doesn't maintain right well or makes too high of a difference in height
          elif (feature_right_well < self.right_well and feature_holes_created == 0.5) or feature_max_height_diff < 0.6:
          #elif (feature_right_well - self.right_well < 0 and feature_holes_created == 0.5) or\
          #  (feature_board_height <= 0.35 and feature_holes_created == 0.5 and feature_lines_cleared != 0.0) or\
          #    feature_max_height_diff < 0.6:
            legal_moves_priority_3.append(tuck_or_spin_to_append)

          # priority 2 - doesn't clear holes or board is high and doesn't clear lines
          elif (feature_holes_created == 0.5 and feature_board_height <= 0.35) or \
            (feature_board_height > 0.35 and feature_lines_cleared == 0.0):
            legal_moves_priority_2.append(tuck_or_spin_to_append)

          # priority 1 - everything else
          else:
            legal_moves_priority_1.append(tuck_or_spin_to_append)
            
    # select the pool of moves based on priority
    if len(legal_moves_tetris) > 0:
      #log.info('Tetris move')
      return legal_moves_tetris
    elif len(legal_moves_priority_1) > 0:
      #log.info('move priority 1')
      return legal_moves_priority_1
    elif len(legal_moves_priority_2) > 0:
      #log.info('move priority 2')
      return legal_moves_priority_2
    elif len(legal_moves_priority_3) > 0:
      #log.info('move priority 3')
      return legal_moves_priority_3
    elif len(legal_moves_priority_4) > 0:
      #log.info('move priority 4')
      return legal_moves_priority_4
    elif len(legal_moves_priority_5) > 0:
      #log.info('move priority 5')
      return legal_moves_priority_5
    else:
      #log.info('move priority 6')
      return legal_moves_priority_6
      
    '''
    # uncomment when running main
    if len(legal_moves_tetris) > 0:
      log.info('Tetris move')
      return legal_moves_tetris
    elif len(legal_moves_priority_1) > 0:
      log.info('move priority 1')
      return legal_moves_priority_1
    elif len(legal_moves_priority_2) > 0:
      log.info('move priority 2')
      return legal_moves_priority_2
    elif len(legal_moves_priority_3) > 0:
      log.info('move priority 3')
      return legal_moves_priority_3
    elif len(legal_moves_priority_4) > 0:
      log.info('move priority 4')
      return legal_moves_priority_4
    elif len(legal_moves_priority_5) > 0:
      log.info('move priority 5')
      return legal_moves_priority_5
    else:
      log.info('move priority 6')
      return legal_moves_priority_6
    '''

  def get_board_info(self, move, pieces_table_copy, move_metadata, verbose=False):
    """Returns the state info of the board, to be passed into the agent, as a List of 
    features.

    More state info can be given to the agent if needed.

    NOTE: For feature extraction, the piece is moved, hard dropped and then lines are cleared
    (if possible) before extraction. Methods should return more than 1 feature or even other
    things such as the board itself, to cut down on loops.
    """
    # get the new board state
    coords = self.piece.simulate_move(move[0], move[1], move[2]) # the new coords

    # get the new board
    feature_landing_height, hard_drop_value, simulated_pieces_table = \
      self.generate_board_with_move(coords, pieces_table_copy)

    # features related to lines
    feature_lines_cleared, feature_lines_ready_to_clear, simulated_pieces_table = \
      self.get_features_line(simulated_pieces_table, coords, hard_drop_value)

    # features related to differences in height
    # NOTE: these 2 methods could be merged eventually
    feature_board_height, feature_fit, feature_pieces_fittable, feature_height_below_median_height = \
      self.get_features_height(simulated_pieces_table)      
    move_metadata[0] = feature_fit

    feature_bumpiness, feature_valleys, feature_valley_depth, feature_max_height_diff = \
      self.get_features_height_diff(simulated_pieces_table)

    # features related to holes
    feature_holes, feature_holes_created, feature_overhang, feature_holes_covered = \
      self.get_features_holes(simulated_pieces_table, coords)

    # features related to transitions
    feature_row_transitions, feature_column_transitions = self.get_features_transitions(simulated_pieces_table)

    # features related to right well
    feature_right_well = self.get_features_right_well(simulated_pieces_table)

    if verbose:
      log.info(' * lines_cleared               : '+ feature_lines_cleared)
      log.info(' * lines_ready_to_clear        : '+ feature_lines_ready_to_clear)
      log.info(' * board_height                : '+ feature_board_height)
      log.info(' * fit                         : '+ feature_fit)
      log.info(' * pieces_fittable             : '+ feature_pieces_fittable)
      log.info(' * bumpiness                   : '+ feature_bumpiness)
      log.info(' * valleys                     : '+ feature_valleys)
      log.info(' * valley_depth                : '+ feature_valley_depth)
      log.info(' * max_height_diff             : '+ feature_max_height_diff)
      log.info(' * holes                       : '+ feature_holes)
      log.info(' * holes_created               : '+ feature_holes_created)
      log.info(' * holes_covered               : '+ feature_holes_covered)
      log.info(' * row_transitions             : '+ feature_row_transitions)
      log.info(' * column_transitions          : '+ feature_column_transitions)
      log.info(' * right_well                  : '+ feature_right_well)

    # add in the hard drop to the actual move
    move[1] += hard_drop_value

    return [feature_lines_cleared, feature_lines_ready_to_clear, feature_board_height, \
      feature_height_below_median_height, feature_fit, feature_pieces_fittable, feature_bumpiness, \
        feature_valleys, feature_valley_depth, feature_max_height_diff, feature_holes, \
        feature_holes_created, feature_holes_covered, feature_row_transitions, feature_column_transitions, \
          feature_right_well]

    '''
    return [feature_board_height, feature_bumpiness, feature_valleys, feature_holes, feature_holes_created, \
      feature_lines_cleared, feature_lines_ready_to_clear, feature_row_transitions, feature_column_transitions, feature_right_well,\
        feature_holes_covered, feature_fit, feature_valley_depth, feature_pieces_fittable, feature_max_height_diff]
    '''

  def generate_board_with_move(self, new_coords, board):
    """Performs a hard drop (places the piece on the board as if it would just fall 
    vertically only), then returns several features related to the new board and the
    new board itself.

    Args:
      new_coords (List): The coordinates of the Piece as a Lists of Lists of (X, Y) 
      for each cell that it occupies.
      board (Array): The 2D Array of the temporary board.
    Returns:
      landing_height (float): The normalized lowest point at which a piece will end up on the 
      board (from a height of 0 to 20).
      hard_drop_value (int): The number of cells that a piece will end up dropping.
      board (Array): The resulting board as a result of the piece being hard dropped.
    """
    # remove the piece
    for coord in self.piece.get_coords():
      board[coord[0]][coord[1]] = constants.PIECE_ID_EMPTY

    # try to do a hard drop
    hard_drop_value = 0
    for i in range(self.height):
      is_valid = True
      for coord in new_coords:
        if coord[0] + hard_drop_value + 1 >= self.height or board[coord[0] + \
          hard_drop_value + 1][coord[1]] != constants.PIECE_ID_EMPTY:
          is_valid = False
          break

      if is_valid:
        hard_drop_value += 1
      else:
        break

    # update the coords
    landing_height = self.height - 1
    for coord in new_coords:
      board[coord[0] + hard_drop_value][coord[1]] = constants.PIECE_ID_CURRENT
      landing_height = min(landing_height, coord[0] + hard_drop_value)

    return landing_height / 20, hard_drop_value, board

  def get_features_line(self, board, coords, hard_drop_value):
    """Returns features that are related to line clears, and clears lines if necessary in the 
    temporary board.

    Args:
      board (Array): The 2D Array of the temporary board.
      coords (List of Tuples): The List of Tuples of (y, x) coordinates.
      hard_drop_value (int): The number of spaces that a piece hard drops.
    Returns:
      feature_lines_to_clear (float): The number of lines cleared (from 0 to 4 lines).
      feature_lines_ready_to_clear (float): The number of lines that are filled except the 
      rightmost column (from 0 to 3 lines).
    """
    lines_to_clear = set() # keep track of previous lines to not double-count
    lines_ready_to_clear = set()
    lines_checked = []

    # run through all coords of the current piece to get the lines to clear
    for coord in coords:
      if coord[0] not in lines_checked:
        is_cleared = True
        is_ready = True

        for j in range(self.width - 1): # left to right
          if board[coord[0] + hard_drop_value][j] == constants.PIECE_ID_EMPTY:
            is_cleared = False
            is_ready = False
            break

        if board[coord[0] + hard_drop_value][self.width - 1] != constants.PIECE_ID_EMPTY:
          is_ready = False
        else:
          is_cleared = False

        if is_cleared:
          lines_to_clear.add(coord[0])
        if is_ready:
          lines_ready_to_clear.add(coord[0])
        lines_checked.append(coord[0])

    # clear the simulated tables
    lines_to_clear_list = list(lines_to_clear).reverse()
    if lines_to_clear_list is not None and lines_to_clear_list(lines_to_clear) > 0:
      for line in lines_to_clear_list:
        board.pop(line)

      for i in range(len(lines_to_clear_list)):
        board.insert(0, [0 for i in range(self.width)])

    return len(lines_to_clear) / 4, len(lines_ready_to_clear) / 3, board

  def get_features_height(self, board):
    """Returns features that are related to board height.
    
    Args:
      board (Array): The 2D Array of the temporary board.
    Returns:
      feature_board_height (float): The average height of all filled columns (from a height of 0
      to 20).
      feature_fit (float): The number of columns that the piece can fit in (from 0 to 10).
      feature_pieces_fittable (float): The number of unique pieces that can fit on the board (from
      0 to 7).
      feature_height_below_median_height (float): The sum of squared height difference between 
      all columns that are lower than the median column height (from 0 to 20 per column).
    """
    # self.piece_next
    empty_columns = 0
    total_height = 0
    prev_height = 0      # needed for O
    prev_prev_height = 0 # needed for T, S, Z pieces
    fit = 0

    height_below_median_height = 0
    
    o_piece_fittable = False
    t_piece_fittable = False
    s_piece_fittable = False
    z_piece_fittable = False
    j_piece_fittable = False
    l_piece_fittable = False

    id = self.piece_next.get_id()

    column_height_list = []

    for i in range(self.width): # column
      height = 0
      for j in range(self.height): # row
        if board[j][i] != constants.PIECE_ID_EMPTY:
          height = j
          break
      
      if i != self.width - 1:
        if height == 0:
          empty_columns += 1
        else:
          total_height += (self.height - height)

      # check if all unique pieces can fit
      if i != 0:
        
        # I piece
        if id == 1: 
          fit += 1

        # O piece
        if prev_height == height:
          if id == 2:
            fit += 1
          o_piece_fittable = True

        # T piece
        if (prev_prev_height == prev_height and prev_height == height) or \
          (prev_prev_height == height and prev_prev_height != prev_height):
          if id == 3: 
            fit += 1
          t_piece_fittable = True
      
        # S piece
        if (prev_prev_height == prev_height and prev_height - height == -1) or\
          (prev_prev_height - prev_height == 1) or (prev_height - height == 1):
          if id == 4:
            fit += 1
          s_piece_fittable = True

        # Z piece
        if (prev_prev_height - prev_height == 1 and prev_height == height) or\
          (prev_prev_height - prev_height == -1) or (prev_height - height == -1):
          if id == 5: 
            fit += 1
          z_piece_fittable = True

        # J piece
        if (prev_prev_height == prev_height or prev_height == height) or\
          (prev_prev_height - prev_height == -2 or prev_height - height == -2):
          if id == 6: 
            fit += 1
          j_piece_fittable = True

        # L piece
        if (prev_prev_height == prev_height or prev_height == height) or\
          (prev_prev_height - prev_height == 2 or prev_height - height == 2):
          if id == 7:
            fit += 1
          l_piece_fittable = True

      prev_prev_height = prev_height
      prev_height = height

      column_height_list.append(height)
      
    pieces_fittable = 0
    if o_piece_fittable: 
      pieces_fittable += 1
    if t_piece_fittable: 
      pieces_fittable += 1
    if s_piece_fittable: 
      pieces_fittable += 1
    if z_piece_fittable: 
      pieces_fittable += 1
    if j_piece_fittable: 
      pieces_fittable += 1
    if l_piece_fittable: 
      pieces_fittable += 1

    # exclude the rightmost column for median height
    column_height_list.pop(len(column_height_list) - 1)
    median_col_height = int(statistics.median(column_height_list))

    median_col_height_upper_limit = 0

    for column_height in column_height_list:
      if column_height < median_col_height:
        height_below_median_height += (median_col_height - column_height) * \
          (median_col_height - column_height)
        median_col_height_upper_limit += 20

    if median_col_height_upper_limit == 0:
      median_col_height_upper_limit = 1
          
    # if the board is empty
    if self.width - empty_columns == 0:
      return 0.0, fit / 9, pieces_fittable / 6, max(1.0 - height_below_median_height / \
        median_col_height_upper_limit, 0.0)
    else:
      return total_height / (self.width - empty_columns) / 20, fit / 9, pieces_fittable / 6, \
        max(1.0 - height_below_median_height / median_col_height_upper_limit, 0.0)

  def get_features_height_diff(self, board):
    """Returns features that are related to differences in height.
    
    Features returned are the average of all columns with cells, rather than the entire board.
    The rightmost column is not considered as it is used as a well.
    
    Args:
      board (Array): The 2D Array of the temporary board.
    Returns:
      feature_bumpiness (float): The average absolute height difference between all filled columns
      (from height of 0 to 20).
      feature_valleys (float): The number of valleys (columns that are 3 or more pieces lower than
      its adjacent columns) dividied by the filled columns.
      feature_valley_depth (float): The average depth of all valleys (from a height of 0 to 20).
      feature_max_height_diff (float): The maximum absolute difference in height of all columns
      (from a height of 0 to 20).
    """
    filled_columns = 0
    prev_height = 0
    prev_prev_height = 0

    bumpiness = 0

    valleys = 0
    valley_combined_depth = 0

    max_column_height_diff = 0
    max_height = 20
    min_height = 0

    # iterate through each column
    for i in range(self.width - 1):
      height = 20

      # get the height
      for j in range(self.height):
        if board[j][i] != constants.PIECE_ID_EMPTY:
          height = j
          break

      bumpiness += abs(height - prev_height) * abs(height - prev_height)

      #max_column_height_diff = max(max_column_height_diff, abs(height - prev_height))      

      # determine valleys
      if prev_height - prev_prev_height >= 3 and prev_height - height >= 3:
        valleys += 1
        valley_combined_depth += max(abs(height - prev_height), \
          abs(prev_prev_height - prev_height))

      if height < 20:
        filled_columns += 1
      prev_prev_height = prev_height
      prev_height = height

      max_height = min(max_height, height)
      min_height = max(min_height, height)

    max_column_height_diff = abs(max_height - min_height)

    if filled_columns == 0:
      return 1.0, 1.0, 1.0, 1.0
    elif valleys != 0:
      return 1 - bumpiness / (filled_columns * filled_columns * 20 * 20), 1 - valleys / filled_columns, \
        1 - valley_combined_depth / (20 * valleys), 1 - max_column_height_diff / 20
    else:
      return 1 - bumpiness / (filled_columns * filled_columns * 20 * 20), 1.0, 1.0, \
        1 - max_column_height_diff / 20

  def get_features_holes(self, board, coords):
    """Returns features that are related to holes.

    Args:
      board (Array): The 2D Array of the temporary board.
      coords (List of Tuples): The List of Tuples of (y, x) coordinates.
    Returns:
      feature_holes (float): The number of holes per column with holes (from 0 to 20).
      feature_holes_created (float): The net change of holes (from 4 to -4 holes created).
      feature_overhang (float): The number of overhangs (filled cells above a hole) per
      column with holes (from 0 to 20)
      feature_holes_covered (float): The number of holes that are covered by the move (based
      on the number of holes).
    """
    holes = 0
    hole_columns = 0
    overhang_total = 0

    holes_in_piece_columns = 0

    # get the columns that the piece coords are in
    piece_coords_columns_set = set()
    for coord in coords:
      piece_coords_columns_set.add(coord[1])

    for i in range(self.width - 1):
      flag = False # presence of a cell that is filled
      overhang_count = 0
      overhang_in_column = 0

      holes_in_column = 0

      for j in range(self.height):
        if board[j][i] != constants.PIECE_ID_EMPTY:
          flag = True
          overhang_count += 1
        elif flag:
          holes_in_column += 1
          overhang_in_column += overhang_count
          overhang_count = 0
      
      overhang_total += overhang_in_column

      if i in piece_coords_columns_set:
        holes_in_piece_columns += holes_in_column

      holes += holes_in_column
      if holes_in_column > 0:
        hole_columns += 1

    if holes == 0:
      return 1.0, 0.5, 1.0, 1.0
    elif self.holes == 0:
      return 1.0 - holes / 20 * hole_columns, max(0.5 - 0.5 * holes / 4, 0), \
        1.0 - overhang_total / (20 * hole_columns), 1.0 - holes_in_piece_columns / holes
    else:
      return 1.0 - holes / 20 * hole_columns, 0.5 - 0.5 * ((holes - self.holes) / self.holes), \
        1.0 - overhang_total / (20 * hole_columns), 1.0 - holes_in_piece_columns / holes
    
    '''
    if hole_columns == 0:
      return 1.0, 0.5, 1.0, 1.0
    elif self.holes != 0:
      if holes != 0:
        return 1.0 - holes / 20 * hole_columns, 0.5 - 0.5 * ((holes - self.holes) / self.holes), \
          1.0 - overhang_total / hole_columns, 1.0 - holes_in_piece_columns / holes
      else:
        return 1.0 - holes / 20 * hole_columns, 0.5 - 0.5 * ((holes - self.holes) / self.holes), \
          1.0, 1.0
    else:
      # makes holes
      if holes != 0:
        return 1.0 - holes / 20 * hole_columns, max(0.5 - 0.5 * holes, 0) , \
          1 - overhang_total / holes, 1 - holes_in_piece_columns / holes
      else:
        return 1.0 - holes / 20 * hole_columns, max(0.5 - 0.5 * holes, 0) , \
          1.0, 1.0
    '''
    
  def get_features_transitions(self, board):
    """Returns features that are related to transitions.

    Transitions refer to a change from filled to not-filled and vice versa.
    The rightmost column is not considered as it is used as a well.

    Args:
      board (Array): The 2D Array of the temporary board.
    Returns:
      feature_row_transitions (float): The number of transitions in each row (from 0 to 100).
      feature_column_transitions (float): The number of transitions in each column (from 0
      to 100).
    """
    row_transitions = 0
    col_transitions = 0

    for i in range(self.height - 1):
      for j in range(self.width):
        # row transition
        if j != self.width - 1:
          if board[i][j] != board[i][j + 1]:
            row_transitions += 1
        if board[i][j] != board[i + 1][j]:
          col_transitions += 1

    return 1 - (row_transitions / 100), 1 - (col_transitions / 100)

  def get_features_right_well(self, board):
    """Returns features that are related to the right well.

    The result of the right well is divided by the overhangs to further differentiate
    based on the number of overhangs (which we try to avoid).

    Args:
      board (Array): The 2D Array of the temporary board.
    Returns:
      feature_right_well (float): The number of filled cells in the rightmost column
      (from 0 to 20), divided by the number of overhangs.
    """
    # the number of filled cells over holes
    count = 0

    # the number of filled sections of cells over holes
    overhang_count = 0
    overhang_flag = False

    for i in range(self.height):
      if board[i][self.width - 1] != constants.PIECE_ID_EMPTY:
        overhang_flag = True
        count += 1
      elif overhang_flag:
        overhang_count += 1
        overhang_flag = False
    
    if overhang_count == 0:
      overhang_count = 1

    return (1 - count / 20) / overhang_count

  def generate_tucks_and_spins(self, move, board, verbose=False):
    """Returns a List of moves corresponding to tucks and spins.

    Tucks are moves that occur when the piece is moved left or right at the last moment,
    while spins are the same, except the piece is rotated.

    Tucks where the piece is moved while in mid-air are not considered due to computation time,
    although they would certainly be useful at times.

    Args:
      move (tuple): A tuple of (x, y, rotation) representing the movement in x / y dimension
      and the rotation of the piece.
      board (Array): The 2D Array of the temporary board.
      verbose (Boolean): Logs out the move generated, False by default.
    Returns:
      A List of legal moves that are either tucks or spins.
    """
    tuck_left = copy.deepcopy(move)
    tuck_right = copy.deepcopy(move)
    spin_left = copy.deepcopy(move)
    spin_right = copy.deepcopy(move)

    tuck_left[0] -= 1
    tuck_right[0] += 1
    spin_left[2] -= 1
    spin_right[2] += 1

    legal_moves = []
    tucks_or_spins = [tuck_left, tuck_right, spin_left, spin_right]
    for tuck_or_spin in tucks_or_spins:
      if self.is_valid_move(self.piece, tuck_or_spin, board, verbose=verbose):
        legal_moves.append(tuck_or_spin)
        if verbose:
          log.info(tuck_or_spin)

    return legal_moves

  # rewards and scores
  def get_score_increase(self, lines_cleared):
    return self.scoring_system[lines_cleared]

  def get_reward_increase(self, lines_cleared):
    return self.reward_system[lines_cleared]

  def get_reward_increase_well(self):
    return self.get_features_right_well(self.pieces_table)

  def get_reward_holes(self):
    for i in range(self.width):
      flag = False # presence of a cell that is filled
      for j in range(self.height):
        if self.pieces_table[j][i] != constants.PIECE_ID_EMPTY and \
          self.pieces_table[j][i] != constants.PIECE_ID_CURRENT:
          flag = True
        elif flag:
          return -1
    
    return 1

  def update_and_get_reward_holes(self):
    """Counts the number of holes in the board and updates it. Returns
    1 if a hole created, or 5 per hole removed.
    """
    right_well_count = 0
    holes = 0
    hole_columns = 0
    overhang_total = 0

    for i in range(self.width):
      flag = False # presence of a cell that is filled
      overhang_count = 0
      overhang_in_column = 0
      right_well_overhang_count = 0

      right_well_overhang_flag = False

      holes_in_column = 0

      for j in range(self.height):
        if self.pieces_table[j][i] != constants.PIECE_ID_EMPTY and \
          self.pieces_table[j][i] != constants.PIECE_ID_CURRENT:
          flag = True
          overhang_count += 1

          if i == self.width - 1:          
            right_well_count += 1
            right_well_overhang_flag = True
        elif flag:
          holes_in_column += 1
          overhang_in_column += overhang_count
          overhang_count = 0

          if right_well_overhang_flag:
            right_well_overhang_count += 1
            right_well_overhang_flag = False

      if right_well_overhang_count == 0:
        right_well_overhang_count = 1

      overhang_total += overhang_in_column

      if i != self.width - 1:
        holes += holes_in_column

    holes_temp = self.holes
    self.holes = holes

    self.right_well = (1 - right_well_count / 20) / right_well_overhang_count
    
    if hole_columns == 0:
      return 1.0
    elif holes_temp != 0:
      return 0.5 - 0.5 * ((holes - holes_temp) / holes_temp)
    else:
      return max(0.5 - 0.5 * holes / 4, 0)

  def update_max_height_diff(self):
    """Updates the max_height_diff of the board.
    """
    filled_columns = 0
    prev_height = 0
    prev_prev_height = 0

    valleys = 0
    valley_combined_depth = 0

    max_column_height_diff = 0
    max_height = 20
    min_height = 0

    # iterate through each column
    for i in range(self.width - 1):
      height = 20

      # get the height
      for j in range(self.height):
        if self.pieces_table[j][i] != constants.PIECE_ID_EMPTY:
          height = j
          break

      # determine valleys
      if prev_height - prev_prev_height >= 3 and prev_height - height >= 3:
        valleys += 1
        valley_combined_depth += max(abs(height - prev_height), \
          abs(prev_prev_height - prev_height))

      if height < 20:
        filled_columns += 1

      prev_prev_height = prev_height
      prev_height = height

      max_height = min(max_height, height)
      min_height = max(min_height, height)

    max_column_height_diff = abs(max_height - min_height)

    self.max_height_diff = 1 - max_column_height_diff / 20
    
    if filled_columns == 0:
      self.valleys = 1.0
    else:
      self.valleys = 1 - valleys / filled_columns
      
  # return the number of lines that have been cleared in the most recent move
  def get_lines_cleared_recently(self):
    return self.lines_cleared_recently

  def get_lines_ready_to_clear_recently(self):
    """Returns the number of rows that are filled except for the last column in the board.
    """
    rows_to_check = [] # keep track of previous lines cleared to prevent double-count
    rows_ready_to_clear = 0

    # run through all coords of the current piece to get the lines to clear
    for coord in self.piece.get_coords():
      if coord[0] not in rows_to_check:
        rows_to_check.append(coord[0])

    for row in rows_to_check:
      ready_flag = True
      for j in range(self.width - 1):
        if self.pieces_table[row][j] == constants.PIECE_ID_EMPTY:
          ready_flag = False
          break

      if ready_flag and self.pieces_table[row][self.width - 1] == constants.PIECE_ID_EMPTY:
        rows_ready_to_clear += 1

    return rows_ready_to_clear

  def get_current_piece(self):
    return self.piece

  def get_piece_count(self):
    return self.piece_count

  def get_move_count(self):
    return self.move_count

  def get_lines_cleared(self):
    return self.line_clears

  def get_line_clear_single(self):
    return self.line_clear_single

  def get_line_clear_double(self):
    return self.line_clear_double

  def get_line_clear_triple(self):
    return self.line_clear_triple

  def get_line_clear_tetris(self):
    return self.line_clear_tetris

  def get_level(self):
    return self.level

  def get_score(self):
    return self.score

  def get_deep_copy_pieces_table(self):
    return copy.deepcopy(self.pieces_table)

  def set_board(self, board):
    """Sets the board based from a 2D array of pieces.

    Args:
      board (Array): The board to set to.
    """
    self.pieces_table = board

  def set_current_piece(self, piece_id):
    self.piece = Piece(piece_id)

  def set_next_piece(self, piece_id):
    self.next_piece = Piece(piece_id)
