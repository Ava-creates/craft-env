# -*- coding: utf-8 -*-
import numpy as np
import time
import collections
import env_factory

def solve(env, item, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = craft(env, item)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

  return total_reward

def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"
  reward = 0 
  for i in range(10):
    if(i == 0):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item,  visualise=visualise)
    
    elif(i==1):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise)
      if temp_reward>0 :
        reward -= 0.3
      
    elif(i==2):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)

    elif(i==3):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise)
      if temp_reward>0 :
        reward -= 0.3

    elif(i==4):
      item = "plank"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[plank]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)

    elif(i==5):
      item = "cloth"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 3, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[cloth]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)


    elif(i==6):
      item = "rope"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 4, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[rope]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise)

    elif(i==7):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise)

    elif(i==8):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)

      temp_reward = solve(env, item, visualise=visualise)
      if temp_reward>0 :
        reward -= 0.3

    else:
      item = "goldarrow"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 6, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
      env.reset()
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)
    print(item , reward)
  return reward

def evaluate_new_test():
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes_for_synth.yaml"
  hints_path = "resources/hints.yaml"     
  reward = 0
  env_sampler = env_factory.EnvironmentFactory(
            recipes_path, hints_path, 6, max_steps=100, 
            reuse_environments=False, visualise=False)
  item = "arrow"
  
  # Environment setup:
  env=env_sampler.sample_environment(task_name='make[arrow]')
  
  # Actions to execute:
  env.step(0)
  env.step(2)
  env.step(2)
  env.step(4)
  env.step(0)
  env.step(0)
  env.step(0)
  env.step(0)
  env.step(0)
  env.step(0)
  env.step(2)
  env.step(4)
  env.step(2)
  env.step(2)
  env.step(2)
  env.step(2)
  env.step(2)
  env.step(2)
  env.step(2)
  env.step(4)
  env.step(1)
  env.step(1)
  env.step(4)
  # ===== IDENTIFIABLE_BLOCK_END =====
  reward = solve(env, item, visualise=visualise)  # +1
  return reward
  
def craft(env, item):
  def get_direction(dx, dy):
      if dx > 0:
          return 3  # RIGHT
      elif dx < 0:
          return 2  # LEFT
      elif dy > 0:
          return 1  # UP
      else:
          return 0  # DOWN

  cookbook = env.world.cookbook
  goal_index = cookbook.index[item]

  if goal_index is None:
      raise ValueError("Unknown item")

  workshop_indices = env.world.workshop_indices

  actions = []

  # Find the closest workshop that can craft the desired item
  closest_workshop_idx, min_distance = None, float('inf')
  pos = np.array(env._current_state.pos)

  for workshop_idx in workshop_indices:
      # Calculate the mean position of all workshops of this type
      workshop_pos_list = np.argwhere(env._current_state.grid[:, :, workshop_idx])

      if len(workshop_pos_list) > 0:  # Check if there is any location for the workshop
          workshop_pos_mean = workshop_pos_list.mean(axis=0)
          distance = np.linalg.norm(pos - workshop_pos_mean, ord=2)
          if distance < min_distance:
              closest_workshop_idx, min_distance = workshop_idx, distance

  if closest_workshop_idx is None:
      raise ValueError("No available workshop found")

  # Calculate the closest position to move towards
  target_positions = np.argwhere(env._current_state.grid[:, :, closest_workshop_idx])
  nearest_target_pos = None
  min_nearest_distance = float('inf')

  for target_pos in target_positions:
      distance = np.linalg.norm(pos - target_pos, ord=2)
      if distance < min_nearest_distance:
          nearest_target_pos = target_pos
          min_nearest_distance = distance

  # Move to the closest workshop position
  while not np.array_equal(pos, nearest_target_pos):
      dx, dy = nearest_target_pos - pos
      direction = get_direction(dx, dy)
      actions.append(direction)
      if abs(dx) >= abs(dy):  # Prioritize moving in x-direction first
          pos[0] += 1 if dx > 0 else -1
      else:  # Then move in y-direction
          pos[1] += 1 if dy > 0 else -1

  # Use the workshop to craft the item
  actions.append(4)  # USE
  print(actions)
  return actions

print(evaluate()) 