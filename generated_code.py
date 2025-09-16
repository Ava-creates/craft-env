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
#   print(item, total_reward, actions_to_take)
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
    turn towards it, and craft the specified item.

    This function implements a robust strategy:
    1. Look up the recipe to find the required workshop and ingredients.
    2. Check if the agent's inventory has the required ingredients.
    3. Use Breadth-First Search (BFS) to find the shortest obstacle-avoiding
       path to an empty cell adjacent to the correct workshop.
    4. Convert the path into a sequence of move actions.
    5. Append a final move action to turn the agent towards the workshop.
    6. Append the 'USE' action to perform the craft.

    Args:
        env (CraftLab): The environment instance.
        item (str): The name of the item to craft.

    Returns:
        list[int]: A list of action integers, or an empty list if
                   crafting is not possible.
    """
    # 1. SETUP: Get required info from the environment and cookbook
    cookbook = env.world.cookbook
    state = env._current_state
    
    item_idx = cookbook.index[item]
    if item_idx is None:
        return []  # Item not recognized

    recipe = cookbook.recipes.get(item_idx)
    if recipe is None or '_at' not in recipe:
        return []  # Not a craftable item at a workshop

    # 2. INGREDIENT CHECK: Verify if the agent has the necessary materials
    inventory = state.inventory
    for ing_name, required_count in recipe.items():
        if ing_name == '_at':
            continue
        ing_idx = cookbook.index[ing_name]
        if inventory[ing_idx] < required_count:
            return []  # Missing ingredients

    # 3. LOCATE WORKSHOPS AND TARGETS
    workshop_name = recipe['_at']
    workshop_idx = cookbook.index[workshop_name]
    grid = state.grid
    width, height, _ = grid.shape

    workshop_locations = np.argwhere(grid[:, :, workshop_idx] == 1)
    if workshop_locations.shape[0] == 0:
        return []  # Required workshop not found on the map

    # A target cell is an empty cell adjacent to a workshop.
    # Map from target_cell -> workshop_cell for easy lookup.
    target_map = {}
    for ws_pos_arr in workshop_locations:
        ws_pos = tuple(ws_pos_arr)
        # Check neighbors (x,y)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adj_pos = (ws_pos[0] + dx, ws_pos[1] + dy)
            if 0 <= adj_pos[0] < width and 0 <= adj_pos[1] < height:
                # An empty cell has a sum of 0 across the kinds axis
                if grid[adj_pos[0], adj_pos[1], :].sum() == 0:
                    if adj_pos not in target_map:
                        target_map[adj_pos] = ws_pos

    if not target_map:
        return []  # No accessible locations next to any workshop

    # 4. PATHFINDING (BFS)
    start_pos = tuple(state.pos)

    # If already at a target location, just turn and use.
    if start_pos in target_map:
        workshop_pos = target_map[start_pos]
        dx = workshop_pos[0] - start_pos[0]
        dy = workshop_pos[1] - start_pos[1]
        
        turn_action = -1
        # Action mapping: 0:DOWN(+y), 1:UP(-y), 2:LEFT(-x), 3:RIGHT(+x)
        if dx == 1: turn_action = 3  # Face RIGHT
        elif dx == -1: turn_action = 2 # Face LEFT
        elif dy == 1: turn_action = 0  # Face DOWN
        elif dy == -1: turn_action = 1 # Face UP
        
        return [turn_action, 4]  # action 4 is USE

    # Initialize BFS
    queue = collections.deque([(start_pos, [])])  # (position, path_of_actions)
    visited = {start_pos}

    path_to_target = None
    final_pos = None

    while queue:
        current_pos, path = queue.popleft()

        if current_pos in target_map:
            path_to_target = path
            final_pos = current_pos
            break

        # Move definitions: (dx, dy, action_to_get_there)
        moves = [(0, 1, 0), (0, -1, 1), (-1, 0, 2), (1, 0, 3)]  # DOWN, UP, LEFT, RIGHT
        
        for dx, dy, action in moves:
            next_pos = (current_pos[0] + dx, current_pos[1] + dy)
            
            if next_pos in visited:
                continue
            
            # Check bounds and obstacles
            if (0 <= next_pos[0] < width and 
                0 <= next_pos[1] < height and 
                grid[next_pos[0], next_pos[1], :].sum() == 0):
                
                visited.add(next_pos)
                new_path = path + [action]
                queue.append((next_pos, new_path))
                
    # 5. CONSTRUCT FINAL ACTION LIST
    if path_to_target is None:
        return []  # No path found

    workshop_pos = target_map[final_pos]

    # Determine the final turn action to face the workshop
    dx = workshop_pos[0] - final_pos[0]
    dy = workshop_pos[1] - final_pos[1]
    
    turn_action = -1
    if dx == 1: turn_action = 3  # Face RIGHT
    elif dx == -1: turn_action = 2 # Face LEFT
    elif dy == 1: turn_action = 0  # Face DOWN
    elif dy == -1: turn_action = 1 # Face UP

    actions = path_to_target + [turn_action, 4]  # Path, Turn, USE

    return actions


print(evaluate())