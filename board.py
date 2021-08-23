# the board contains the playing field
import random, yaml, copy
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

    # NOTE: test 2
    self.holes = 0

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

    if not self.update_board():
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
    #return [0, (1 * self.level), (10 * self.level), (100 * self.level), (1000 * self.level)]
    return [0, 10, 100, 1000, 10000]

  def generate_state_info_board(self, new_coords, pieces_table_copy):
    """Performs a hard drop (places the piece on the board as if it would just fall 
    vertically only), then returns several things related to the new board.

    Returns:
      landing_height, the lowest point at which a piece will end up on the board.
      hard_drop_value, the number of cells that a piece will end up dropping.
      pieces_table_copy, the resulting board as a result of the piece being hard dropped.
    """
    # remove the piece
    for coord in self.piece.get_coords():
      pieces_table_copy[coord[0]][coord[1]] = constants.PIECE_ID_EMPTY

    # try to do a hard drop
    hard_drop_value = 0
    for i in range(self.height):
      is_valid = True
      for coord in new_coords:
        if coord[0] + hard_drop_value + 1 >= self.height or pieces_table_copy[coord[0] + \
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
      pieces_table_copy[coord[0] + hard_drop_value][coord[1]] = constants.PIECE_ID_CURRENT
      landing_height = min(landing_height, coord[0] + hard_drop_value)

    #self.render_given_board(pieces_table_copy)
    return landing_height / 20, hard_drop_value, pieces_table_copy

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
                                [0, 1, 0], [0, 1, 1], [0, 1, -1], [0, 2, 2], [0, 2, -2], [0, 3, 3], [0, 3, -3]]
    
    legal_moves = []

    test_pieces_table = copy.deepcopy(self.pieces_table)
    for move in moves:
      if self.is_valid_move(self.piece, move, test_pieces_table, verbose=verbose):
        test_pieces_table = copy.deepcopy(self.pieces_table)
        legal_moves.append([move, self.get_board_info(move, test_pieces_table, verbose=verbose)])

        # tuck / spin
        for tuck_or_spin in self.generate_tucks_and_spins(move, test_pieces_table, verbose=verbose):
          legal_moves.append([tuck_or_spin, self.get_board_info(tuck_or_spin, copy.deepcopy(self.pieces_table), verbose=verbose)])

    return legal_moves

  def get_board_info(self, move, pieces_table_copy, verbose=False):
    """Returns the state info of the board, to be passed into the agent
    More state info can be given to the agent if needed.

    NOTE: The piece is moved and then hard dropped to evaluate how good the move may be.
    """
    # get the new board state
    coords = self.piece.simulate_move(move[0], move[1], move[2]) # the new coords
    landing_height, hard_drop_value, simulated_pieces_table = \
      self.generate_state_info_board(coords, pieces_table_copy)

    # the average height of columns with a piece
    board_height = self.get_state_board_height(simulated_pieces_table)

    # the sum of differences between heights of a column and its adjacent columns
    bumpiness = self.get_state_bumpiness(simulated_pieces_table)

    # how many cells have an empty cell below
    holes = self.get_state_holes(simulated_pieces_table)

    # how many columns are empty
    #wells = self.get_state_wells(simulated_pieces_table)

    # how many lines will be cleared by the move
    lines_cleared, lines_ready_to_clear = self.get_state_line_features(simulated_pieces_table, coords, hard_drop_value)

    # how many empty / filled cells are adjacent to a filled / empty cell on the same row
    row_transitions, col_transitions = self.get_state_transitions(simulated_pieces_table)

    # proportion of pieces on the left of the board
    #proportion_left = self.get_proportion_left_side(simulated_pieces_table)

    # if a right well is present
    right_well = self.get_right_well(simulated_pieces_table)

    if verbose:
      #log.info(' * landing_height:             ' + str(landing_height))
      #log.info(' * board_height:               ' + str(board_height))
      log.info(' * bumpiness:                  ' + str(bumpiness))
      log.info(' * holes:                      ' + str(holes))
      log.info(' * lines_cleared:              ' + str(lines_cleared))
      log.info(' * row_transitions:            ' + str(row_transitions))
      log.info(' * lines_ready_to_clear:       ' + str(lines_ready_to_clear))
      #log.info(' * col_transitions:            ' + str(col_transitions))
      #log.info(' * proportion_left:            ' + str(proportion_left))
      log.info(' * right_well:                 ' + str(right_well))

    move[1] += hard_drop_value

    return [board_height, bumpiness, holes, lines_cleared, \
      row_transitions, lines_ready_to_clear, right_well]

  def get_state_line_features(self, board, coords, hard_drop_value):
    """Returns the number of lines cleared when a piece is hard dropped, and the number
    of lines that are ready to clear (columns 0 to 8 are filled but 9 isn't).

    The agent should want to clear lines with a move.

    Args:
      board (Array): The 2D Array of the board.
      coords (List of Tuples): The List of Tuples of (y, x) coordinates.
      hard_drop_value (int): The number of spaces that a piece hard drops.
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

    return len(lines_to_clear) / 4, len(lines_ready_to_clear) / 3

  def get_state_wells(self, board):
    """Returns how many wells there are in the board.
    """
    wells = 0
    for i in range(len(board[0])): # column
      is_well = True
      for j in range(len(board)): # row
        if board[j][i] != constants.PIECE_ID_EMPTY:
          is_well = False
          break

      if is_well:
        wells += 1

    return wells

  def get_state_board_height(self, board):
    """Returns the average height of all non-empty columns.
    """
    try:
      empty_columns = 0
      total_height = 0

      for i in range(self.width): # column
        height = 0
        for j in range(self.height): # row
          if board[j][i] != constants.PIECE_ID_EMPTY:
            height = j
            break
        if height == 0:
          empty_columns += 1
        else:
          total_height += (self.height - height)

      return (total_height / (self.width - empty_columns) / 20)
    except ZeroDivisionError:
      return 0

  def get_state_board_height_features(self, board):
    """Returns several height related features from a board.

    Returns:
      Average board height of filled columns.
      Max height of all filled columns.
    """
    try:
      empty_columns = 0
      total_height = 0

      max_height = 0

      for i in range(len(board[0])): # column
        height = 0
        for j in range(len(board) - 1, 0, -1): # row
          if board[j][i] != constants.PIECE_ID_EMPTY:
            height = j
            max_height = max(max_height, j)
            break
        if height == 0:
          empty_columns += 1
        else:
          total_height += height

      return total_height / (self.width - empty_columns), max_height
    except ZeroDivisionError:
      return 0, 0

  # returns the sum total of differences between height of each column and its adjacent one
  def get_state_bumpiness(self, board):
    bumpiness = 0

    # iterate through each column
    for i in range(self.width):
      prev_height = 0
      height = 0
      for j in range(self.height):
        if board[j][i] != constants.PIECE_ID_EMPTY: # get the first non-empty cell
          height = j
          if i != 0:
            bumpiness += abs(height - prev_height)
          prev_height = height

          break
      
    return bumpiness / 190

  # returns how many cells that have an empty cell below
  def get_state_holes(self, board):
    holes = 0

    for i in range(self.width):
      flag = False # presence of a cell that is filled
      for j in range(self.height):
        if board[j][i] != constants.PIECE_ID_EMPTY:
          flag = True
        elif flag:
          holes += 1

    return 1 - (holes / 100)

  def get_state_transitions(self, board):
    """Returns the row and column transitions.

    Transitions are the sum of different cells adjacent to one another in row / col.
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

  def get_proportion_left_side(self, board):
    """Returns the proportion of pieces that lie on the left side of the board.

    Agent should try to stack on the left based on general player behavior.
    """
    try:
      count_left = 0
      count_right = 0

      mid = int(self.width / 2)

      for i in range(0, mid, 1):
        for j in range(self.height):
          if board[j][i] != constants.PIECE_ID_EMPTY:
            count_left += 1

      for i in range(mid, self.width, 1):
        for j in range(self.height):
          if board[j][i] != constants.PIECE_ID_EMPTY:
            count_right += 1

      return count_left / (count_left + count_right)
    except ZeroDivisionError:
      return 0

  def get_right_well(self, board):
    """Returns the presence of a right well.

    Agent should try to maintain a right well to make Tetrises.
    """
    for i in range(self.height):
      if board[i][self.width - 1] != constants.PIECE_ID_EMPTY:
        return 0

    return 1

  def generate_tucks_and_spins(self, move, pieces_table_copy, verbose=False):
    """Returns a List of moves corresponding to tucks and spins.
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
      if self.is_valid_move(self.piece, tuck_or_spin, pieces_table_copy, verbose=verbose):
        legal_moves.append(tuck_or_spin)
        if verbose:
          log.info(tuck_or_spin)

    return legal_moves

  # gets the current piece
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

  # returns increase in score from lines cleared
  def get_score_increase(self, lines_cleared):
    return self.scoring_system[lines_cleared]

  def get_reward_increase(self, lines_cleared):
    return self.reward_system[lines_cleared]

  def get_reward_increase_well(self):
    return self.get_right_well(self.pieces_table)

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
    -1 per hole created, or 5 per hole removed.
    """
    holes = 0
    for i in range(self.width):
      flag = False # presence of a cell that is filled
      for j in range(self.height):
        if self.pieces_table[j][i] != constants.PIECE_ID_EMPTY and \
          self.pieces_table[j][i] != constants.PIECE_ID_CURRENT:
          flag = True
        elif flag and self.pieces_table[j][i] != constants.PIECE_ID_CURRENT:
          holes += 1

    diff = holes - self.holes
    reward = 0 if (diff > 0) else diff * -5
    self.holes = holes

    return reward

  def get_deep_copy_pieces_table(self):
    return copy.deepcopy(self.pieces_table)
