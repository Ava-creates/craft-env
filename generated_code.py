import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 14 
  actions_to_take = craft_func(env, 14)
  print("actions", actions_to_take)
  observations = env.reset()
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    print(reward)
    total_reward += reward
    # print(env._current_state.satisfies(None, 14))
    if reward:
      rewarding_frame = observations['image'].copy()
      rewarding_frame[:40] *= np.array([0, 1, 0])
    elif done:
      break

  return total_reward


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"

  env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, max_steps=100, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[stick]')
  return solve(env, visualise=visualise)

def craft_func(env, item_index):
 
    """Craft the specified item by collecting required primitives and using a workshop."""
    
    # Define action indices
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3
    USE = 4
    
    actions = []
    
    # Get the recipe for the desired item
    cookbook = env.world.cookbook.recipes
    recipe = cookbook[item_index]
    
    # Collect required primitives
    required_primitives = {i: quantity for i, quantity in recipe.items() if isinstance(i, int)}
    
    # Function to move to a specific location (x, y)
    def move_to(x, y):
        current_x, current_y = env._current_state.pos
        dx, dy = x - current_x, y - current_y
        actions.extend([RIGHT] * dx if dx > 0 else [LEFT] * abs(dx))
        actions.extend([DOWN] * dy if dy > 0 else [UP] * abs(dy))
    
    # Collect each required primitive
    for primitive_index, quantity in required_primitives.items():
        while env._current_state.inventory[primitive_index] < quantity:
            # Find the nearest location of this primitive
            locations = np.argwhere(env._current_state.grid[:, :, primitive_index])
            if not locations.size:
                raise ValueError(f"No {env.world.cookbook.index.get(primitive_index)} found in the environment.")
            
            closest_location = min(locations, key=lambda loc: np.linalg.norm(np.array(loc) - np.array(env._current_state.pos)))
            move_to(*closest_location)
            
            # Collect the primitive
            actions.append(USE)
    
    # Move to a workshop and craft the item
    workshop_index = recipe["_at"]
    workshops = env.world.cookbook.recipes[workshop_index]
    closest_workshop = min(workshops, key=lambda loc: np.linalg.norm(np.array(loc) - np.array(env._current_state.pos)))
    move_to(*closest_workshop)
    
    # Craft the item
    actions.append(USE)
    
    return actions


print(evaluate())