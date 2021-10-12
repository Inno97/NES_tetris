# reinforcement learning
import random, os
from re import L
import tensorflow as tf
import numpy as np
import constants
from logger import get_logger
log = get_logger()

class ExperienceBuffer:
  def __init__(self, buffer_size=20000):
    '''The storage buffer of past experiences for the agent to learn from.
    '''
    self.buffer = []
    self.buffer_size = buffer_size

  def add(self, experience):
    '''Adds a given experience to the buffer, and pops the last
    '''
    if len(self.buffer) > self.buffer_size:
      self.buffer.pop(0)
    self.buffer.append(experience)

  def sample(self, size):
    '''Returns a random sample from the buffer.
    '''
    return random.sample(self.buffer, size)

class Network:
  def __init__(self, state_size=constants.STATE_SIZE, discount=1, epsilon=1, epsilon_min=0, epsilon_episode_limit=500):
    """The network representing the agent.

    TODO: fill this in
    Args:
      state_size
      discount
      epsilon
      epsilon_min
      epsilon_episode_limit
    """
    self.state_size = state_size
    self.model = self.create_model()
    self.discount = discount
    self.epsilon = epsilon
    self.epsilon_min = epsilon_min
    self.epsilon_episode_limit = epsilon_episode_limit
    self.epsilon_decay = (epsilon - epsilon_min) / epsilon_episode_limit
    self.experiences = ExperienceBuffer()
    self.tensorboard = tf.keras.callbacks.TensorBoard(log_dir=constants.LOG_DIR,
                                                      histogram_freq=1000,
                                                      write_graph=True,
                                                      write_images=True)
    
  def create_model(self, verbose=False):
    """Creates and returns a model to be used.

    If verbose, prints out a summary of the model created.
    """
    model =  tf.keras.models.Sequential([
        tf.keras.layers.Dense(128, input_dim=self.state_size, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear'),
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mean_squared_error'])

    if verbose:
      model.summary()

    tf.keras.utils.plot_model(model, constants.IMAGE_PATH, show_shapes=True)

    return model

  def act(self, obs):
    """Returns the best move based on a List of given states, unless agent decides to explore, 
    which it returns a random move instead.

    TODO: fill in this documentation with the proper types
    Returns:
    """
    # no moves
    if len(obs) == 0:
      return None, None
    # explore
    elif random.uniform(0, 1) < self.epsilon:
      return np.array(obs[random.randint(0, len(obs) - 1)])

    best_rating = None
    state_to_use = 0

    ratings = self.predict_ratings(obs)
    for i in range(len(obs)):
      if best_rating is None or ratings[i] > best_rating:
        best_rating = ratings[i]
        state_to_use = i

    return obs[state_to_use][0], obs[state_to_use][1]

  def predict_ratings(self, states):
    """Returns the predictions from the agent as a List.
    """
    predictions = self.model.predict(np.array([state[1] for state in states]))

    return [predict[0] for predict in predictions]

  def train(self, env, episodes=1):
    """Trains for a given number of episodes and returns a List of Lists for the
    steps, rewards, scores and line clears for the training episodes.
    """
    rewards = []
    scores = []

    lines_cleared = []
    lines_cleared_single = []
    lines_cleared_double = []
    lines_cleared_triple = []
    lines_cleared_tetris = []
    steps = 0

    for episode in range(episodes):
      obs = env.reset()
      move_metadata = []
      move_metadata.append(0) # fit
      current_state = env.board.get_board_info([0, 0, 0], env.board.get_deep_copy_pieces_table(), move_metadata)

      done = False
      total_reward = 0

      while not done:
        action, next_state = self.act(obs)
        if action is None:
          done = True
          steps += 1
          total_reward -= 5
          continue

        obs, reward, done, info = env.step(action)
        self.experiences.add((current_state, reward, next_state, done, action))

        current_state = next_state
        steps += 1
        total_reward += reward

      rewards.append(total_reward)
      scores.append(env.board.get_score())

      lines_cleared.append(env.board.get_lines_cleared())
      lines_cleared_single.append(env.board.get_line_clear_single())
      lines_cleared_double.append(env.board.get_line_clear_double())
      lines_cleared_triple.append(env.board.get_line_clear_triple())
      lines_cleared_tetris.append(env.board.get_line_clear_tetris())

      self.learn()
      if episode % 10 == 0 and episode != 0:
        log.info('Trained for ' + str(episode) + ' episodes')

    return [steps, rewards, scores, lines_cleared, lines_cleared_single, lines_cleared_double, \
      lines_cleared_triple, lines_cleared_tetris]

  def load(self, path=constants.WEIGHT_PATH):
    """Loads weights from local .h5 file (default is taken from config.yml).
    """
    if os.path.isfile(path):
      self.model.load_weights(path)
      log.info('Loaded weights from ' + str(path))
    else:
      log.warn('Unable to load.')

  def save(self, path=constants.WEIGHT_PATH):
    """Saves weights to local .h5 file (default is taken from config.yml).
    """
    try:
      if not os.path.exists(os.path.dirname(constants.WEIGHT_DIR)):
        os.makedirs(os.path.dirname(constants.WEIGHT_DIR))

      self.model.save_weights(path)
      log.info('Saved weights to ' + str(path))
    except Exception:
      log.warn('Failed to save')

  def learn(self, batch_size=2048, epochs=1, episodes=1):
    """Model learns about recent experiences.

    Batch_size corresponds to the random experiences from experience buffer.
    """
    if len(self.experiences.buffer) < batch_size: # buffer too small, return
      return

    batch = self.experiences.sample(batch_size)
    train_x = []
    train_y = []

    # NOTE: testing if we should put in the original move data
    states = np.array([[x[4], x[2]] for x in batch])
    #states = np.array([[[0, 0, 0], x[2]] for x in batch])
    
    ratings = self.predict_ratings(states)

    for i, (current_state, reward, next_state, done, action) in enumerate(batch):
      if not done:
        q = reward + self.discount * ratings[i]
      else:
        q = reward
      train_x.append(current_state)
      train_y.append(q)

    self.model.fit(np.array(train_x), np.array(train_y), batch_size=len(train_x), verbose=0,
                  epochs=epochs, callbacks=[self.tensorboard])
    self.epsilon = max(self.epsilon_min, self.epsilon - self.epsilon_decay * episodes)
