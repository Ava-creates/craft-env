# -*- coding: utf-8 -*-
import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  actions_to_take = craft(env, 30)
  print(actions_to_take)
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
  visualise = True
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"

  env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path,2, max_steps=100, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[goldarrow]')

  return solve(env, visualise=visualise)


def craft(env, item) -> float:

  import collections

  # Action constants (from action_specs)
  # Placed inside the function to adhere to the strict requirement of
  # returning only code that fits within the function.
  DOWN = 0
  UP = 1
  LEFT = 2
  RIGHT = 3
  USE = 4
  ACTIONS = [DOWN, UP, LEFT, RIGHT, USE]

  # Reset the environment to a consistent starting state.
  # This populates `env._current_state` with the initial `CraftState`.
  env.reset(seed=0)
  initial_craft_state = env._current_state

  # Queue for Breadth-First Search (BFS).
  # Each element is a tuple: (current_CraftState, list_of_actions_to_reach_this_state).
  queue = collections.deque([(initial_craft_state, [])])

  # Set to store visited states to avoid redundant computations and cycles.
  # A state is uniquely identified by its grid layout, inventory, agent position, and direction.
  # `grid.tobytes()` is used for efficient hashing of the numpy grid array.
  # Inventory (numpy array) and position (tuple) are converted to tuples for hashing.
  visited = set()

  # Maximum depth to search. This limits the number of actions in a potential solution path.
  # It prevents excessively long runtimes for complex or potentially unsolvable goals.
  # This value might need tuning depending on the typical complexity of crafting tasks.
  max_search_depth = 75

  while queue:
    current_state, actions_so_far = queue.popleft()

    # Check if the goal item is present in the current state's inventory.
    if current_state.satisfies(None, item):
      return actions_so_far

    # If the current path length exceeds the maximum allowed search depth,
    # prune this branch to limit computational cost.
    if len(actions_so_far) >= max_search_depth:
      continue

    # Create a hashable representation of the current state.
    state_key = (current_state.grid.tobytes(), tuple(current_state.inventory),
                 current_state.pos, current_state.dir)

    # If this state has already been visited, skip it.
    # BFS inherently finds the shortest path, so if we've seen this state,
    # we've either seen it via a shorter path, or we're exploring a cycle.
    if state_key in visited:
      continue
    visited.add(state_key)

    # Explore all possible actions from the current state.
    for action in ACTIONS:
      # `current_state.step(action)` returns a new `CraftState` instance,
      # which is essential for BFS to explore distinct states without modifying previous ones.
      reward, next_state = current_state.step(action)
      queue.append((next_state, actions_so_far + [action]))

  # If the queue becomes empty and the goal was not found, it means the item
  # cannot be crafted within the specified search depth or is fundamentally impossible.
  return []

print(evaluate()) 