# the possible Shapes of a Piece, these are generated as a list of templates
# id - the class ID of the piece
# orientations - all the possible orientations
class Shape:
  def __init__(self, id, orientations):
      self.id = id
      self.max_rotations = len(orientations)
      self.orientations = orientations
      self.shape_coord = [] # contains the coordinates of spaces filed by the shape
      
      # width and height of the Piece
      self.width = len(orientations[0][0])
      self.height = len(orientations[0])

      self.generate_shape_coord()

  # returns the shape orientation of a piece, given a rotation number
  def get_orientation(self, rotation):
      return self.orientations[rotation % self.max_rotations]

  # get the coordinates of cells occupied by a shape
  def get_coord_occupied(self, rotation):
      return self.shape_coord[rotation % self.max_rotations]

  # generates shape coord all at once
  def generate_shape_coord(self):
      for rotation in range(self.max_rotations):
          self.shape_coord.append(list(self.generate_shape_coord_iterative(rotation)))

  # generate the occupied coordinates of a shape
  def generate_shape_coord_iterative(self, rotation):
      orientation = self.get_orientation(rotation)
      width = self.width
      height = self.height
      for offset_x in range(width):
        for offset_y in range(height):
          if orientation[offset_y][offset_x] != ' ':
            yield offset_y, offset_x

  def get_id(self):
    return self.id

# the different possible Shapes of Pieces and their orientations
# id - 0 / empty, 1 / I, 2 / O, 3 / T, 4 / S, 5 / Z, 6 / J, 7 / L
# first shape is empty

# shape coords
SHAPE_NULL_COORDS = [[' ']]

SHAPE_I_COORDS = [[
    '    ',
    '    ',
    '####',
    '    ',
], [
    '  # ',
    '  # ',
    '  # ',
    '  # ',
]]

SHAPE_O_COORDS = [[
    '##',
    '##',
]]

SHAPE_T_COORDS = [[
    '   ',
    '###',
    ' # ',
], [
    ' # ',
    '## ',
    ' # ',
], [
    ' # ',
    '###',
    '   ',
], [
    ' # ',
    ' ##',
    ' # ',
]]

SHAPE_S_COORDS = [[
    '   ',
    ' ##',
    '## ',
], [
    ' # ',
    ' ##',
    '  #',
]]

SHAPE_Z_COORDS = [[
    '   ',
    '## ',
    ' ##',
], [
    '  #',
    ' ##',
    ' # ',
]]

SHAPE_J_COORDS = [[
    '   ',
    '###',
    '  #',
], [
    ' # ',
    ' # ',
    '## ',
], [
    '#  ',
    '###',
    '   ',
], [
    ' ##',
    ' # ',
    ' # ',
]]

SHAPE_L_COORDS = [[
    '   ',
    '###',
    '#  ',
], [
    '## ',
    ' # ',
    ' # ',
], [
    '  #',
    '###',
    '   ',
], [
    ' # ',
    ' # ',
    ' ##',
]]

SHAPE_NULL = Shape(0, SHAPE_NULL_COORDS)

SHAPE_I = Shape(1, SHAPE_I_COORDS)

SHAPE_O = Shape(2, SHAPE_O_COORDS)

SHAPE_T = Shape(3, SHAPE_T_COORDS)

SHAPE_S = Shape(4, SHAPE_S_COORDS)

SHAPE_Z = Shape(5, SHAPE_Z_COORDS)

SHAPE_J = Shape(6, SHAPE_J_COORDS)

SHAPE_L = Shape(7, SHAPE_L_COORDS)

# the list of templated shapes
SHAPES = [SHAPE_I, SHAPE_O, SHAPE_T, SHAPE_S, SHAPE_Z, SHAPE_J, SHAPE_L]
SHAPES_ID = [SHAPE_NULL, SHAPE_I, SHAPE_O, SHAPE_T, SHAPE_S, SHAPE_Z, SHAPE_J, SHAPE_L]
SHAPES_COORDS = [SHAPE_NULL_COORDS, SHAPE_I_COORDS, SHAPE_O_COORDS, SHAPE_T_COORDS, 
                 SHAPE_S_COORDS, SHAPE_Z_COORDS, SHAPE_J_COORDS, SHAPE_L_COORDS]
SHAPES_NAMES = ["Empty", "Long bar", "O", "T", "S", "Z", "J", "L"]