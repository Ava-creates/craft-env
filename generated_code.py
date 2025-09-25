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
    Calculates a sequence of actions to navigate to and collect a specified primitive.

    This function implements the A* search algorithm to find the shortest path from the
    agent's current state to a state where it is adjacent to and facing the target
    primitive. It correctly handles the agent's direction and navigates around
    obstacles.

    Args:
        env (CraftLab): The environment instance.
        primitive (str): The name of the primitive to collect (e.g., 'WOOD', 'IRON').

    Returns:
        list[int]: A list of action integers representing the optimal plan. Returns
                   an empty list if no path is found.
    """
    # Action constants from the environment specification and analysis.
    # It's assumed UP=Forward, LEFT=Turn Left, RIGHT=Turn Right.
    ACTION_UP = 1
    ACTION_LEFT = 2
    ACTION_RIGHT = 3
    ACTION_USE = 4

    # Define a consistent agent direction encoding (0:N, 1:E, 2:S, 3:W - Clockwise)
    # and the corresponding (dx, dy) vectors for moving forward.
    DIR_VECTORS = {
        0: (0, -1),   # North
        1: (1, 0),    # East
        2: (0, 1),    # South
        3: (-1, 0),   # West
    }

    current_state = env._current_state
    world = current_state.world
    grid = current_state.grid
    start_pos = current_state.pos
    start_dir = current_state.dir

    # Step 1: Identify the target primitive's index and find all its locations.
    try:
        primitive_index = world.cookbook.index[primitive]
    except KeyError:
        return []  # Invalid primitive name.

    target_coords = np.argwhere(grid[:, :, primitive_index] > 0)
    if target_coords.shape[0] == 0:
        return []  # Primitive not found on the grid.
    target_locations = set(map(tuple, target_coords))

    # Step 2: Set up the A* search algorithm.
    # The heuristic function is the Manhattan distance to the nearest target.
    def heuristic(pos):
        px, py = pos
        return min(abs(px - tx) + abs(py - ty) for tx, ty in target_locations)

    # The priority queue stores tuples of: (priority, cost, state, path).
    # - priority: The f-value (cost + heuristic) for sorting.
    # - cost: The g-value, or length of the path so far.
    # - state: A tuple of (x, y, direction).
    # - path: The list of actions taken to reach the state.
    initial_state = (start_pos[0], start_pos[1], start_dir)
    pq = [(heuristic(start_pos), 0, initial_state, [])]
    visited = set()

    while pq:
        _, cost, state, path = heapq.heappop(pq)

        if state in visited:
            continue
        visited.add(state)

        pos_x, pos_y, direction = state

        # Step 3: Check for the goal condition.
        # The goal is reached if the agent is facing a cell with the target primitive.
        dx, dy = DIR_VECTORS[direction]
        front_pos = (pos_x + dx, pos_y + dy)

        if front_pos in target_locations:
            return path + [ACTION_USE]

        # Step 4: Expand the search by exploring all possible actions.

        # Action: TURN_RIGHT (action 3)
        # A clockwise turn increments the direction index.
        new_dir_right = (direction + 1) % 4
        new_state_right = (pos_x, pos_y, new_dir_right)
        if new_state_right not in visited:
            new_cost = cost + 1
            priority = new_cost + heuristic((pos_x, pos_y))
            heapq.heappush(pq, (priority, new_cost, new_state_right, path + [ACTION_RIGHT]))

        # Action: TURN_LEFT (action 2)
        # A counter-clockwise turn decrements the direction index.
        new_dir_left = (direction - 1 + 4) % 4
        new_state_left = (pos_x, pos_y, new_dir_left)
        if new_state_left not in visited:
            new_cost = cost + 1
            priority = new_cost + heuristic((pos_x, pos_y))
            heapq.heappush(pq, (priority, new_cost, new_state_left, path + [ACTION_LEFT]))

        # Action: MOVE_FORWARD (action 1)
        # Check if the cell in front is within bounds and empty (passable).
        fx, fy = front_pos
        width, height, _ = grid.shape
        if 0 <= fx < width and 0 <= fy < height:
            # A cell is passable if its one-hot encoding sums to 0.
            if np.sum(grid[fx, fy, :]) == 0:
                new_state_forward = (fx, fy, direction)
                if new_state_forward not in visited:
                    new_cost = cost + 1
                    priority = new_cost + heuristic((fx, fy))
                    heapq.heappush(pq, (priority, new_cost, new_state_forward, path + [ACTION_UP]))

    return []  # Return an empty list if A* completes without finding a path.


print(evaluate())