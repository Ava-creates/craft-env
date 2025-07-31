import numpy as np
import time

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
      primtive = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[axe]')
        
      reward += solve(env, primitive, visualise=visualise)

  return reward

# @funsearch.evolve
def collect(env, primitive) -> list[int]:
  """Returns a list of actions to find and collect the primitve passed int he function in the passed env. """
  # return [1,4]
  # `collect_v2` is an improvement over `collect_v1` by using Breadth-First Search (BFS)
  # to find a path that respects obstacles and agent facing direction for the 'USE' action.
  # Since `collections.deque` cannot be imported inside the function, a list is used
  # as a queue (simulating deque's behavior by incrementing an index).

  ACTION_DOWN = 0
  ACTION_UP = 1
  ACTION_LEFT = 2
  ACTION_RIGHT = 3
  ACTION_USE = 4

  # Map action to its corresponding direction integer (0:UP, 1:RIGHT, 2:DOWN, 3:LEFT)
  ACTION_TO_DIR = {
      ACTION_UP: 0,
      ACTION_RIGHT: 1,
      ACTION_DOWN: 2,
      ACTION_LEFT: 3
  }

  # Map direction integer to its (dx, dy) vector (change in position)
  DIR_VEC = {
      0: (0, -1),  # UP: decreases y
      1: (1, 0),   # RIGHT: increases x
      2: (0, 1),   # DOWN: increases y
      3: (-1, 0)   # LEFT: decreases x
  }

  print(env.world.grabbable_indices)
  # 1. Pre-checks: If the primitive is not a grabbable item, it cannot be "collected".
  if primitive not in env.world.grabbable_indices:
    return []

  # Get current state information
  initial_state = env._current_state
  start_x, start_y = initial_state.pos
  start_dir = initial_state.dir # Agent's initial facing direction (0, 1, 2, or 3)
  grid = initial_state.grid
  grid_width, grid_height, _ = grid.shape

  # Helper function to check if a grid cell is within bounds and not an obstacle.
  # Obstacles are defined by non_grabbable_indices (e.g., water, workshops).
  non_grabbable_indices = env.world.non_grabbable_indices
  def is_walkable(x, y):
    if not (0 <= x < grid_width and 0 <= y < grid_height):
      return False # Out of bounds
    # Check if the cell is occupied by any non-grabbable item that blocks movement.
    for k_idx in non_grabbable_indices:
      if grid[x, y, k_idx] == 1:
        return False
    return True

  # Breadth-First Search (BFS) for shortest path
  # Queue stores tuples: (current_x, current_y, current_direction, list_of_actions_taken)
  # Using a list and an index to simulate a queue's `popleft` efficiently (amortized O(1) for appends, O(1) for popping by index).
  queue = [(start_x, start_y, start_dir, [])]
  queue_idx = 0

  # Visited set to avoid redundant exploration and cycles.
  # A state is defined by (x, y, direction) because the agent's direction matters for the 'USE' action.
  visited = set([(start_x, start_y, start_dir)])
  print(len(queue))
  while queue_idx < len(queue):
    print("in bfs")
    curr_x, curr_y, curr_dir, path_actions = queue[queue_idx]
    queue_idx += 1 # "Pop" the current state by advancing the index
    print("path", path_actions)
    # Check if the primitive can be collected from the current position and direction.
    # The 'USE' action is assumed to act on the cell directly in front of the agent.
    faced_dx, faced_dy = DIR_VEC[curr_dir]
    faced_x, faced_y = curr_x + faced_dx, curr_y + faced_dy

    # If the cell directly in front contains the target primitive and is within bounds:
    if (0 <= faced_x < grid_width and 0 <= faced_y < grid_height and
        grid[faced_x, faced_y, primitive] == 1):
      # Goal reached! Return the path including the final 'USE' action.
      return path_actions + [ACTION_USE]

    # Explore possible next movement actions (UP, RIGHT, DOWN, LEFT)
    for action in [ACTION_UP, ACTION_RIGHT, ACTION_DOWN, ACTION_LEFT]:
      # Determine the new position and direction after this action.
      # The agent moves in the direction of the action and faces that direction.
      move_dx, move_dy = DIR_VEC[ACTION_TO_DIR[action]]
      next_x, next_y = curr_x + move_dx, curr_y + move_dy
      next_dir = ACTION_TO_DIR[action] # Agent's new facing direction

      # If the next cell is walkable and this (position, direction) state hasn't been visited,
      # add it to the queue for further exploration.
      if is_walkable(next_x, next_y) and (next_x, next_y, next_dir) not in visited:
        visited.add((next_x, next_y, next_dir))
        queue.append((next_x, next_y, next_dir, path_actions + [action]))

  # If the queue becomes empty and no path to collect the primitive was found, return an empty list.
  return []



print(evaluate())