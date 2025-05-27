# -*- coding: utf-8 -*-
import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 11
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

  env = env_sampler.sample_environment(task_name='get[gold]')
  return solve(env, visualise=visualise)



def craft(env, item) -> list[int]:
    """Returns a list of actions to craft the item which is the index of the item in the env.world.cookbook.index"""

    def bfs(start_state):
        queue = [(start_state, [])]
        visited_states = set()
        
        while queue:
            current_state, path = queue.pop(0)
            
            # Convert the state to a hashable format for storing in visited set
            state_hash = tuple(current_state.grid.flatten()) + tuple(current_state.inventory) + (current_state.pos, current_state.dir)

            if state_hash in visited_states:
                continue
            
            visited_states.add(state_hash)
            
            # Check if goal is satisfied
            if current_state.satisfies(None, item):
                print(path)
                return path

            for action in range(env.world.n_actions):
                _, new_state = current_state.step(action)
                queue.append((new_state, path + [action]))
        
        return []

    start_state = env._current_state
    return bfs(start_state)

evaluate()