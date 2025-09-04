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


def collect(env, primitive) -> list[int]:
    MAX_STEPS = 100
    UP, DOWN, LEFT, RIGHT, USE = 0, 1, 2, 3, 4

    action_list = []
    state = env._current_state
    target_index = state.world.cookbook.index[primitive]

    queue = collections.deque([(state.pos, 0, np.copy(state.inventory), [])])
    visited = set()
    # print(state.pos)
    while queue:
        pos, steps, inv, actions = queue.popleft()
        # print(pos, steps, actions)
        if steps >= MAX_STEPS:
            continue

        # Check if the position and inventory have been visited
        state_key = (tuple(pos), tuple(inv))
        if state_key in visited:
            continue
        visited.add(state_key)

        # Create a new state object for the current BFS step
        state = craft.CraftState(
            scenario=state.scenario,
            grid=np.copy(state.grid),
            pos=pos,
            dir=state.dir,
            inventory=np.copy(inv)
        )

        # # Check if the target primitive is next to the agent
        adjacent_cells = [
            (pos[0], pos[1] - 1),  # UP
            (pos[0], pos[1] + 1),  # DOWN
            (pos[0] - 1, pos[1]),  # LEFT
            (pos[0] + 1, pos[1])   # RIGHT
        ]


        for adj_pos in adjacent_cells:
            if 0 <= adj_pos[0] < state.grid.shape[0] and 0 <= adj_pos[1] < state.grid.shape[1]:
                cell_index = np.argmax(state.grid[adj_pos])

                if cell_index == target_index:
                    action_list = actions + [UP, USE] if adj_pos[1] < pos[1] else\
                                actions + [DOWN, USE] if adj_pos[1] > pos[1] else\
                                actions + [LEFT, USE] if adj_pos[0] < pos[0] else\
                                actions + [RIGHT, USE]
                    # print(action_list)
                    return action_list

        # Generate possible moves
        for i, new_pos in enumerate(adjacent_cells):
            if 0 <= new_pos[0] < state.grid.shape[0] and 0 <= new_pos[1] < state.grid.shape[1]:
                cell_index = np.argmax(state.grid[new_pos])
                if cell_index not in state.world.non_grabbable_indices:
                    queue.append((new_pos, steps + 1, inv, actions + [i]))

        # Check for tool usage
        # print(inv)
        inventory_items = np.where(inv > 0)[0]
        # print(inventory_items)
        for item_idx in inventory_items:

            tool_usage_conditions = {
                'gold': ('bridge', 'water'),
                'GEM': ('PICKAXE', 'ROCK'),
                'TREE': ('AXE', 'TREE'),
                'BOULDER': ('HAMMER', 'BOULDER'),
                'IRON_ORE': ('DRILL', 'IRON_ORE'),
                'BUSH': ('SHEARS', 'BUSH'),
                'STONE': ('HAMMER', 'STONE'),
            }

            if primitive in tool_usage_conditions:

                required_tool, target_resource = tool_usage_conditions[primitive]
                # print("bridge index", state.world.cookbook.index[required_tool])
                if item_idx == state.world.cookbook.index[required_tool]:
                    for dir_idx, adj_pos in enumerate(adjacent_cells):
                        if 0 <= adj_pos[0] < state.grid.shape[0] and 0 <= adj_pos[1] < state.grid.shape[1]:
                            cell_index = np.argmax(state.grid[adj_pos])
                            if cell_index == state.world.cookbook.index[target_resource]:
                                new_inv = inv.copy()
                                queue.append((adj_pos, steps + 2, new_inv, actions + [dir_idx, USE]))
    
    return []  # Return empty list and negative reward if target is unreachable



print(evaluate())