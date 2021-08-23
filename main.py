import yaml, statistics, time, os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
config = yaml.safe_load(open('config.yml'))

from env import NesTetrisEnv
from ai import Network
from logger import get_logger
log = get_logger()

# trains and runs the agent
env = NesTetrisEnv()
network = Network(epsilon=0, epsilon_episode_limit=1)
network.load()

done = False

log.info('======================================================================================')
log.info('Running game')
log.info('======================================================================================')

with tf.device('/GPU:0'):  
  env = NesTetrisEnv()
  obs = env.reset()

  while not done:
    # get the next action
    if len(obs) != 0:
      action, state = network.act(obs)
      log.info('===============================================================')
      log.info('Move / States')
      log.info(action)
      #log.info(' * landing_height:             ' + str(state[0]))
      #log.info(' * board_height:               ' + str(state[1]))
      #log.info(' * bumpiness:                  ' + str(state[1]))
      #log.info(' * holes:                      ' + str(state[2]))
      #log.info(' * lines_cleared:              ' + str(state[3]))
      #log.info(' * row_transitions:            ' + str(state[4]))
      #log.info(' * lines_ready_to_clear:       ' + str(state[5]))
      #log.info(' * col_transitions:            ' + str(state[7]))
      #log.info(' * proportion_left:            ' + str(state[8]))
      #log.info(' * right_well:                 ' + str(state[6]))
      #log.info('===============================================================')
    else:
      log.info('===============================================================')
      log.info('Game Over')
      log.info('===============================================================')
      break

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
