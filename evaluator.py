# import numpy as np
# import time
# import subprocess

# import env_factory

# NUM_EPISODES = 20
# # cap on steps per episode (to avoid infinite loops)
# MAX_STEPS_PER_EPISODE = 100

# # Create the environment factory
# factory = env_factory.EnvironmentFactory(
#     recipes_path="recipes.yaml",
#     hints_path="hints.yaml"
# )

# def evaluate() -> float:
#     """Evaluates the current `craft` policy over NUM_EPISODES random tasks."""
#     total_return = 0.0

#     for episode in range(NUM_EPISODES):
#         # 1) Create a fresh env and reset it with a deterministic seed
#         env = factory.sample_environment()  # Use the factory to create an environment
#         obs = env.reset(seed=episode)

#         # 2) Pull out the goal‐item index for this task
#         #    (CraftLab stores it on env.scenario.task.goal)
#         goal_name, goal_arg = env.scenario.task.goal

#         # 3) Ask your assembled policy to produce a list of actions
#         action_sequence = craft(env, goal_arg)

#         # 4) Step through those actions, accumulating reward
#         ep_return = 0.0
#         done = False
#         for t, action in enumerate(action_sequence):
#             r, done, _ = env.step(action)
#             ep_return += r
#             if done or t + 1 >= MAX_STEPS_PER_EPISODE:
#                 break

#         total_return += ep_return

#     # Return the mean episodic return as the fitness score for FunSearch
#     return total_return / NUM_EPISODES

# def craft(env, item) -> list[int]:
#     """Returns a list of actions to craft the item which is the index of the item in the env.world.cookbook.index"""
#     return [1,4,1,4]




import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 14 
  actions_to_take = craft(env, item)
  observations = env.reset()
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if reward:
      rewarding_frame = observations['image'].copy()
      rewarding_frame[:40] *= np.array([0, 1, 0])
    elif done:
      break

  return total_reward


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = True
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"

  env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, max_steps=100, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[stick]')
  return solve(env, visualise=visualise)



def craft(env, item) -> list[int]:
  """Returns a list of actions to craft the item which is the index of the item in the env.world.cookbook.index"""
  # return []
  print("stick")
  print(env.world.cookbook.index)
  goal_index = env.world.cookbook.index["stick"]
  print(goal_index)
  recipe = env.world.cookbook.recipes.get(goal_index, {})
  print(recipe)
  # Initialize the action list
  actions = []

  # Iterate over the recipe to determine the sequence of actions needed
  for ingredient_index, count in recipe.items():
      if ingredient_index == "_key":
          continue  # Skip the '_key' which denotes the output item

      # Attempt to find the ingredient in the inventory
      found = False
      for i in range(len(env.world.grabbable_indices)):
          if (env.world.inventory[i] > 0 and 
              env.world.cookbook.index[i] == ingredient_index):
              print("what are you trying to do")
              # Determine the action to pick up this ingredient
              action_index = env.world.grabbable_indices.index(i)
              print(action_index)
              actions.append(action_index)
              found = True
              break

      if not found:
          raise ValueError(f"Ingredient {ingredient_index} not found in inventory for crafting item {goal_index}")

  return actions


evaluate()