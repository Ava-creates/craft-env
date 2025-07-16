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
  
  # Get the primitives/items required to craft the given item
  task = env.task
  goal_name, goal_arg = task.goal

  # Get all items needed in the recipe for the goal
  needed_items = env.world.cookbook.primitives_for(item_index)

  actions = []
  
  # Collect the needed items
  for primitive, count in needed_items.items():
    while np.sum(env._current_state.inventory[primitive]) < count:
      if not env._current_state.next_to(primitive):
        # Move to a workshop where we can find this item
        workshops_for_item = env.world.cookbook.workshops_for(primitive)
        for workshop in workshops_for_item:
          # Check if the current state is next to any of these workshops
          if env._current_state.next_to(workshop):
            break
        else:
          # If no workshop is adjacent, move to one (for simplicity, we'll assume a workshop is always reachable)
          actions.extend(move_actions(env, primitive))
      
      # Craft the item at the workshop
      actions.append(env.action_specs()['USE'])
  
  # Once all items are collected, craft the goal item
  if env._current_state.next_to(env.world.cookbook.workshops_for(goal_arg)[0]):
    actions.append(env.action_specs()['USE'])
  else:
    actions.extend(move_actions(env, goal_arg))
    actions.append(env.action_specs()['USE'])
    
  return actions


print(evaluate())