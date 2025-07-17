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
  
    """
    Returns a list of actions that we will take to craft the item at the item_index.
    Crafting an item requires collecting the primitives/items needed and then going to one of the workshops to craft the item.

    Parameters:
    - env: CraftLab environment object
    - item_index: Index of the item to be crafted

    Returns:
    - List of actions (integers) to craft the item.
    """
    # Get the primitives required for the specified item index
    cookbook = env.world.cookbook
    primitives_needed = cookbook.primitives_for(item_index)
    
    action_sequence = []
    
    def collect_item(kind):
        """
        Collects items of a given kind until we have enough.

        Parameters:
        - kind: Index of the item kind to be collected

        Returns:
        - List of actions (integers) to collect the item.
        """
        actions = []
        while primitives_needed[kind] > 0:
            # Move and collect items
            for _ in range(5):  # Example: move around and collect in a small area
                actions.extend([env.action_specs()['LEFT'], env.action_specs()['USE']])
            primitives_needed[kind] -= 1  # Decrement the count as we assume collection
        return actions
    
    def go_to_workshop():
        """
        Moves to one of the workshops.

        Returns:
        - List of actions (integers) to move to a workshop.
        """
        # Example: Move in a specific pattern to reach a workshop
        actions = [env.action_specs()['UP'], env.action_specs()['UP'],
                   env.action_specs()['RIGHT'], env.action_specs()['USE']]
        return actions
    
    # Collect all needed primitives
    for kind, count in primitives_needed.items():
        action_sequence.extend(collect_item(kind))
    
    # Move to a workshop and craft the item
    action_sequence.extend(go_to_workshop())
    action_sequence.append(env.action_specs()['USE'])  # Craft the item at the workshop
    
    return action_sequence


print(evaluate())