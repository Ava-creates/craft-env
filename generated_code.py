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
    Generates a sequence of actions to find, move to, and collect a specified primitive.

    This function implements a Breadth-First Search (BFS) algorithm to navigate the agent
    to a position where it can collect the target primitive. It is designed to be robust
    by addressing the specific mechanics of the Craft environment:

    1.  **Pathfinding Goal**: The agent cannot occupy the same cell as a resource (e.g., a
        tree). Therefore, the BFS finds a path to a walkable cell *adjacent* to the
        target primitive.

    2.  **Directional Collection**: The 'USE' action is directional. To collect the
        primitive, the agent must be adjacent to it and facing it. This implementation
        assumes a "bump-to-turn" mechanic, where attempting to move into the blocked
        resource cell orients the agent correctly.

    The algorithm is as follows:
    - Identify all grid locations of the target primitive.
    - Find all valid, walkable cells adjacent to these locations; these are the goals.
    - Run BFS from the agent's current position to find the shortest path to any goal cell.
    - Once the agent reaches a goal cell, determine the direction towards the primitive.
    - Append a final movement action (the "bump") to face the primitive, followed by the
      'USE' action to collect it.
    """
    # Step 1: Initialize state variables from the environment
    current_state = env._current_state
    world = current_state.world
    grid = current_state.grid
    start_pos = current_state.pos

    try:
        primitive_index = world.cookbook.index[primitive]
    except KeyError:
        return []  # Invalid primitive name

    # Define action constants based on environment specification
    ACTION_DOWN, ACTION_UP, ACTION_LEFT, ACTION_RIGHT, ACTION_USE = 0, 1, 2, 3, 4

    # Map actions to coordinate changes (dx=row_change, dy=col_change)
    action_to_delta = {
        ACTION_DOWN: (1, 0),
        ACTION_UP: (-1, 0),
        ACTION_LEFT: (0, -1),
        ACTION_RIGHT: (0, 1),
    }

    # Step 2: Find all primitive locations and their adjacent, walkable goal cells
    target_coords = np.argwhere(grid[:, :, primitive_index] == 1)
    if target_coords.size == 0:
        return []  # Primitive not found on the map

    adjacent_goals = set()
    goal_to_target_map = {}  # Map goal cells back to their target for orientation

    for tx, ty in target_coords:
        for action, (dx, dy) in action_to_delta.items():
            # An adjacent cell is where the agent must be to perform the action
            ax, ay = tx - dx, ty - dy
            adj_pos = (ax, ay)

            # Check if the adjacent cell is within bounds and walkable
            if (0 <= ax < grid.shape[0] and 0 <= ay < grid.shape[1]):
                kind_at_adj = np.argmax(grid[ax, ay])
                if kind_at_adj not in world.non_grabbable_indices:
                    adjacent_goals.add(adj_pos)
                    if adj_pos not in goal_to_target_map:
                        goal_to_target_map[adj_pos] = (tx, ty)

    if not adjacent_goals:
        return []  # No accessible cells next to the primitive

    # Step 3: BFS to find the shortest path to a goal cell
    path_to_adjacent = None
    final_pos = None

    if start_pos in adjacent_goals:
        path_to_adjacent = []
        final_pos = start_pos
    else:
        queue = collections.deque([(start_pos, [])])
        visited = {start_pos}

        while queue:
            (cx, cy), path = queue.popleft()

            for action, (dx, dy) in action_to_delta.items():
                nx, ny = cx + dx, cy + dy
                next_pos = (nx, ny)

                if next_pos in visited:
                    continue
                
                # Check grid bounds and walkability for the next step
                if (0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]):
                    kind_at_next = np.argmax(grid[nx, ny])
                    if kind_at_next not in world.non_grabbable_indices:
                        new_path = path + [action]
                        if next_pos in adjacent_goals:
                            path_to_adjacent = new_path
                            final_pos = next_pos
                            queue.clear()  # Shortest path found, terminate search
                            break
                        
                        visited.add(next_pos)
                        queue.append((next_pos, new_path))
    
    if path_to_adjacent is None:
        return []  # No path could be found

    # Step 4: Determine final orientation ("bump") and USE actions
    full_path = list(path_to_adjacent)
    (gx, gy) = final_pos
    (tx, ty) = goal_to_target_map[final_pos]

    # Calculate the action required to face the target from the adjacent goal position
    required_turn_action = -1
    if (tx, ty) == (gx - 1, gy): # Target is UP
        required_turn_action = ACTION_UP
    elif (tx, ty) == (gx + 1, gy): # Target is DOWN
        required_turn_action = ACTION_DOWN
    elif (tx, ty) == (gx, gy - 1): # Target is LEFT
        required_turn_action = ACTION_LEFT
    elif (tx, ty) == (gx, gy + 1): # Target is RIGHT
        required_turn_action = ACTION_RIGHT

    if required_turn_action != -1:
        full_path.append(required_turn_action)
        full_path.append(ACTION_USE)
    
    return full_path


print(evaluate())