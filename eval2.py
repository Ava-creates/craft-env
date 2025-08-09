import numpy as np
import time
import collections
import env_factory
import craft
import env

import env_factory
def solve(env, primitive, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  #primitive = "wood"
  actions_to_take = collect(env, primitive)
  print(actions_to_take)
  observations = env.reset()
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

  print(primitive, total_reward)
  return total_reward

def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"
  reward = 0 
  for i in range(3):
    if(i == 0):
      primitive = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
        
      reward += solve(env, primitive,  visualise=visualise)

    elif(i==1):
      primitive = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
        
      reward += solve(env, primitive, visualise=visualise)

    else:
      primitive = "gold"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward += solve(env, primitive, visualise=visualise)

  return reward

# @funsearch.evolve
def collect(env, primitive) -> list[int]:
  from collections import deque

  ACTION_MAP = {
      "UP": 0,
      "DOWN": 1,
      "LEFT": 2,
      "RIGHT": 3,
      "USE": 4
  }

  def find_shortest_path(grid, start_pos, target_kind, inventory):
      directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT

      def can_move(x, y, pos_direction):
          if not (0 <= x < grid.shape[0] and 0 <= y < grid.shape[1]):
              return False
          
          # Check for obstacles based on inventory
          is_clear = True
          for i_kind in range(grid.shape[2]):
              if grid[x, y, i_kind] == 1:
                  tool_needed = determine_tool(i_kind)
                  if tool_needed and inventory[tool_needed] <= 0:
                      is_clear = False
                      break
          return is_clear

      def determine_tool(kind_index):
          # This function should map kinds to required tools based on the world's rules
          kind_name = current_state.world.cookbook.index.get(kind_index)
          if kind_name == "WATER":
              return current_state.world.water_index  # Assuming water needs a bridge or boat tool
          elif kind_name == "ROCK":
              return current_state.world.stone_index  # Assuming rocks need a pickaxe tool
          else:
              return None

      queue = deque([(start_pos[0], start_pos[1], current_state.dir, [])])
      visited = set()
      while queue:
          x, y, pos_direction, path = queue.popleft()
          if (x, y, pos_direction) in visited:
              continue
          visited.add((x, y, pos_direction))
          
          # Check if target is found
          if grid[x, y, target_kind] == 1:
              return path + [(x, y)]
          
          for dx, dy in directions:
              nx, ny = x + dx, y + dy
              new_direction = (dx, dy)
              
              if can_move(nx, ny, new_direction):
                  queue.append((nx, ny, new_direction, path + [(nx, ny)]))
      return None

  actions = []
  current_state = env._current_state
  grid = current_state.grid.copy()
  pos = current_state.pos
  inventory = current_state.inventory.copy()

  # Map primitive names to their respective indices in the index list
  primitives_index = current_state.world.cookbook.index.index(primitive)

  # Find the shortest path to a cell containing the target kind
  path_to_primitive = find_shortest_path(grid, pos, primitives_index, inventory)
  if path_to_primitive:
      for (x, y) in path_to_primitive[:-1]:  # Exclude the last position since we'll use there
          dx, dy = x - pos[0], y - pos[1]
          current_direction = current_state.dir
          
          if dx == 0 and dy < 0:  # UP
              target_direction = 0
          elif dx == 0 and dy > 0:  # DOWN
              target_direction = 1
          elif dx < 0 and dy == 0:  # LEFT
              target_direction = 2
          elif dx > 0 and dy == 0:  # RIGHT
              target_direction = 3

          if current_direction != target_direction:
              actions.append(target_direction)  # Add action to change direction

          actions.append(ACTION_MAP["USE"])

      # Collect the primitive
      actions.append(ACTION_MAP["USE"])

  return actions


print(evaluate())