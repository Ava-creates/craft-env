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
  state, reward, actions_to_take = collect(env, primitive)
  print(actions_to_take)
  observations = env.reset()
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break
  if total_reward > 0.5:
    return 0.3
  print(total_reward)
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
    MAX_STEPS = 100
    UP, DOWN, LEFT, RIGHT, USE = 0, 1, 2, 3, 4

    action_list = []
    state = env._current_state
    target_index = state.world.cookbook.index[primitive]

    # Priority queue for BFS (position, steps, inventory, actions)
    queue = collections.deque([(state.pos, 0, np.copy(state.inventory), [])])
    visited = set()

    while queue:
        pos, steps, inv, actions = queue.popleft()

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

        # Check if the target primitive is next to the agent
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
                    return action_list, 0, action_list

        # Generate possible moves
        for i, new_pos in enumerate(adjacent_cells):
            if 0 <= new_pos[0] < state.grid.shape[0] and 0 <= new_pos[1] < state.grid.shape[1]:
                cell_index = np.argmax(state.grid[new_pos])
                if cell_index not in state.world.non_grabbable_indices:
                    queue.append((new_pos, steps + 1, inv, actions + [i]))

        # Check for tool usage
        inventory_items = np.where(inv > 0)[0]
        for item_idx in inventory_items:
            tool_usage_conditions = {
                'GOLD': ('BRIDGE', 'WATER'),
                'GEM': ('PICKAXE', 'ROCK'),
                'TREE': ('AXE', 'TREE'),
                'BOULDER': ('HAMMER', 'BOULDER'),
                'IRON_ORE': ('DRILL', 'IRON_ORE'),
                'BUSH': ('SHEARS', 'BUSH'),
                'STONE': ('HAMMER', 'STONE'),
            }

            if primitive in tool_usage_conditions:
                required_tool, target_resource = tool_usage_conditions[primitive]
                if item_idx == state.world.cookbook.index[required_tool]:
                    for adj_pos in adjacent_cells:
                        if 0 <= adj_pos[0] < state.grid.shape[0] and 0 <= adj_pos[1] < state.grid.shape[1]:
                            cell_index = np.argmax(state.grid[adj_pos])
                            if cell_index == state.world.cookbook.index[target_resource]:
                                new_inv = inv.copy()
                                new_inv[item_idx] -= 1
                                queue.append((adj_pos, steps + 2, new_inv, actions + [USE]))

    return [], -1, []  # Return empty list and negative reward if target is unreachable


print(evaluate())