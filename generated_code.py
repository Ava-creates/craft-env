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
 
    """Crafting an item requires collecting the primitives/items needed and then going to one of the workshops to craft the item.
    
    This function crafts the given item by:
    - Collecting all necessary primitives for crafting the item
    - Going to a workshop and using the primitives to craft the item
    
    Args:
        env (CraftLab): The environment in which the agent operates.
        item_index (int): Index of the item to be crafted in the cookbook.
        
    Returns:
        list[int]: A sequence of actions that will lead to crafting the desired item.
    """
    
    # Access the world and cookbook from the environment
    world = env.world
    cookbook = world.cookbook
    
    # Get primitives needed for the given item_index
    needed_primitives = cookbook.primitives_for(item_index)
    
    action_sequence = []
    
    # Collect all necessary primitives
    for primitive, count in needed_primitives.items():
        while np.sum(env._current_state.inventory[primitive]) < count:
            # Check if we are next to the primitive
            if env._current_state.next_to(primitive):
                action_sequence.append(env.action_specs()['USE'])
            else:
                # Move randomly to find the primitive (simple strategy)
                direction = np.random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                action_sequence.append(env.action_specs()[direction])
                
    # Go to a workshop and use primitives to craft the item
    for workshop in range(3):  # Assuming there are 3 workshops indexed 0, 1, 2
        if env._current_state.next_to(world.cookbook.index[f"WORKSHOP{workshop}"]):
            action_sequence.append(env.action_specs()['USE'])
            break
        else:
            # Move randomly to find a workshop (simple strategy)
            direction = np.random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            action_sequence.append(env.action_specs()[direction])
    
    return action_sequence


print(evaluate())