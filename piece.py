# the piece class itself, contains data on its coordinates and rotations
class Piece:
  def __init__(self, id, x = 0, y = 0, rotation = 0):
    self.x = x # coordinates of the top left corner of piece
    self.y = y
    self.id = id
    self.rotation = rotation
    self.shape_coords = None # the coordinates of the shape of the Piece
    self.coords = []
    self.prev_coords = []

    # general direction that the piece has been moving
    self.is_left = False
    self.is_right = False

  # rotates the piece, +1 is clockwise
  def rotate(self, rotation_val):
    if rotation_val == -1 or rotation_val == 1:
      self.rotation += rotation_val
      self.rotation = self.rotation % len(SHAPES_COORDS[self.id])

  # update the coordinates after a move and returns both the previous and
  # the new coordinates
  def move(self, x, y, rotation_val):
    self.prev_coords = self.coords
    self.x += x
    self.y += y
    self.rotate(rotation_val)
    self.coords = self.update_coords()

    if x == -1:
      self.is_left = True
      self.is_right = False
    elif x == 1:
      self.is_left = False
      self.is_right = True

    return self.prev_coords, self.coords

  # returns the coordinates of cells occupied by a piece
  def get_coords(self):
    return self.coords

  # returns the previous coordinates of cells occupied by a piece
  def get_prev_coords(self):
    return self.prev_coords

  def get_rotation(self):
    return self.rotation

  # updates the coordinates of a piece based on its current x / y coordinates
  def update_coords(self):
    self.coords = []
    self.shape_coords = SHAPES_ID[self.id].get_coord_occupied(self.rotation)
    for coord in self.shape_coords:
      self.coords.append([self.y + coord[0], self.x + coord[1]])

    return self.coords

  # simulates a move and returns updated coords without touching original data
  def simulate_move(self, x, y, rotation_val):
    curr_x = self.x + x
    curr_y = self.y + y
    curr_rotation = self.rotation + rotation_val
    curr_rotation = curr_rotation % len(SHAPES_COORDS[self.id])

    coords = []
    shape_coords = SHAPES_ID[self.id].get_coord_occupied(curr_rotation)
    for coord in shape_coords:
      coords.append([curr_y + coord[0], curr_x + coord[1]])

    return coords

  # validates that the current state is legal
  # note: not working, need to insert reference to board for var "board"
  def is_valid_state(self):
    for coord in self.coords:
      x = coord[1]
      y = coord[0]

      if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
        return False
      if board[y][x] != 0 and board[y][x] != 8:
        return False

    return True

  # calculates the amount that a piece will fall after a move
  def get_y_coord_shift(self):
    return 1 # return a single drop for the time being for simplicity
    #return FRAME_DELAY / FRAMES_PER_GRIDCELL_Y[STARTING_LEVEL]

  def get_id(self):
    return self.id

  # prints metadata of piece
  def print_info(self):
    print("current id is:", self.get_id(), "/", SHAPES_NAMES[self.id],
          "Rotation:", self.rotation)
    print("coords:", self.get_coords())

    print("current piece arrangement")
    for line in SHAPES_COORDS[self.get_id()][self.rotation]:
      print("|", line, "|")

  # prints metadata of a simulated move
  def print_simulated_move(self, x, y, rotation_val):
    rotation = self.rotation + rotation_val
    rotation = rotation % len(SHAPES_COORDS[self.id])

    print("current id is:", self.get_id(), "/", SHAPES_NAMES[self.id],
          "Rotation:", rotation)
    print("coords:", self.simulate_move(x, y, rotation_val))

    print("current piece arrangement")
    for line in SHAPES_COORDS[self.get_id()][rotation]:
      print("|", line, "|")

  # prints the current direction that the piece is heading
  def print_direction(self):
    if self.is_left:
      print("left")
    elif self.is_right:
      print("right")
    else:
      print("neutral")