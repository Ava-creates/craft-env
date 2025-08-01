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
  """Improved version of `collect_v1` by tracking inventory in BFS visited states.
  
  This improvement makes the BFS more robust by including the agent's current
  inventory state as part of the 'visited' set key. This allows the algorithm
  to correctly find paths where collecting a tool (e.g., an axe as a grabbable item)
  is an intermediate step to then collect the target primitive (e.g., wood).
  The USE action is also explored generally, not just when facing the target primitive,
  to account for picking up such intermediate items.

  Args:
      env (env.CraftLab): The CraftLab object.
      primitive (str): The name of the primitive to collect.

  Returns:
      List[int]: A sequence of action indices to execute.
  """
  current_state = env._current_state
  world = env.world

  # 1. Get the primitive's integer ID from the cookbook.
  try:
    i_kind = world.cookbook.index[primitive.lower()]
  except KeyError:
    return []

  # 2. Check if the primitive is already in the agent's inventory.
  if current_state.inventory[i_kind] > 0:
      return []

  # 3. Semantic check: Determine if this primitive is generally collectible via 'USE'.
  is_collectible_via_use = (
      i_kind in world.grabbable_indices or 
      i_kind == world.water_index or 
      i_kind == world.stone_index
  )
  if not is_collectible_via_use:
    return []

  # 4. Define actions and direction deltas.
  action_map = env.action_specs()
  UP_ACT = action_map["UP"]
  DOWN_ACT = action_map["DOWN"]
  LEFT_ACT = action_map["LEFT"]
  RIGHT_ACT = action_map["RIGHT"]
  USE_ACT = action_map["USE"]
  move_actions = [UP_ACT, DOWN_ACT, LEFT_ACT, RIGHT_ACT]

  _DIR_TO_DELTA_FRONT = {
      0: (-1, 0),
      1: (0, 1),
      2: (1, 0),
      3: (0, -1)
  }

  def _get_turning_actions(current_dir: int, target_dir: int) -> list[int]:
      if current_dir == target_dir:
          return []
      diff = (target_dir - current_dir + 4) % 4
      if diff == 1:
          return [RIGHT_ACT]
      elif diff == 3:
          return [LEFT_ACT]
      else:
          return [RIGHT_ACT, RIGHT_ACT]

  # 5. Initialize BFS.
  q = collections.deque()
  visited = set()
  initial_inventory_tuple = tuple(current_state.inventory)
  q.append((current_state, []))
  visited.add((current_state.pos[0], current_state.pos[1], current_state.dir, initial_inventory_tuple))

  grid_width, grid_height, _ = current_state.grid.shape
  MAX_EXPLORED_STATES = grid_width * grid_height * 4 * 10 
  explored_states_count = 0

  # 6. BFS Loop.
  while q:
    state, path = q.popleft()
    explored_states_count += 1
    if explored_states_count > MAX_EXPLORED_STATES:
      continue 

    current_r, current_c = state.pos
    current_dir = state.dir

    if state.next_to(i_kind):
        for target_dir in range(4):
            dr, dc = _DIR_TO_DELTA_FRONT[target_dir]
            facing_r, facing_c = current_r + dr, current_c + dc

            if (0 <= facing_r < grid_width and 0 <= facing_c < grid_height and 
                state.grid[facing_r, facing_c, i_kind] == 1):
                
                turns_to_face = _get_turning_actions(current_dir, target_dir)
                temp_state_after_turns = state 
                for turn_action in turns_to_face:
                    _, temp_state_after_turns = temp_state_after_turns.step(turn_action)

                inventory_before_use = np.copy(temp_state_after_turns.inventory)
                _, state_after_use = temp_state_after_turns.step(USE_ACT)

                if state_after_use.inventory[i_kind] > inventory_before_use[i_kind]:
                    return path + turns_to_face + [USE_ACT]

    for action in move_actions:
      _, next_state = state.step(action)
      next_inventory_tuple = tuple(next_state.inventory)
      next_state_key = (next_state.pos[0], next_state.pos[1], next_state.dir, next_inventory_tuple)
      if next_state_key not in visited:
        visited.add(next_state_key)
        q.append((next_state, path + [action]))

    inventory_before_any_use = np.copy(state.inventory)
    _, state_after_current_use = state.step(USE_ACT)
    if not (np.array_equal(state_after_current_use.inventory, inventory_before_any_use) and
            state_after_current_use.pos == state.pos and
            state_after_current_use.dir == state.dir):
        next_inventory_tuple = tuple(state_after_current_use.inventory)
        next_state_key = (state_after_current_use.pos[0], state_after_current_use.pos[1], state_after_current_use.dir, next_inventory_tuple)
        if next_state_key not in visited:
            visited.add(next_state_key)
            q.append((state_after_current_use, path + [USE_ACT]))

  # 7. Primitive is unreachable.
  return []





print(evaluate())