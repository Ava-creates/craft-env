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
  print(primitive, total_reward, actions_to_take)
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
# @funsearch.evolve
# def collect(env, primitive) -> list[int]:
#     MAX_STEPS = 40
#     UP, DOWN, LEFT, RIGHT, USE = 0, 1, 2, 3, 4

#     action_list = []
#     state = env._current_state
#     target_index = state.world.cookbook.index[primitive]

#     # Priority queue for BFS (position, steps, inventory, actions)
#     queue = collections.deque([(state.pos, 0, np.copy(state.inventory), [])])
#     visited = set()
#     print(state.pos)
#     while queue:
#         pos, steps, inv, actions = queue.popleft()
#         # print(pos, steps, actions)
#         if steps >= MAX_STEPS:
#             continue

#         # Check if the position and inventory have been visited
#         state_key = (tuple(pos), tuple(inv))
#         if state_key in visited:
#             continue
#         visited.add(state_key)

#         # Create a new state object for the current BFS step
#         state = craft.CraftState(
#             scenario=state.scenario,
#             grid=np.copy(state.grid),
#             pos=pos,
#             dir=state.dir,
#             inventory=np.copy(inv)
#         )

#         # # Check if the target primitive is next to the agent
#         adjacent_cells = [
#             (pos[0], pos[1] - 1),  # UP
#             (pos[0], pos[1] + 1),  # DOWN
#             (pos[0] - 1, pos[1]),  # LEFT
#             (pos[0] + 1, pos[1])   # RIGHT
#         ]


#         for adj_pos in adjacent_cells:
#             if 0 <= adj_pos[0] < state.grid.shape[0] and 0 <= adj_pos[1] < state.grid.shape[1]:
#                 cell_index = np.argmax(state.grid[adj_pos])

#                 if cell_index == target_index:
#                     action_list = actions + [UP, USE] if adj_pos[1] < pos[1] else\
#                                 actions + [DOWN, USE] if adj_pos[1] > pos[1] else\
#                                 actions + [LEFT, USE] if adj_pos[0] < pos[0] else\
#                                 actions + [RIGHT, USE]
#                     return action_list, 0, action_list

#         # Generate possible moves
#         for i, new_pos in enumerate(adjacent_cells):
#             if 0 <= new_pos[0] < state.grid.shape[0] and 0 <= new_pos[1] < state.grid.shape[1]:
#                 cell_index = np.argmax(state.grid[new_pos])
#                 if cell_index not in state.world.non_grabbable_indices:
#                     queue.append((new_pos, steps + 1, inv, actions + [i]))

#         # Check for tool usage
#         # print(inv)
#         inventory_items = np.where(inv > 0)[0]
#         # print(inventory_items)
#         for item_idx in inventory_items:

#             tool_usage_conditions = {
#                 'gold': ('bridge', 'water'),
#                 'GEM': ('PICKAXE', 'ROCK'),
#                 'TREE': ('AXE', 'TREE'),
#                 'BOULDER': ('HAMMER', 'BOULDER'),
#                 'IRON_ORE': ('DRILL', 'IRON_ORE'),
#                 'BUSH': ('SHEARS', 'BUSH'),
#                 'STONE': ('HAMMER', 'STONE'),
#             }

#             if primitive in tool_usage_conditions:

#                 required_tool, target_resource = tool_usage_conditions[primitive]
#                 # print("bridge index", state.world.cookbook.index[required_tool])
#                 if item_idx == state.world.cookbook.index[required_tool]:
#                     for dir_idx, adj_pos in enumerate(adjacent_cells):
#                         if 0 <= adj_pos[0] < state.grid.shape[0] and 0 <= adj_pos[1] < state.grid.shape[1]:
#                             cell_index = np.argmax(state.grid[adj_pos])
#                             if cell_index == state.world.cookbook.index[target_resource]:
#                                 new_inv = inv.copy()
#                                 queue.append((adj_pos, steps + 2, new_inv, actions + [dir_idx, USE]))

#     return [], -1, []  # Return empty list and negative reward if target is unreachable



