# trains and runs the agent

import yaml, statistics, time, os
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
config = yaml.safe_load(open('config.yml'))

from env import NesTetrisEnv
from ai import Network
from logger import get_logger
log = get_logger()

env = NesTetrisEnv()
network = Network(epsilon=0.95, epsilon_episode_limit=config['TRAINING']['EPSILON_LIMIT'])

done = False
episodes_ran = 0
total_steps = 0
episodes = config['TRAINING']['EPISODE_INTERVAL']
total_episodes = config['TRAINING']['EPISODES']

log.info('======================================================================================')
log.info('training for ' + str(total_episodes) + ' episodes')
log.info('======================================================================================')


with tf.device('/GPU:0'):
  fig, ax = plt.subplots()

  episode_axis = []
  rewards_axis = []
  scores_axis = []
  lines_cleared_axis = []

  while not done:
    obs = env.reset()
    time_start = time.time()
    steps, rewards, scores, lines_cleared, lines_cleared_single, lines_cleared_double, \
      lines_cleared_triple, lines_cleared_tetris = network.train(env, episodes=episodes)
    episodes_ran += episodes
    total_steps += steps

    if config['TRAINING']['SAVE_SEPARATE_TRAINING_INTERVALS']:
      path_name = os.path.join(os.path.dirname(__file__), 'weights\\' + \
        config['SETTINGS']['WEIGHTS_FILENAME'] + '_' + str(episodes_ran) + '_episodes.h5')
      network.save(path_name)
    else:
      network.save()

    log.info('======================================================================================')

    log.info(' * Total Games: '  + str(episodes_ran))
    log.info(' * Took total / per game (seconds): '  +  str(time.time() - time_start) +  ' / ' +  str((time.time() - time_start) / episodes))
    log.info(' * Total Steps: '  +  str(total_steps))
    log.info(' * Epsilon: '  +  str(network.epsilon))
    log.info(' * (Reward / Score / Lines Cleared) ')
    log.info(' * Median: '  +  str(statistics.median(rewards)) +  ' / ' +  str(statistics.median(scores)) +  ' / ' +  \
      str(statistics.median(lines_cleared)))
    log.info(' * Mean: '  +  str(statistics.mean(rewards)) +  ' / ' +  str(statistics.mean(scores)) +  ' / ' +  \
      str(statistics.mean(lines_cleared)))
    log.info(' * Min: '  +  str(min(rewards)) +  ' / ' +  str(min(scores)) +  ' / ' +  str(min(lines_cleared)))
    log.info(' * Max: '  +  str(max(rewards)) +  ' / ' +  str(max(scores)) +  ' / ' +  str(max(lines_cleared)))

    log.info('======================================================================================')

    log.info(' * Lines Cleared Statistics (Single / Double / Triple / Tetris):')
    log.info(' * Median: '  +  str(statistics.median(lines_cleared_single)) +  ' / ' +  \
      str(statistics.median(lines_cleared_double)) +  ' / ' +  \
        str(statistics.median(lines_cleared_triple)) +  ' / ' +  \
          str(statistics.median(lines_cleared_tetris)))
    log.info(' * Mean: '  +  str(statistics.mean(lines_cleared_single)) +  ' / ' +  \
      str(statistics.mean(lines_cleared_double)) +  ' / ' +  \
        str(statistics.mean(lines_cleared_triple)) +  ' / ' +  \
          str(statistics.mean(lines_cleared_tetris)))
    log.info(' * Min: '  +  str(min(lines_cleared_single)) +  ' / ' +  str(min(lines_cleared_double)) +  \
      ' / ' +  str(min(lines_cleared_triple)) +  ' / ' +  str(min(lines_cleared_tetris)))
    log.info(' * Max: '  +  str(max(lines_cleared_single)) +  ' / ' +  str(max(lines_cleared_double)) +  \
      ' / ' +  str(max(lines_cleared_triple)) +  ' / ' +  str(max(lines_cleared_tetris)))
    log.info('======================================================================================')

    # play a sample game
    obs = env.reset()
    sample_done = False

    while True:
      # get the next action
      if len(obs) != 0:
        action, state = network.act(obs)
      else:
        break
      env.update_state(state)
      obs, reward, sample_done, info = env.step(action)
    env.render()

    # update graphs
    episode_axis.append(episodes_ran)
    rewards_axis.append(statistics.mean(rewards))
    scores_axis.append(statistics.mean(scores))
    lines_cleared_axis.append(statistics.mean(lines_cleared))

    plt.clf()
    plt.plot(np.array(episode_axis), np.array(rewards_axis))
    ax.set_title('Rewards')
    plt.xlabel('Episodes')
    plt.ylabel('Rewards')
    plt.grid()
    plt.savefig('weights/' + config['SETTINGS']['WEIGHTS_FILENAME'] + '_rewards.jpg')

    plt.clf()
    plt.plot(np.array(episode_axis), np.array(scores_axis))
    ax.set_title('Scores')
    plt.xlabel('Episodes')
    plt.ylabel('Scores')
    plt.grid()
    plt.savefig('weights/' + config['SETTINGS']['WEIGHTS_FILENAME'] + '_scores.jpg')

    plt.clf()
    plt.plot(np.array(episode_axis), np.array(lines_cleared_axis))
    ax.set_title('Lines Cleared')
    plt.xlabel('Lines Cleared')
    plt.ylabel('Rewards')
    plt.grid()
    plt.savefig('weights/' + config['SETTINGS']['WEIGHTS_FILENAME'] + '_lines_cleared.jpg')

    if episodes_ran >= total_episodes:
      done = True
      break

  network.save()

  log.info('training done')
