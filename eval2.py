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
    # """
    # Returns a sequence of actions to collect a specified primitive.

    # This function computes a shortest path to a target primitive using a Breadth-First Search (BFS).
    # It handles obstacles like water or rock by using tools available in the agent's inventory
    # (e.g., using a bridge to cross water or a pickaxe to break a rock). The BFS explores possible paths,
    # accounting for changes in the environment (grid) and the agent's inventory when a tool is used.

    # The state tracked in the BFS is a tuple containing the agent's position, the current
    # grid layout, the current inventory, and the sequence of actions taken to reach this state.
    # This ensures that each search branch operates on an independent and correct version of the world.

    # Args:
    #     env (env.CraftLab): The CraftLab environment instance.
    #     primitive (str): The name of the primitive to collect (e.g., 'WOOD', 'GOLD').

    # Returns:
    #     List[int]: A sequence of action indices to navigate to and collect the primitive.
    #                Returns an empty list if the primitive is unreachable.
    # """
    # # Step 1: Extract the current state from the environment
    # current_state = env._current_state

    # # Step 2: Identify the index of the primitive to collect
    # primitive_index = current_state.world.cookbook.index[primitive]

    # # Step 3: Define a simple BFS (Breadth-First Search) algorithm to find the shortest path
    # def bfs(start_pos, target_kind):
    #     """Performs Breadth-First Search to find the shortest path to a cell with the target kind."""
    #     queue = collections.deque([(start_pos, [])])
    #     visited = set()
    #     while queue:
    #         (x, y), path = queue.popleft()
    #         if (x, y) in visited:
    #             continue
    #         visited.add((x, y))
    #         # Check all four possible directions: UP, DOWN, LEFT, RIGHT
    #         for dx, dy, action in [(-1, 0, 2), (1, 0, 3), (0, -1, 0), (0, 1, 1)]:
    #             nx, ny = x + dx, y + dy
    #             # Ensure the new position is within bounds and not blocked by non-grabbable entities
    #             if 0 <= nx < current_state.grid.shape[0] and 0 <= ny < current_state.grid.shape[1]:
    #                 kind_index = np.argmax(current_state.grid[nx, ny])
    #                 if kind_index in current_state.world.non_grabbable_indices:
    #                     continue
    #                 new_path = path + [action]
    #                 # Check if the target primitive is found at this cell
    #                 if kind_index == target_kind:
    #                     return new_path
    #                 queue.append(((nx, ny), new_path))
    #     return []

    # # Step 4: Use the BFS to find a path to any cell containing the primitive
    # actions = bfs(current_state.pos, primitive_index)

    # # Step 5: Append the USE action to collect the primitive
    # if actions:
    #     actions.append(4)  # The index for the USE action

    # return actions

    """
    Computes a shortest path to collect a specified primitive using a stateful Breadth-First Search.

    This function finds the shortest sequence of actions for the agent to move
    adjacent to a target primitive and collect it. The search accounts for the
    agent's current position, inventory, and the grid layout.

    The agent can use tools from its inventory to overcome obstacles (e.g., using a
    'bridge' to cross 'water'). The BFS simulates these actions by tracking changes
    to the grid and inventory, allowing it to discover paths through cleared obstacles.

    The state in the BFS queue consists of:
    - pos (tuple): The agent's (x, y) coordinates.
    - inventory (np.ndarray): The agent's current inventory.
    - grid (np.ndarray): The current state of the world grid for that search branch.
    - actions (list): The sequence of actions taken to reach this state.

    The search terminates upon finding a path that places the agent next to the
    target primitive, returning the full action sequence, including the final 'USE'
    action. If no path is found, it returns an empty list.

    Args:
        env (env.CraftLab): The CraftLab environment instance, providing access to the current state.
        primitive (str): The name of the primitive to collect (e.g., 'wood', 'gold').

    Returns:
        List[int]: A list of action indices to collect the primitive, or an empty
                   list if it's unreachable.
    """
    UP, DOWN, LEFT, RIGHT, USE = 0, 1, 2, 3, 4
    
    initial_state = env._current_state
    world = initial_state.world
    cookbook = world.cookbook
    grid_shape = initial_state.grid.shape

    try:
        target_idx = cookbook.index[primitive]
        water_idx = cookbook.index['water']
        bridge_idx = cookbook.index['bridge']
        stone_idx = cookbook.index['stone']
        axe_idx = cookbook.index['axe']
    except KeyError:
        # This occurs if a required item like 'water' or the primitive itself isn't in the cookbook.
        return []

    # Map obstacles to the tools required to clear them
    tool_for_obstacle = {
        water_idx: bridge_idx,
        stone_idx: axe_idx
    }

    # BFS queue stores tuples of: (position, inventory, grid, actions)
    queue = collections.deque([
        (
            initial_state.pos,
            initial_state.inventory.copy(),
            initial_state.grid.copy(),
            []
        )
    ])
    
    # Visited set prevents cycles and redundant computations.
    # The key includes position, inventory, and the grid state.
    visited = set()
    initial_state_key = (initial_state.pos, tuple(initial_state.inventory), initial_state.grid.tobytes())
    visited.add(initial_state_key)

    # Map action indices to their corresponding (dx, dy) deltas
    action_deltas = {
        UP:    (0, -1),
        DOWN:  (0, 1),
        LEFT:  (-1, 0),
        RIGHT: (1, 0),
    }
    
    while queue:
        pos, inventory, grid, actions = queue.popleft()

        if len(actions) > 200:  # Safety break to prevent searching infinitely on complex maps
            continue

        # Explore neighbors by trying each directional action from the current position
        for action, (dx, dy) in action_deltas.items():
            neighbor_pos = (pos[0] + dx, pos[1] + dy)

            # Check if the neighbor is within the grid bounds
            if not (0 <= neighbor_pos[0] < grid_shape[0] and 0 <= neighbor_pos[1] < grid_shape[1]):
                continue
            
            # Identify the content of the neighbor cell
            cell_idx = np.argmax(grid[neighbor_pos])

            # Case 1: Neighbor is the target primitive. We found a solution.
            if cell_idx == target_idx:
                # To collect, the agent must face the target and USE. The `action` will turn
                # the agent. The subsequent move will be blocked by the resource, but the
                # agent will be correctly oriented for the USE action.
                return actions + [action, USE]

            # Case 2: Neighbor is an empty, traversable cell.
            if cell_idx == 0:
                new_pos = neighbor_pos
                new_actions = actions + [action]
                
                # The grid and inventory don't change for a simple move.
                state_key = (new_pos, tuple(inventory), grid.tobytes())
                if state_key not in visited:
                    visited.add(state_key)
                    queue.append((new_pos, inventory, grid, new_actions))

            # Case 3: Neighbor is an obstacle that can be cleared with a tool.
            elif cell_idx in tool_for_obstacle:
                required_tool_idx = tool_for_obstacle[cell_idx]
                
                # Check if the agent has the necessary tool in its inventory.
                if inventory[required_tool_idx] > 0:
                    # Simulate using the tool: agent stays at `pos`, but inventory and grid change.
                    new_inventory = inventory.copy()
                    new_inventory[required_tool_idx] -= 1
                    
                    new_grid = grid.copy()
                    # Clear the obstacle cell, making it empty (represented by a zero vector).
                    new_grid[neighbor_pos] = 0.0

                    # The action sequence is to face the obstacle and use the tool.
                    new_actions = actions + [action, USE]
                    
                    # This new search state starts from the *same position* but with an updated world.
                    state_key = (pos, tuple(new_inventory), new_grid.tobytes())
                    if state_key not in visited:
                        visited.add(state_key)
                        queue.append((pos, new_inventory, new_grid, new_actions))

    # If the queue becomes empty, no path was found.
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