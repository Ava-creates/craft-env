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
        
      reward += solve(env, primitive, visualise=visualise)

  return reward

# @funsearch.evolve
def collect(env, primitive) -> list[int]:
    """Improved version of `collect_v1`, ensuring 'collect' for grabbable items means acquiring them in inventory."""
    actions_to_take = []
    
    # 1. Get primitive index and check grabbability
    primitive_id = env.world.cookbook.index[primitive]
    print(primitive, primitive_id, env.task)
    # If the primitive name does not map to an ID, it's unknown.
    if primitive_id is None:
        return []

    initial_state = env._current_state

    # --- V1 Improvement: Check if primitive is already in inventory ---
    # If the primitive is already collected (present in inventory), no actions are needed.
    # This applies to grabbable items. For non-grabbable items like workshops,
    # the inventory check will be 0, so it will proceed to find a path to reach it.
    if initial_state.inventory[primitive_id] > 0:
        return []
    # --- End V1 Improvement ---

    # Determine if the primitive is grabbable (requires a USE action and adds to inventory)
    is_grabbable = primitive_id in env.world.grabbable_indices
    
    # Get action mappings from the environment
    action_map = env.action_specs()
    ACTION_UP = action_map["UP"]
    ACTION_DOWN = action_map["DOWN"]
    ACTION_LEFT = action_map["LEFT"]
    ACTION_RIGHT = action_map["RIGHT"]
    ACTION_USE = action_map["USE"]

    # 2. Initialize Breadth-First Search (BFS)
    # The queue stores tuples: (current_CraftState, list_of_actions_to_reach_this_state)
    path_queue = collections.deque([(initial_state, [])])
    
    # Keep track of visited states to prevent cycles and redundant exploration.
    # A state is uniquely defined by (agent_position_tuple, agent_direction_int).
    visited_states = set()
    visited_states.add((initial_state.pos, initial_state.dir))
    
    # Define possible movement actions
    possible_moves = [ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT]
    
    # Safety limit for BFS depth to prevent excessively long searches on large maps.
    max_search_iterations = initial_state.grid.shape[0] * initial_state.grid.shape[1] * 4 * 2 
    current_iterations = 0 
    
    while path_queue and current_iterations < max_search_iterations:
        current_sim_state, current_path = path_queue.popleft()
        current_iterations += 1

        # 3. Check if the goal condition is met for the current simulated state
        # The goal is to be next to (or on) the primitive's location.
        if current_sim_state.next_to(primitive_id):
            # --- V2 Improvement: Refined Goal Check for 'collect' ---
            if is_grabbable:
                # For grabbable items, "collect" implies successfully acquiring the item.
                # Simulate the USE action to check if it results in inventory change.
                _reward, state_after_use = current_sim_state.step(ACTION_USE)
                
                # If the primitive's count in inventory increased, then collection was successful.
                if state_after_use.inventory[primitive_id] > current_sim_state.inventory[primitive_id]:
                    current_path.append(ACTION_USE)  # Add the USE action to the path
                    return current_path  # Return this path as a solution
                # If USE did not result in collection, continue the BFS
            else:
                # For non-grabbable items, "collect" means simply reaching/being next to it.
                return current_path  # This path is a solution.
            # --- End V2 Improvement ---
        
        # 4. Explore possible next moves from the current state
        for action in possible_moves:
            _reward, next_sim_state = current_sim_state.step(action)
            next_state_tuple = (next_sim_state.pos, next_sim_state.dir)
            if next_state_tuple not in visited_states:
                visited_states.add(next_state_tuple)
                new_path = list(current_path) + [action]
                path_queue.append((next_sim_state, new_path))
                
    # If no valid path found
    return []




print(evaluate())