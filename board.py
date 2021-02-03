# the board contains the playing field
PIECE_ID_CURRENT = 8 # used to identify the current piece
PIECE_ID_EMPTY = 0
PIECE_OFFSET_INITIAL = [0, 2, 0, 1, 1, 1, 1, 1] # y offset needed for initial placement

class Board:
  def __init__(self, height, width):
    self.height = height
    self.width = width

    self.pieces_table = [[0 for i in range(width)] for j in range(height)]

    self.piece = None
    self.piece_next = None

    self.ticks = 0 # the current frame count
    self.level = STARTING_LEVEL
    self.move_count = 0
    self.piece_count = 0
    self.line_clears = 0
    self.line_clears_for_next_level = LINES_FIRST_LEVEL_JUMP[0][self.level]

    self.scoring_system = self.generate_scoring_system()
    self.score = 0
    self.game_over = False

    # unused as holding pieces are not allowed in NES tetris
    self.piece_holding = None
    self.piece_last = None
    self.can_hold = False

    # generate the random bag of pieces
    self.bag = self.generate_bag()
    self.piece = self.create_piece()
    self.piece_next = self.create_piece()

  # generates a full bag of 7 pieces 
  def generate_bag(self):
    random_shapes = list(SHAPES)
    random.shuffle(random_shapes)

    bag = []
    # generate bag based on whether true random or fixed
    if IS_TRUE_RANDOM_PIECES:
      for i in range(7):
        id = random_shapes[random.randint(0, 6)].get_id()
        bag.append(Piece(id))
    else:
      for shapes in random_shapes:
        bag.append(Piece(shapes.get_id()))
    return bag

  # generates a random piece
  def create_piece(self):
    if not self.bag:
      self.bag = self.generate_bag()
    return self.bag.pop()

  # put the new piece on the board and then update the next piece
  def place_new_piece(self):
    # swap piece and then fill the bag if needed
    self.piece = self.piece_next
    self.piece_next = self.create_piece()

    # place the piece in the middle of the board
    self.piece.move(int(self.width / 2), 0 - PIECE_OFFSET_INITIAL[self.piece.get_id()], 0)

    if not self.update_board():
      self.game_over = True
      return

    self.piece_count += 1
    self.ticks = 0

  # moves the piece, assumes that move is legal and expects a tuple of (x, y, rotation)
  def move_piece(self, move, verbose = False):
    self.get_current_piece().move(move[0], move[1], move[2])
    self.update_board()
    self.lines_cleared_recently = 0

    if self.is_piece_set():
      self.set_piece()
      self.lines_cleared_recently = self.update_line_clear()
      self.update_score(self.lines_cleared_recently)      
      self.place_new_piece()

    if verbose:
      self.print_current_piece_state()
      print("cleared lines", lines_cleared)
      self.render_board()

  # sets the piece on the board, assumes that piece clears check for being set
  def set_piece(self):
    for coord in self.piece.get_coords():
      self.pieces_table[coord[0]][coord[1]] = self.piece.get_id()

  # manually sets the next piece, only done when the next piece has no 
  # available moves, and cannot be set because of this
  def force_set_next_piece(self):
    if self.is_piece_set():
      self.set_piece()

  # updates the current piece's coords on the board, and returns status
  def update_board(self):
    for coord in self.piece.get_prev_coords():
      if self.pieces_table[coord[0]][coord[1]] == PIECE_ID_CURRENT:
        self.pieces_table[coord[0]][coord[1]] = PIECE_ID_EMPTY
      else:
        #self.reset_move(self.piece.get_coords(), self.piece.get_prev_coords())
        return False

    for coord in self.piece.get_coords():
      if self.pieces_table[coord[0]][coord[1]] > PIECE_ID_EMPTY and self.pieces_table[coord[0]][coord[1]] < PIECE_ID_CURRENT:
        self.reset_move(self.piece.get_coords(), self.piece.get_prev_coords())
        return False
      else:
        self.pieces_table[coord[0]][coord[1]] = PIECE_ID_CURRENT

    self.move_count += 1
    return True

  # runs through the board, clears any filled lines and returns how many that were cleared
  def update_line_clear(self):
    lines_to_clear = [] # keep track of previous lines to not double-count
    lines_cleared = []

    # run through all coords of the current piece to get the lines to clear
    for coord in self.piece.get_coords():
      if self.is_line_clear(coord[0]) and coord[0] not in lines_to_clear:
        lines_to_clear.append(coord[0])

    # clear the lines
    lines_to_clear.reverse()
    for line in lines_to_clear:
      lines_cleared.append(self.clear_line(line))

    # add back lines
    self.add_empty_lines(len(lines_to_clear))

    self.line_clears += len(lines_to_clear)

    return len(lines_to_clear)

  # clears the specified line
  def clear_line(self, line_number):
    return self.pieces_table.pop(line_number)

  # adds an empty line
  def add_empty_lines(self, lines_to_add):
    for i in range(lines_to_add):
      self.pieces_table.insert(0, [0 for i in range(self.width)])

  # checks and updates level according to line clears
  def update_level(self):
    if self.lines >= self.line_clears_for_next_level:
      self.level += 1
      self.line_clears_for_next_level += 10

  # resets the previous move made, because it was illegal and executed halfway
  # this does not revert any overwritten cells that were previously occupied by a piece
  def reset_move(self, coords, prev_coords):
    # revert new state
    for coord in coords:
      if self.pieces_table[coord[0]][coord[1]] == PIECE_ID_CURRENT:
        self.pieces_table[coord[0]][coord[1]] = PIECE_ID_EMPTY

    # restore previous state
    for coords in prev_coords:
      self.pieces_table[coord[0]][coord[1]] = PIECE_ID_CURRENT

  # update frame tick count and move the piece down
  def update_frame_count(self):
    if IS_DAS_ON:
      self.ticks += DAS_DELAY
    self.ticks += FRAME_DELAY

  # updates the score based on the level
  def update_score(self, lines_cleared):
    self.score += self.scoring_system[lines_cleared]

  # returns a list of points given for line clears for the current level
  def generate_scoring_system(self):
    return [0, (40 * self.level + 1), (100 * self.level + 1), (300 * self.level + 1), (1200 * self.level + 1)]

  # return new final board state for state info
  def generate_state_info_board(self, new_coords, pieces_table_copy):
    # remove the piece
    for coord in self.piece.get_coords():
      pieces_table_copy[coord[0]][coord[1]] = PIECE_ID_EMPTY

    # try to do a hard drop
    hard_drop_value = 0
    for i in range(self.height):
      is_valid = True
      for coord in new_coords:
        if coord[0] + hard_drop_value + 1 >= self.height or pieces_table_copy[coord[0] + hard_drop_value + 1][coord[1]] !=  PIECE_ID_EMPTY:
          is_valid = False
          break

      if is_valid:
        hard_drop_value += 1
    
    # update the coords
    landing_height = 0
    for coord in new_coords:
      pieces_table_copy[coord[0] + hard_drop_value][coord[1]] = PIECE_ID_CURRENT
      landing_height = max(landing_height, coord[0] + hard_drop_value)

    return landing_height, pieces_table_copy

  # prints out the entire board
  def render_board(self):
    for i in range(self.height):
      line_to_print = "|"
      for j in range(self.width):
        id = self.pieces_table[i][j]
        if id == PIECE_ID_EMPTY:
          line_to_print += " |"
        elif id == PIECE_ID_CURRENT:
          line_to_print += "=|"
        else:
          line_to_print += "X|"
      
      print(line_to_print)

  def print_current_piece_state(self):
    self.piece.print_info()

  def print_next_piece_state(self):
    self.piece_next.print_info()

  # validate if the move is legal or not
  def is_valid_move(self, piece, move, board, verbose = False):
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

  # returns if the piece should be set into the board
  # piece is considered set if it touches another piece on the board
  def is_piece_set(self):
    for coord in self.piece.get_coords():
      if coord[0] == (self.height - 1):
        return True
      elif self.pieces_table[coord[0] + 1][coord[1]] > PIECE_ID_EMPTY and self.pieces_table[coord[0] + 1][coord[1]] < PIECE_ID_CURRENT:
        return True

    return False

  # returns if the game is over
  def is_game_over(self):
    return self.game_over

  # returns whether the piece should drop on its own and reset tick count if true
  def is_natural_drop(self):
    if self.ticks > FRAMES_PER_GRIDCELL_Y[0][self.level]:
      self.ticks = self.ticks % FRAMES_PER_GRIDCELL_Y[0][self.level]
      return True

    return False

  # returns if a given line in the board is to be cleared
  def is_line_clear(self, line_number):
    for i in range(len(self.pieces_table[line_number])):
      if self.pieces_table[line_number][i] == PIECE_ID_EMPTY:
        return False 
    return True

  # returns a list of tuples of move and state info of each possible move
  # each move is a tuple of 3 elements (x offset, y offset, rotation)
  # state info is a tuple of elements corresponding to information of the resulting board
  def get_available_moves_state_info(self, verbose = False):
    self.update_frame_count() # will move piece down naturally if needed

    # left / right / down / clockwise / anti-clockwise
    if self.is_natural_drop():
      #moves = [[-1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]]
      moves = [[-1, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 1, -1]]
    else:
      moves = [[-1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]]

    # remove moves that are in opposite direction of the piece direction
    if IS_ONE_DIRECTION_MOVEMENT:
      if self.piece.is_left:
        moves.pop(1)
      elif self.piece.is_right:
        moves.pop(0)
      
    legal_moves = []

    test_pieces_table = copy.deepcopy(self.pieces_table)
    for move in moves:
      if self.is_valid_move(self.piece, move, test_pieces_table, verbose = verbose):
        legal_moves.append([move, self.get_board_info(move, test_pieces_table, verbose = verbose)])
    
    return legal_moves

  # returns the state info of the board, to be passed into the agent
  # more state info can be given to the agent if needed:
  # the piece is moved and then hard dropped to evaluate how good the move may be
  def get_board_info(self, move, pieces_table_copy, verbose = False):
    # get the new board state
    coords = self.piece.simulate_move(move[0], move[1], move[2]) # the new coords
    landing_height, simulated_pieces_table = self.generate_state_info_board(coords, pieces_table_copy)

    # Lines Cleared - How many lines will be cleared by the move
    lines_cleared = self.get_state_lines_cleared(simulated_pieces_table, coords)

    # Wells - Presence of an empty column for Tetrises
    wells = self.get_state_wells(simulated_pieces_table)

    # Board height - How high the current board is
    #board_height = self.get_state_board_height(simulated_pieces_table)

    # Bumpiness - The difference between heights of each column
    #bumpiness = self.get_state_bumpiness(simulated_pieces_table)

    # Holes - How many cells have an empty cell below
    holes = self.get_state_holes(simulated_pieces_table)

    # Row Transitions / Column Transitions - How many empty / filled cells are 
    # adjacent to the opposite on the same row
    row_transitions, col_transitions = self.get_state_transitions(simulated_pieces_table)

    # Piece coordinates - Location of piece and its previous location
    coord_x_new = coords[0][1]
    coord_y_new = coords[0][0]

    if verbose:
      print("lines cleared", lines_cleared, "wells", wells)
      print("board height", board_height, "bumpiness", bumpiness)
      print("holes", holes)
      print("coords new (x, y)" , coord_x_new, coord_y_new, "coords (x, y)", coord_x, coord_y)

    #return [lines_cleared, wells, board_height, bumpiness, holes, 
    #        coord_x_new, row_transitions, col_transitions]
    return [landing_height, lines_cleared, holes, row_transitions, col_transitions]

  def get_state_lines_cleared(self, board, coords):
    lines_to_clear = [] # keep track of previous lines to not double-count

    # run through all coords of the current piece to get the lines to clear
    for coord in coords:
      if coord[0] not in lines_to_clear:
        is_cleared = True
        for j in range(self.width): # by col
          if board[coord[0]][j] == PIECE_ID_EMPTY:
            is_cleared = False
            break

        if is_cleared:
          lines_to_clear.append(coord[0])

    return len(lines_to_clear)
  
  # returns how many wells there are in the board
  def get_state_wells(self, board):
    wells = 0
    for i in range(len(board[0])): # column
      is_well = True
      for j in range(len(board)): # row
        if board[j][i] != PIECE_ID_EMPTY:
          is_well = False
          break

      if is_well:
        wells += 1

    return wells

  # returns the average height of all non-empty columns
  def get_state_board_height(self, board):
    non_empty_columns = 0
    total_height = 0

    for i in range(len(board[0])): # column
      height = 0
      for j in range(len(board)): # row
        if board[j][i] != PIECE_ID_EMPTY:
          height += 1
      if height == 0:
        non_empty_columns += 1
      else:
        total_height += height

    return total_height / (self.width - non_empty_columns)

  # returns the sum total of differences between height of each column and its adjacent one
  def get_state_bumpiness(self, board):
    bumpiness = 0

    # iterate through each column
    for i in range(self.width):
      prev_height = 0
      height = 0
      for j in range(self.height):
        if board[j][i] != PIECE_ID_EMPTY: # get the first non-empty cell
          height = j
          if i != 0:
            bumpiness += abs(height - prev_height)
          prev_height = height

          break
      
    return bumpiness

  # returns how many cells that have an empty cell below
  def get_state_holes(self, board):
    holes = 0

    for i in range(self.width):
      is_overhang = False # presence of a cell above that is filled
      for j in range(self.height):
        if board[j][i] != PIECE_ID_EMPTY:
          is_overhang = True
        elif is_overhang and board[j][i] == PIECE_ID_EMPTY:
          holes += 1

    return holes

  # returns the row and col transitions
  # the aggregate number of different cells adjacent to one another in row / col
  def get_state_transitions(self, board):
    row_transitions = 0
    col_transitions = 0

    is_next_row_empty = True
    is_next_col_empty = True

    for i in range(self.height - 1):
      for j in range(self.width):
        # row transition
        if j != self.width - 1:
          if board[i][j] == PIECE_ID_EMPTY and board[i][j + 1] != PIECE_ID_EMPTY:
            row_transitions += 1
          elif board[i][j] != PIECE_ID_EMPTY and board[i][j + 1] == PIECE_ID_EMPTY:
            row_transitions += 1

        if board[i + 1][j] == PIECE_ID_EMPTY and board[i + 1][j] != PIECE_ID_EMPTY:
          col_transitions += 1
        elif board[i + 1][j] != PIECE_ID_EMPTY and board[i + 1][j] == PIECE_ID_EMPTY:
          col_transitions += 1

    return row_transitions, col_transitions


  # gets the current piece
  def get_current_piece(self):
    return self.piece

  def get_piece_count(self):
    return self.piece_count

  def get_move_count(self):
    return self.move_count

  def get_lines_cleared(self):
    return self.lines_cleared

  def get_level(self):
    return self.level

  def get_score(self):
    return self.score

  # return the number of lines that have been cleared in the most recent move
  def get_lines_cleared_recently(self):
    return self.lines_cleared_recently

  # returns increase in score from lines cleared
  def get_score_increase(self, lines_cleared):
    return self.scoring_system[lines_cleared]

  def get_deep_copy_pieces_table(self):
    return copy.deepcopy(self.pieces_table)