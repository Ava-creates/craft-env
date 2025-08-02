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
def collect(env, primitive):
  state = env._current_state
  cookbook = env.world.cookbook
  grid = state.grid  # Current grid state (static for pathfinding within this call)
  
  # 1. Get the integer ID for the primitive from the cookbook index
  primitive_idx = cookbook.index[primitive] 
  if primitive_idx is None:
    # Primitive name not found in cookbook, cannot collect.
    return []

  # Determine if the primitive is grabbable (i.e., can be held in inventory).
  # Grabbable items are things like WOOD, IRON, GRASS, etc., which require a 'USE' action.
  is_grabbable = primitive_idx in env.world.grabbable_indices
  
  # Optimization: If the primitive is grabbable and already in inventory, 
  # no collection actions are needed. The item is already "collected".
  if is_grabbable and state.inventory[primitive_idx] > 0:
    return []

  # Get action mappings for easier use
  action_map = env.action_specs()
  ACTION_UP = action_map['UP']
  ACTION_DOWN = action_map['DOWN']
  ACTION_LEFT = action_map['LEFT']
  ACTION_RIGHT = action_map['RIGHT']
  ACTION_USE = action_map['USE']

  # Grid dimensions (WIDTH, HEIGHT, n_kinds) for boundary checks
  WIDTH, HEIGHT, _ = grid.shape

  # Determine other properties of the target primitive for goal checking logic.
  is_workshop = primitive_idx in env.world.workshop_indices
  is_stationary_primitive = (primitive_idx == env.world.water_index or 
                             primitive_idx == env.world.stone_index or 
                             primitive_idx == cookbook.index['BOUNDARY'])
  
  # Breadth-First Search (BFS) setup
  q = collections.deque([(state.pos, state.dir, [])]) 
  visited = {(state.pos, state.dir)} 

  min_path_len = float('inf')
  best_path_actions = []

  while q:
    current_pos, current_dir, current_actions = q.popleft()

    if len(current_actions) >= min_path_len:
        continue

    is_goal_reached = False
    actions_to_complete_goal = []

    if is_grabbable:
      fwd_x, fwd_y = current_pos
      if current_dir == 0: fwd_y -= 1  # UP
      elif current_dir == 1: fwd_y += 1  # DOWN
      elif current_dir == 2: fwd_x -= 1  # LEFT
      elif current_dir == 3: fwd_x += 1  # RIGHT
      
      if 0 <= fwd_x < WIDTH and 0 <= fwd_y < HEIGHT:
        if grid[fwd_x, fwd_y, primitive_idx] > 0:
          is_goal_reached = True
          actions_to_complete_goal = [ACTION_USE] 

    elif is_workshop or is_stationary_primitive:
      if grid[current_pos[0], current_pos[1], primitive_idx] > 0:
        is_goal_reached = True
        actions_to_complete_goal = [] 

    if is_goal_reached:
      total_actions = current_actions + actions_to_complete_goal
      if len(total_actions) < min_path_len:
        min_path_len = len(total_actions)
        best_path_actions = total_actions

    for action_type in [ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT]:
      temp_state_for_step = craft.CraftState(
          state.scenario, state.grid, current_pos, current_dir, state.inventory
      )
      _, new_temp_state = temp_state_for_step.step(action_type)
      
      new_pos = new_temp_state.pos
      new_dir = new_temp_state.dir
      new_state_tuple = (new_pos, new_dir)

      if new_state_tuple not in visited:
        visited.add(new_state_tuple)
        q.append((new_pos, new_dir, current_actions + [action_type]))

  return best_path_actions




print(evaluate())