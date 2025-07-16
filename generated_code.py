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
 # TODO: Implement this function
    """Returns a list of actions that we will take to craft the item at the item_index. Crafting an item requires collecting the primitives/items needed and then going to one of the workshops to craft the item."""
    
    # Get the cookbook from the world environment
    cookbook = env.world.cookbook
    
    # Find the recipe for the desired item
    recipe = None
    for output, inputs in cookbook.recipes.items():
        if output == item_index:
            recipe = inputs
            break
            
    if recipe is None:
        raise ValueError(f"No recipe found for item index {item_index}")
        
    # Collect primitives needed for the recipe
    actions = []
    required_primitives = [i for i in recipe if isinstance(i, int)]
    required_counts = {primitive: recipe[primitive] for primitive in required_primitives}
    
    while not all(env._current_state.inventory[primitive] >= count for primitive, count in required_counts.items()):
        # Find a nearby primitive and collect it
        for primitive in required_primitives:
            if env._current_state.next_to(primitive):
                actions.append(env.action_specs()['USE'])  # Collect the item
                break
        else:
            # If no primitives are next to us, move randomly (for simplicity)
            possible_moves = [env.action_specs()[dir] for dir in ['UP', 'DOWN', 'LEFT', 'RIGHT']]
            action = np.random.choice(possible_moves)
            actions.append(action)
            
    # Go to a workshop and craft the item
    workshops = [i for i, is_workshop in enumerate(cookbook.recipes[output]) if isinstance(is_workshop, str) and "WORKSHOP" in is_workshop]
    if not workshops:
        raise ValueError("No workshop found to craft the item")
    
    # For simplicity, let's assume we can go directly to a workshop (no pathfinding)
    workshop_index = workshops[0]  # Just pick the first workshop for now
    
    # Move to the workshop
    while not env._current_state.next_to(workshop_index):
        possible_moves = [env.action_specs()[dir] for dir in ['UP', 'DOWN', 'LEFT', 'RIGHT']]
        action = np.random.choice(possible_moves)
        actions.append(action)
        
    # Craft the item at the workshop
    actions.append(env.action_specs()['USE'])
    
    return actions


print(evaluate())