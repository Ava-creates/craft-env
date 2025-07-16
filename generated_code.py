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
    
    # Dictionary mapping item indices to their crafting recipes
    cookbook = env.world.cookbook.recipes
    
    # Get the recipe for the desired item
    recipe = cookbook[item_index]
    
    # Initialize a list to hold actions
    actions = []
    
    # Collect all primitives needed for the recipe
    for primitive, count in recipe.items():
        if isinstance(primitive, int):  # Ignore "_at" and "_yield"
            while env._current_state.inventory[primitive] < count:
                if env._current_state.next_to(primitive):
                    actions.append(env.action_specs()['USE'])
                else:
                    # Move towards the primitive (assuming we have a simple heuristic to find it)
                    actions.extend(move_towards_primitive(env, primitive))
    
    # Go to the workshop where the item can be crafted
    workshop = recipe["_at"]
    workshop_index = env.world.cookbook.index[workshop]
    while not env._current_state.next_to(workshop_index):
        # Move towards the workshop (assuming we have a simple heuristic to find it)
        actions.extend(move_towards_workshop(env, workshop_index))
    
    # Craft the item at the workshop
    actions.append(env.action_specs()['USE'])
    
    return actions


print(evaluate())