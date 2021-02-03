# reinforcement learning
class ExperienceBuffer:
  def __init__(self, buffer_size=20000):
    self.buffer = []
    self.buffer_size = buffer_size

  def add(self, experience):
    if len(self.buffer) > self.buffer_size:
      self.buffer.pop(-1)
    self.buffer.append(experience)

  def sample(self, size):
    return random.sample(self.buffer, size)

class Network:
  def __init__(self, state_size=STATE_SIZE, discount=1, epsilon=1, epsilon_min=0.0001, epsilon_episode_limit=500):
    self.state_size = state_size
    self.model = self.create_model()
    self.discount = discount
    self.epsilon = epsilon
    self.epsilon_min = epsilon_min
    self.epsilon_episode_limit = epsilon_episode_limit
    self.epsilon_decay = (epsilon - epsilon_min) / epsilon_episode_limit
    self.experiences = ExperienceBuffer()
    self.tensorboard = tf.keras.callbacks.TensorBoard(log_dir=LOG_DIR,
                                                      histogram_freq=1000,
                                                      write_graph=True,
                                                      write_images=True)
    
  # setups and returns model
  def create_model(self, verbose = False):
    model =  tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear'),
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mean_squared_error'])

    if verbose:
      model.summary()

    tf.keras.utils.plot_model(model, IMAGE_PATH, show_shapes=True)

    return model

  # returns the best move, unless agent decides to explore
  def act(self, states):
    # no moves
    if len(states) == 0:
      return None, None
    # explore
    if random.uniform(0, 1) < self.epsilon:
      return np.array(states[random.randint(0, len(states) - 1)])

    best_rating = None
    best_state = None
    state_to_use = 0

    ratings = self.predict_ratings(states)
    for i in range(len(states)):
      if best_rating is None or (best_rating is not None and ratings[i] > best_rating):
        best_rating = ratings[i]
        state_to_use = i

    return states[state_to_use][0], states[state_to_use][1]

  # runs the state through the NN, and return the outputs
  def predict_ratings(self, states):
    if len(states[0]) == 1:
      inputs = np.array(states)
    else:
      inputs = np.array([state[1] for state in states])

    # run the prediction, catch ValueError when states contain List() objs because
    # the state contains moves / board info, which are of different dimensions
    # and are not convertible under np.array(), and end up as List()s
    try:
      predictions = self.model.predict(states)
    except ValueError:
      predictions = self.model.predict(np.array([state[1] for state in states]))
    

    return [predict[0] for predict in predictions]

  # trains for a given number of episodes, returns the amount of steps, reward and scores
  def train(self, env, episodes = 1):
    rewards = []
    scores = []
    steps = 0

    for episode in range(episodes):
      obs = env.reset()
      previous_state = env.board.get_board_info([0, 0, 0], env.board.get_deep_copy_pieces_table())

      done = False
      total_reward = 0

      while not done:
        action, state = self.act(obs)
        if action is None:
          done = True
          steps += 1
          total_reward -= 5
          continue

        obs, reward, done, info = env.step(action)
        self.experiences.add((previous_state, reward, state, done))
        previous_state = state
        steps += 1
        total_reward += reward

      rewards.append(total_reward)
      scores.append(env.board.get_score())

      self.learn()

    return [steps, rewards, scores]

  # load from local .h5
  def load(self):
    if Path(WEIGHT_PATH).is_file():
      self.model.load_weights(WEIGHT_PATH)

  # save to local .h5
  def save(self):
    if not os.path.exists(os.path.dirname(WEIGHT_PATH)):
      os.makedirs(os.path.dirname(WEIGHT_PATH))

    self.model.save_weights(WEIGHT_PATH)

  # model learns about reent experiences
  # batch_size corresponds to the random experiences from experience buffer
  def learn(self, batch_size = 512, epochs = 1):
    if len(self.experiences.buffer) < batch_size: # buffer too small, return
      return

    batch = self.experiences.sample(batch_size)
    train_x = []
    train_y = []

    states = np.array([[[0, 0, 0], x[2]] for x in batch])
    ratings = self.predict_ratings(states)

    for i, (previous_state, reward, next_state, done) in enumerate(batch):
      if not done:
        rating = ratings[i]
        q = reward + self.discount * rating
      else:
        q = reward
      train_x.append(previous_state)
      train_y.append(q)

    self.model.fit(np.array(train_x), np.array(train_y), batch_size=len(train_x), verbose=0,
                  epochs=epochs, callbacks=[self.tensorboard])
    self.epsilon = max(self.epsilon_min, self.epsilon - self.epsilon_decay)