import numpy as np
import time
import collections
import env_factory
import craft
import env

import env_factory
def solve(env, primitive, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = collect(env, primitive)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

  if total_reward>0.5:
    return 0.2

  return total_reward


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"
  reward = 0 
  for i in range(10):
    if(i == 0):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
    
    elif(i==1):
      p = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      
    elif(i==2):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()

    elif(i==3): #grass not present onthe grid should return empty list
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()

    elif(i==4):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[plank]')
      env.reset()
      #env.step(1)
      #env.step(4)

    elif(i==5):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 3, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[cloth]')
      env.reset()
      #env.step(1)
      #env.step(4)


    elif(i==6):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 4, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[rope]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)

    elif(i==7):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)
      #env.step(0)
      #env.step(4)

    elif(i==8):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)

    else:
      p = "gold"
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
      
    r= solve(env, p, visualise=visualise)
    reward += r

  return reward
  
  
def collect(env, primitive):
  """
  Generates a sequence of actions to find, move adjacent to, face, and collect a primitive.

  This function implements a Breadth-First Search (BFS) algorithm to find the 
  shortest path from the agent's current state to a state where it can collect 
  the target primitive.

  The key considerations are:
  1.  **Correct Goal State**: The agent cannot move onto the primitive's cell. It must
      move to an empty adjacent cell.
  2.  **Agent Direction**: The 'USE' action is directional. The agent must be facing
      the primitive to collect it. Therefore, the agent's direction is a critical
      part of the search state.

  The BFS explores states represented as (position, direction) tuples, ensuring
  the final path correctly orients the agent before the final 'USE' action.
  """
  import numpy as np
  from collections import deque

  # -- State and environment information --
  current_state = env._current_state
  grid = current_state.grid
  start_pos = current_state.pos
  start_dir = current_state.dir
  
  grid_w, grid_h, _ = grid.shape
  primitive_index = env.world.cookbook.index[primitive]

  # -- Mappings for actions, directions, and grid deltas --
  # Based on CraftLab spec & craft.py constants: DOWN=0, UP=1, LEFT=2, RIGHT=3.
  # We assume the agent's internal state `CraftState.dir` uses the same convention.
  action_to_dir = {
      craft.DOWN: 0,
      craft.UP: 1,
      craft.LEFT: 2,
      craft.RIGHT: 3,
  }
  
  # Delta (dx, dy) for moving in the direction of an action. Assumes (x, y) coordinates.
  action_deltas = {
      craft.DOWN: (0, -1),
      craft.UP: (0, 1),
      craft.LEFT: (-1, 0),
      craft.RIGHT: (1, 0),
  }

  # Reverse mapping to find which action is needed to face a certain relative direction.
  delta_to_action = {v: k for k, v in action_deltas.items()}

  # -- Helper function for pathfinding --
  def is_traversable(x, y):
      # A cell is traversable if it is within bounds and completely empty.
      # Any item on a cell makes it non-traversable.
      if not (0 <= x < grid_w and 0 <= y < grid_h):
          return False
      return not np.any(grid[x, y] > 0)

  # 1. Identify all valid goal states for the search.
  # A goal state is a tuple of ((position), direction) where the agent is
  # at an empty cell adjacent to the primitive, and is facing the primitive.
  goal_states = set()
  # Find all locations (px, py) of the target primitive.
  primitive_locations = np.argwhere(grid[:, :, primitive_index] > 0)
  
  if primitive_locations.size == 0:
      return [] # Primitive not found on the map.

  for px, py in primitive_locations:
      # Check all four neighbors of the primitive to find valid standing spots.
      for target_delta, action in delta_to_action.items():
          # The agent's goal position (gx, gy) is adjacent to the primitive (px, py).
          # The delta is from the agent to the target, so agent_pos = primitive_pos - delta.
          dx, dy = target_delta
          gx, gy = px - dx, py - dy

          # The cell the agent stands on must be traversable on its own.
          # We check the start pos separately.
          if is_traversable(gx, gy) or (gx, gy) == start_pos:
              # The direction the agent must face is determined by the required action.
              required_dir = action_to_dir[action]
              goal_states.add(((gx, gy), required_dir))

  if not goal_states:
      return []

  # Handle the edge case where the agent starts in a goal state.
  if (start_pos, start_dir) in goal_states:
      return [craft.USE]

  # 2. Perform Breadth-First Search (BFS) to find the shortest path.
  # The state in the queue is ((x, y), direction, path_list).
  # The visited set stores ((x, y), direction) to avoid cycles and redundant paths.
  queue = deque([(start_pos, start_dir, [])])
  visited = set([(start_pos, start_dir)])

  while queue:
      (cx, cy), cdir, path = queue.popleft()

      # Explore possible next states by taking each of the 4 move actions.
      for action in [craft.UP, craft.DOWN, craft.LEFT, craft.RIGHT]:
          # The action determines the new direction and the attempted move.
          new_dir = action_to_dir[action]
          dx, dy = action_deltas[action]
          nx, ny = cx + dx, cy + dy

          if is_traversable(nx, ny):
              new_state = ((nx, ny), new_dir)
              
              if new_state not in visited:
                  new_path = path + [action]
                  if new_state in goal_states:
                      return new_path + [craft.USE]
                  
                  visited.add(new_state)
                  queue.append((new_state[0], new_state[1], new_path))
                  
  return []


print(evaluate())