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
  
    """Crafts an item by moving to the appropriate workshop after collecting all necessary primitives.

    Args:
        env (CraftLab): The environment in which the agent acts.
        item_index (int): Index of the item to be crafted.

    Returns:
        list[int]: List of actions required to craft the item.
    """
    # Get the current state from the environment
    current_state = env._current_state
    
    # Get the primitives needed for the item
    cookbook = current_state.world.cookbook
    primitives_needed = cookbook.primitives_for(item_index)
    
    actions = []
    
    # Collect all needed primitives
    for primitive, count in primitives_needed.items():
        while np.sum(current_state.inventory[primitive]) < count:
            # Find a location with the needed primitive
            locations = np.argwhere(current_state.grid[:, :, primitive] > 0)
            
            if len(locations) == 0:
                print(f"No available {primitive} to collect.")
                break
            
            for loc in locations:
                x, y = loc
                agent_x, agent_y = current_state.pos
                
                # Move to the location of the primitive
                if agent_x < x:
                    actions.append(env.action_specs()['RIGHT'])
                elif agent_x > x:
                    actions.append(env.action_specs()['LEFT'])
                if agent_y < y:
                    actions.append(env.action_specs()['DOWN'])
                elif agent_y > y:
                    actions.append(env.action_specs()['UP'])
                
                # Collect the primitive
                actions.append(env.action_specs()['USE'])
                
                # Update the current state after collecting the primitive
                _, current_state = current_state.step(actions[-1])
    
    # Find a workshop to craft the item
    workshops = [cookbook.index["WORKSHOP0"], cookbook.index["WORKSHOP1"], cookbook.index["WORKSHOP2"]]
    for workshop in workshops:
        if current_state.next_to(workshop):
            actions.append(env.action_specs()['USE'])
            break
    else:
        print("No available workshop to craft the item.")
    
    return actions


print(evaluate())