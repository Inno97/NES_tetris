# imports

# board.py
import random
import copy

# gym environment
import gym
import pandas
from gym import spaces

import numpy as np

# reinforcment learning
import tensorflow as tf
import os
import statistics
from pathlib import Path
import time

# local imports
from shape import shape
from piece import piece
from board import board
from env import NesTetrisEnv
from ai import ExperienceBuffer, Agent

# settings
STARTING_LEVEL = 18
IS_DAS_ON = False # delayed auto-shift, not implemented yet

# remove moves that are in opposite directions (IE move left then move right)
IS_ONE_DIRECTION_MOVEMENT = True 

IS_TRUE_RANDOM_PIECES = True # generates pieces randomly

# fixed parameters

# board sizes
BOARD_HEIGHT = 20
BOARD_WIDTH = 10

# frames required for a piece to move down 1 cell vertically
FRAMES_PER_GRIDCELL_Y = [[48, 
   43, 38, 33, 28, 23, 
   18, 13, 8, 6, 5, 
   5, 5, 4, 4, 4, 
   3, 3, 3, 2, 2, 
   2, 2, 2, 2, 2,
   2, 2, 2, 1]]

# delayed auto-shift, forces first move to be delayed to 16 frames
DAS_DELAY = 16

FRAME_DELAY = 6 # how many frames it takes per move

# initial lines needed for first level increase
LINES_FIRST_LEVEL_JUMP = [[10,
   20, 30, 40, 50, 60, 
   70, 80, 90, 100, 100,
   100, 100, 100, 100, 100, 
   110, 120, 130, 140, 150,
   160, 170, 180, 190, 200,
   200, 200, 200]]

LINES_PER_LEVEL = 10 # how many lines per subsequent level increase


# reinforcement learning
ACTION_SIZE = 5
STATE_SIZE = 5

# colab paths
#WEIGHT_PATH = os.path.join(os.getcwd(), 'weights.h5')
#IMAGE_PATH = os.path.join(os.getcwd(), 'model.png')
#LOG_DIR = os.path.join(os.getcwd(), 'logs')

WEIGHT_PATH = os.path.join(os.path.dirname(__file__), 'weights.h5')
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'model.png')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

# trains and runs the agent

env = NesTetrisEnv()
obs = env.reset()
network = Network(epsilon=0.95, epsilon_episode_limit=500)
#network.load()

done = False
total_games = 0
total_steps = 0
episodes = 50
total_episodes = 2000

while not done:
  time_start = time.time()
  steps, rewards, scores = network.train(env, episodes=episodes)
  total_games += len(scores)
  total_steps += steps
  network.save()


  print("==================")
  print("* Total Games: ", total_games)
  print("* Took total / per game (seconds):", time.time() - time_start, "/", (time.time() - time_start) / episodes)
  print("* Total Steps: ", total_steps)
  print("* Epsilon: ", network.epsilon)
  print("*")
  print("* Average: ", sum(rewards) / len(rewards), "/", sum(scores) / len(scores))
  print("* Median: ", statistics.median(rewards), "/", statistics.median(scores))
  print("* Mean: ", statistics.mean(rewards), "/", statistics.mean(scores))
  print("* Min: ", min(rewards), "/", min(scores))
  print("* Max: ", max(rewards), "/", max(scores))
  print("==================")

  if total_games > total_episodes:
    done = True 

# load and test
env = NesTetrisEnv()
obs = env.reset()
network = Network()
network.load()

done = False
total_games = 0
total_steps = 0

while not done:
  # get the next action
  if len(obs) != 0:
    #move_num = random.randint(0, len(obs) - 1)
    action, state = network.act(obs)
  else:
    print("no more moves")
    break

  #action, state = network.act(obs) # when the DQN is finished
  obs, reward, done, info = env.step(action)
  env.render()
  print("=====================")

print("=====finished=====")
env.render()
