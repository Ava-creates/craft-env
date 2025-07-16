# -*- coding: utf-8 -*-
import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 14
  reward = craft(env, 14)
#   print("actions", actions_to_take)
#   observations = env.reset()
#   total_reward = 0.0

#   for t in range(len(actions_to_take)):
#     action = actions_to_take[t]
#     reward, done, observations = env.step(action)
#     print(reward)
#     total_reward += reward
#     # print(env._current_state.satisfies(None, 14))
#     if reward:
#       rewarding_frame = observations['image'].copy()
#       rewarding_frame[:40] *= np.array([0, 1, 0])
#     elif done:
#       break

  return reward


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = True
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"

  env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, max_steps=100, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[stick]')
  return solve(env, visualise=visualise)


def craft(env, item_index) -> float:
  from collections import deque
  
  # Action constants
  DOWN, UP, LEFT, RIGHT, USE = 0, 1, 2, 3, 4
  
  def move_towards(pos, target):
    """Returns the next action to move from pos to target using greedy policy."""
    x, y = pos
    tx, ty = target
    if tx < x:
      return LEFT
    elif tx > x:
      return RIGHT
    elif ty < y:
      return DOWN
    elif ty > y:
      return UP
    return None

  def find_positions(kind_index, grid):
    """Return list of (x, y) where kind_index is located."""
    positions = []
    for x in range(grid.shape[0]):
      for y in range(grid.shape[1]):
        if grid[x, y, kind_index]:
          positions.append((x, y))
    return positions

  def get_current_pos():
    return env._current_state.pos

  def is_done():
    return env._is_done()

  reward = 0.0
  steps = 0
  max_steps = env.max_steps

  obs = env.observations()
  needed = env.world.cookbook.primitives_for(item_index)
  # Include goal itself to monitor pickup
  needed[item_index] = 1

  while not is_done() and steps < max_steps:
    obs = env.observations()
    state = env._current_state
    pos = state.pos
    grid = obs["features_dict"]["features_global"]
    inventory = state.inventory.copy()

    # Determine what we still need
    to_get = {item: count for item, count in needed.items() if inventory[item] < count}
    if not to_get:
      # Have everything, try crafting at workshop
      crafted = False
      for i_ws in env.world.workshop_indices:
        workshop_positions = find_positions(i_ws, grid)
        for wp in workshop_positions:
          if abs(wp[0] - pos[0]) + abs(wp[1] - pos[1]) == 1:
            reward_step, done, _ = env.step(USE)
            reward += reward_step
            steps += 1
            crafted = True
            break
        if crafted:
          break
      else:
        # Move toward nearest workshop
        target = workshop_positions[0] if workshop_positions else None
        if target:
          action = move_towards(pos, target)
          if action is not None:
            reward_step, done, _ = env.step(action)
            reward += reward_step
            steps += 1
      continue

    # Otherwise, go collect needed items
    for item in to_get:
      positions = find_positions(item, grid)
      if not positions:
        continue
      target = positions[0]
      if abs(target[0] - pos[0]) + abs(target[1] - pos[1]) == 1:
        reward_step, done, _ = env.step(USE)
        reward += reward_step
        steps += 1
      else:
        action = move_towards(pos, target)
        if action is not None:
          reward_step, done, _ = env.step(action)
          reward += reward_step
          steps += 1
      break

  return reward



print(evaluate()) 