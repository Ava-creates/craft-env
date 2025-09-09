# -*- coding: utf-8 -*-
import numpy as np
import time
import collections
import env_factory

def solve(env, item, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = craft(env, item)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break
  print(item, total_reward, actions_to_take)
  return total_reward

def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  #max reward is 6 for this fucntion so any craft objet that can get when it is working properly
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"     
  reward = 0 
  for i in range(11):
    if(i == 0):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item,  visualise=visualise) #should give +1
    
    elif(i==1):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise)  #should give 0 when it is working properly
      if temp_reward>0 :
        reward -= 0.3
      
    elif(i==2):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  # 0 when working properly

    elif(i==3):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise) # 0 when working properly 
      if temp_reward>0 :
        reward -= 0.3

    elif(i==4):
      item = "plank"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[plank]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise) # +1 this does nnot work need to collect more before crafting

    elif(i==5):
      item = "cloth"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 3, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[cloth]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  #+1


    elif(i==6):
      item = "rope"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 4, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[rope]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise) #+1

    elif(i==7):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  #+1

    elif(i==8):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)

      temp_reward = solve(env, item, visualise=visualise)
      if temp_reward>0 :
        reward -= 0.3

    elif(i==9):
      item = "goldarrow"
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
      reward += solve(env, item, visualise=visualise)  # +1

    else:
      recipes_path_2 = "resources/recipes_for_synth.yaml"
      item = "arrow"
      env_sampler = env_factory.EnvironmentFactory(
            recipes_path_2, hints_path, 6, max_steps=100, 
            reuse_environments=False, visualise=False)
      env=env_sampler.sample_environment(task_name='make[arrow]')
      env.reset()
      # Actions to execute:
      env.step(0)
      env.step(2)
      env.step(2)
      env.step(4)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(2)
      env.step(4)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward+=solve(env, item, visualise=visualise) 
      
  return reward
  


def craft(env, item):
    """
    Generates a sequence of actions to move to the correct workshop,
    face it, and craft the specified item.
    """
    cookbook = env.world.cookbook
    state = env._current_state
    grid = state.grid
    start_pos = tuple(state.pos)

    # 1. Get Recipe & Required Workshop from the cookbook
    goal_index = cookbook.index[item]
    if goal_index is None:
        raise ValueError(f"Unknown item: {item}")

    recipe = cookbook.recipes.get(goal_index)
    if not recipe:
        raise ValueError(f"No recipe found for item: {item}")

    workshop_name = recipe.get('_at')
    if not workshop_name:
        raise ValueError(f"Recipe for {item} does not specify a workshop.")
    
    required_workshop_idx = cookbook.index[workshop_name]
    if required_workshop_idx is None:
        raise ValueError(f"Unknown workshop: {workshop_name}")

    # 2. Find all valid target cells (empty cells adjacent to the correct workshop)
    workshop_locations = np.argwhere(grid[:, :, required_workshop_idx])
    if workshop_locations.size == 0:
        raise ValueError(f"No '{workshop_name}' found on the grid.")

    # Map of {agent_target_pos: corresponding_workshop_pos}
    target_map = {}
    for wx, wy in workshop_locations:
        # Check 4-directional neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = wx + dx, wy + dy
            # Check if neighbor is valid and empty
            if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1] and not np.any(grid[nx, ny, :]):
                target_map[(nx, ny)] = (wx, wy)
    
    if not target_map:
        raise ValueError(f"No accessible cells next to any '{workshop_name}'.")
    
    # 3. Pathfinding using Breadth-First Search (BFS)
    # The BFS finds the shortest path of actions to the nearest valid target cell.
    
    # Action mapping: 0=DOWN, 1=UP, 2=LEFT, 3=RIGHT
    # Maps a delta (dx, dy) to a specific action
    action_map = {(0, -1): 0, (0, 1): 1, (-1, 0): 2, (1, 0): 3}
    
    # Queue stores tuples of (current_position, list_of_actions_to_get_here)
    queue = collections.deque([(start_pos, [])])
    visited = {start_pos}
    
    path_actions = []
    final_agent_pos = None
    final_workshop_pos = None

    # Handle edge case: agent is already next to the workshop
    if start_pos in target_map:
        path_actions = []
        final_agent_pos = start_pos
        final_workshop_pos = target_map[start_pos]
    else:
        found_path = False
        while queue:
            (cx, cy), current_actions = queue.popleft()

            # Explore neighbors
            for (dx, dy), action in action_map.items():
                nx, ny = cx + dx, cy + dy
                
                if (nx, ny) in visited:
                    continue
                
                # Check boundaries and if the cell is empty (not an obstacle)
                is_valid = (0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1])
                if is_valid and not np.any(grid[nx, ny, :]):
                    visited.add((nx, ny))
                    new_actions = current_actions + [action]
                    
                    # If neighbor is a target, we found the shortest path
                    if (nx, ny) in target_map:
                        path_actions = new_actions
                        final_agent_pos = (nx, ny)
                        final_workshop_pos = target_map[(nx, ny)]
                        found_path = True
                        break 
                    
                    queue.append(((nx, ny), new_actions))
            if found_path:
                break

    if final_agent_pos is None:
        raise RuntimeError(f"Could not find a path to a '{workshop_name}'.")

    # 4. Generate Final Turn and USE Actions
    actions = list(path_actions)
    
    agent_x, agent_y = final_agent_pos
    workshop_x, workshop_y = final_workshop_pos

    # Determine direction to face and the corresponding action.
    # This action "bumps" into the workshop, setting the agent's direction correctly.
    face_action = -1
    if workshop_y > agent_y: face_action = 1 # Face UP
    elif workshop_y < agent_y: face_action = 0 # Face DOWN
    elif workshop_x > agent_x: face_action = 3 # Face RIGHT
    elif workshop_x < agent_x: face_action = 2 # Face LEFT
    
    if face_action != -1:
        actions.append(face_action)
    
    # Finally, append the USE action to craft the item
    actions.append(4)

    return actions
print(evaluate()) 