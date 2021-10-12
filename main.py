import yaml, statistics, time, os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
config = yaml.safe_load(open('config.yml'))

from env import NesTetrisEnv
from ai import Network
from logger import get_logger
import constants
log = get_logger()

def get_board():
  """Reads and sets the board based off the console output.
  """
  lines = [\
  '| | | | | |=|=| | | |', 
  '| | | | | |=|=| | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| | | | | | | | | | |', 
  '| |X|X| | |X| | |X| |', 
  '| |X|X|X|X|X|X|X|X| |', 
  '|X|X|X|X|X|X|X|X|X| |', 
  '|X|X|X|X|X|X|X|X|X| |', 
  '|X|X|X|X|X|X|X|X|X| |', 
  '|X|X|X|X|X|X|X|X|X| |']

  board = []

  for line in lines:
    row = []
    for char in line:
      if char == ' ':
        row.append(constants.PIECE_ID_EMPTY)
      elif char == '=':
        row.append(constants.PIECE_ID_CURRENT)
      elif char != '|':
        row.append(constants.PIECE_ID_I)

    board.append(row)

  return board

def log_state(state):
  """Logs the features from a given state.
  """
  log.info(' * lines_cleared                   : ' + str(state[0]))
  log.info(' * lines_ready_to_clear            : ' + str(state[1]))
  log.info(' * board_height                    : ' + str(state[2]))
  log.info(' * height_below_median_height      : ' + str(state[3]))
  log.info(' * fit                             : ' + str(state[4]))
  log.info(' * pieces_fittable                 : ' + str(state[5]))
  log.info(' * bumpiness                       : ' + str(state[6]))
  log.info(' * valleys                         : ' + str(state[7]))
  log.info(' * valley_depth                    : ' + str(state[8]))
  log.info(' * max_height_diff                 : ' + str(state[9]))
  log.info(' * holes                           : ' + str(state[10]))
  log.info(' * holes_created                   : ' + str(state[11]))
  log.info(' * holes_covered                   : ' + str(state[12]))
  log.info(' * row_transitions                 : ' + str(state[13]))
  log.info(' * column_transitions              : ' + str(state[14]))
  log.info(' * right_well                      : ' + str(state[15]))

def main():

  # trains and runs the agent
  env = NesTetrisEnv()
  network = Network(epsilon=0, epsilon_episode_limit=1)
  network.load()


  done = False
  debug_move = False


  log.info('======================================================================================')
  log.info('Running game')
  log.info('======================================================================================')

  with tf.device('/GPU:0'):  
    env = NesTetrisEnv()
    obs = env.reset()

    # load a sample move if necessary for analysis
    if debug_move:
      env.board.set_board(get_board())
      env.board.set_current_piece(2)

    while not done:
      # get the next action
      if len(obs) != 0:
        log.info('===============================================================')
        log.info(' Original right well:        ' + str(env.board.right_well))
        log.info(' Original valleys:           ' + str(env.board.valleys))

        if debug_move:
          for move, state in obs:
            log.info(move)
            log_state(state)
            env.board.render_move(env.board.get_current_piece(), move)

        action, state = network.act(obs)

        log.info('Move / States')
        log.info(action)
        log.info(' Next piece:                  ' + str(env.board.piece_next.get_id()))
        log_state(state)
        log.info('===============================================================')
      else:
        log.info('===============================================================')
        log.info('Game Over')
        log.info('===============================================================')
        break

      env.update_state(state)
      obs, reward, done, info = env.step(action, verbose=False)
      env.render()

    log.info('===============================================================')

    log.info('======FINISHED=======')
    log.info('Score: ' + str(env.board.get_score()))
    log.info('Lines cleared: ' + str(env.board.get_lines_cleared()))

    log.info('===============================================================')
    log.info('Lines cleared: ')
    log.info('Single: ' + str(env.board.get_line_clear_single()))
    log.info('Double: ' + str(env.board.get_line_clear_double()))
    log.info('Triple: ' + str(env.board.get_line_clear_triple()))
    log.info('Tetris: ' + str(env.board.get_line_clear_tetris()))

    log.info('===============================================================')

if __name__ == '__main__':
  main()