def collect(env, primitive):
    """
    Returns a sequence of actions to collect a specified primitive.

    This function computes a shortest path to a target primitive using a Breadth-First Search (BFS).
    It handles obstacles like water or rock by using tools available in the agent's inventory
    (e.g., using a bridge to cross water or a pickaxe to break a rock). The BFS explores possible paths,
    accounting for changes in the environment (grid) and the agent's inventory when a tool is used.

    The state tracked in the BFS is a tuple containing the agent's position, the current
    grid layout, the current inventory, and the sequence of actions taken to reach this state.
    This ensures that each search branch operates on an independent and correct version of the world.

    Args:
        env (env.CraftLab): The CraftLab environment instance.
        primitive (str): The name of the primitive to collect (e.g., 'WOOD', 'GOLD').

    Returns:
        List[int]: A sequence of action indices to navigate to and collect the primitive.
                   Returns an empty list if the primitive is unreachable.
    """
    # Action constants
    UP, DOWN, LEFT, RIGHT, USE = 0, 1, 2, 3, 4

    # Get initial state and references to world components
    initial_state = env._current_state
    cookbook = initial_state.world.cookbook

    try:
        target_index = cookbook.index[primitive]
    except KeyError:
        return [] # Primitive does not exist in this world's recipes

    # Define which tools can clear which obstacles by mapping their names.
    # This is robust to whether these items actually exist in a given scenario.
    obstacle_to_tool_map = {}
    tool_map_definitions = [
        ('water', 'bridge'),
        ('rock', 'pickaxe'),
        ('stone', 'pickaxe'), # Assuming pickaxe also works on stone
        ('tree', 'axe'),
        ('boulder', 'hammer')
    ]
    for obstacle_name, tool_name in tool_map_definitions:
        if obstacle_name in cookbook.index and tool_name in cookbook.index:
            obstacle_to_tool_map[cookbook.index[obstacle_name]] = cookbook.index[tool_name]

    # Map actions to coordinate deltas for movement
    action_to_delta = {
        UP: (0, -1),
        DOWN: (0, 1),
        LEFT: (-1, 0),
        RIGHT: (1, 0),
    }

    # --- BFS Setup ---
    # State: (position, grid_state, inventory_state, actions_list)
    start_pos = initial_state.pos
    start_grid = initial_state.grid.copy()
    start_inventory = initial_state.inventory.copy()
    
    queue = collections.deque([(start_pos, start_grid, start_inventory, [])])
    
    # Visited set prevents cycles. Key: (position_tuple, inventory_tuple)
    # Inventory is part of the key because reaching a cell with different
    # tools is a fundamentally different and valid state to explore.
    visited = set([(start_pos, tuple(start_inventory))])

    while queue:
        pos, grid, inventory, actions = queue.popleft()

        # --- 1. Goal Check ---
        # Check if the target primitive is in an adjacent cell.
        for move_action, (dx, dy) in action_to_delta.items():
            adj_pos = (pos[0] + dx, pos[1] + dy)

            if not (0 <= adj_pos[0] < grid.shape[0] and 0 <= adj_pos[1] < grid.shape[1]):
                continue

            # If the adjacent cell has our target, we've found a path.
            if np.argmax(grid[adj_pos]) == target_index:
                # The final sequence is to face the target and then USE.
                return actions + [move_action, USE]

        # --- 2. Explore Neighbors ---
        for move_action, (dx, dy) in action_to_delta.items():
            next_pos = (pos[0] + dx, pos[1] + dy)

            if not (0 <= next_pos[0] < grid.shape[0] and 0 <= next_pos[1] < grid.shape[1]):
                continue

            # --- Case A: Next cell is empty ---
            if not np.any(grid[next_pos]):
                state_key = (next_pos, tuple(inventory))
                if state_key not in visited:
                    visited.add(state_key)
                    # For a simple move, grid and inventory don't change.
                    queue.append((next_pos, grid, inventory, actions + [move_action]))

            # --- Case B: Next cell is a clearable obstacle ---
            else:
                obstacle_index = np.argmax(grid[next_pos])
                required_tool_index = obstacle_to_tool_map.get(obstacle_index)

                # Check if we have the necessary tool for this obstacle.
                if required_tool_index is not None and inventory[required_tool_index] > 0:
                    # Create the new state that results from clearing the obstacle and moving.
                    new_inventory = inventory.copy()
                    new_inventory[required_tool_index] -= 1
                    
                    new_grid = grid.copy()
                    new_grid[next_pos].fill(0) # Clear the obstacle from the grid.

                    # The action sequence to clear and move is: face, use, move.
                    new_actions = actions + [move_action, USE, move_action]
                    
                    state_key = (next_pos, tuple(new_inventory))
                    if state_key not in visited:
                        visited.add(state_key)
                        queue.append((next_pos, new_grid, new_inventory, new_actions))

    # If the queue is exhausted, the target is unreachable with the current inventory.
    return []

    # Get the current state and world information
  # state = env._current_state
  # world = state.world

  # # Get the index for the primitive we need to collect
  # primitive_index = world.cookbook.index.index(primitive)

  # def bfs(start_pos, goal_index):
  #     """Performs a breadth-first search to find the shortest path from start_pos to the nearest cell containing goal_index."""
  #     queue = collections.deque([(start_pos, [])])
  #     visited = set([start_pos])

  #     while queue:
  #         (x, y), path = queue.popleft()
          
  #         # Check if we are at a goal
  #         if state.grid[x, y].argmax() == goal_index:
  #             return path

  #         # Explore neighbors
  #         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
  #             nx, ny = x + dx, y + dy
  #             if 0 <= nx < state.grid.shape[0] and 0 <= ny < state.grid.shape[1]:
  #                 if (nx, ny) not in visited:
  #                     visited.add((nx, ny))
  #                     new_path = path + [get_action(dx, dy)]
  #                     queue.append(((nx, ny), new_path))
  #     return None

  # def get_action(dx, dy):
  #     """Returns the action index corresponding to the given direction change."""
  #     if dx == -1 and dy == 0:
  #         return env.action_specs()["LEFT"]
  #     elif dx == 1 and dy == 0:
  #         return env.action_specs()["RIGHT"]
  #     elif dx == 0 and dy == -1:
  #         return env.action_specs()["DOWN"]
  #     elif dx == 0 and dy == 1:
  #         return env.action_specs()["UP"]
  #     return None

  # # Find the shortest path to collect the primitive
  # path = bfs(state.pos, primitive_index)
  # if path is not None:
  #     return path + [env.action_specs()["USE"]]
  # else:
  #     return []
  # Return empty list and negative reward if target is unreachable



print(evaluate())