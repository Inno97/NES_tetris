# Contains relevant constants to be used
import os, yaml
config = yaml.safe_load(open('config.yml'))

# Board dimensions
BOARD_HEIGHT = 20
BOARD_WIDTH = 10

# Frames required for a piece to move down 1 cell vertically
FRAMES_PER_GRIDCELL_Y = [[48, 
   43, 38, 33, 28, 23, 
   18, 13, 8, 6, 5, 
   5, 5, 4, 4, 4, 
   3, 3, 3, 2, 2, 
   2, 2, 2, 2, 2,
   2, 2, 2, 1]]

# Delayed auto-shift, forces first move to be delayed to 16 frames
DAS_DELAY = 16

# How many frames it takes per move
FRAME_DELAY = 6 

# Initial lines needed for first level increase
LINES_FIRST_LEVEL_JUMP = [[10,
   20, 30, 40, 50, 60, 
   70, 80, 90, 100, 100,
   100, 100, 100, 100, 100, 
   110, 120, 130, 140, 150,
   160, 170, 180, 190, 200,
   200, 200, 200]]

# how many lines per subsequent level increase
LINES_PER_LEVEL = 10 

# reinforcement learning
ACTION_SIZE = 13
STATE_SIZE = 7

# Paths
WEIGHT_PATH = os.path.join(os.path.dirname(__file__), 'weights\\' + \
   config['SETTINGS']['WEIGHTS_FILENAME'] + '.h5')
WEIGHT_DIR = os.path.join(os.path.dirname(__file__), 'weights\\')
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'weights\\' + \
   config['SETTINGS']['WEIGHTS_FILENAME'] + '.png')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

# used to identify pieces
PIECE_ID_EMPTY = 0
PIECE_ID_I = 1
PIECE_ID_O = 2
PIECE_ID_T = 3
PIECE_ID_S = 4
PIECE_ID_Z = 5
PIECE_ID_J = 6
PIECE_ID_L = 7
PIECE_ID_CURRENT = 8
PIECE_Y_OFFSET_INITIAL = [0, 2, 0, 1, 1, 1, 1, 1] # y offset needed for initial placement