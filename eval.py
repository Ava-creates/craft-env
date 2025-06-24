# -*- coding: utf-8 -*-
import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 14
  actions_to_take = craft(env, item)
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
      print(env._current_state.pos)
      def get_primitive_positions(primitive):
          positions = []
          for x in range(env._current_state.grid.shape[0]):
              for y in range(env._current_state.grid.shape[1]):
                  if env._current_state.grid[x, y].argmax() == primitive:
                      positions.append((x, y))
          return positions

      def move_to_position(x, y):
          current_x, current_y = env._current_state.pos
          dx, dy = x - current_x, y - current_y

          # Adjust direction and move step by step
          while dx != 0 or dy != 0:
              if abs(dx) > abs(dy):  # Move horizontally first if needed
                  if dx < 0:
                      actions.append(2)  # LEFT
                      env._current_state.pos = (env._current_state.pos[0] - 1, env._current_state.pos[1])
                      env._current_state.dir = 2
                      dx += 1
                  elif dx > 0:
                      actions.append(3)  # RIGHT
                      env._current_state.pos = (env._current_state.pos[0] + 1, env._current_state.pos[1])
                      env._current_state.dir = 3
                      dx -= 1
              else:  # Move vertically
                  if dy < 0:
                      actions.append(0)  # DOWN
                      env._current_state.pos = (env._current_state.pos[0], env._current_state.pos[1] - 1)
                      env._current_state.dir = 0
                      dy += 1
                  elif dy > 0:
                      actions.append(1)  # UP
                      env._current_state.pos = (env._current_state.pos[0], env._current_state.pos[1] + 1)
                      env._current_state.dir = 1
                      dy -= 1

      def pick_up_at_position(x, y):
          move_to_position(x, y)
          # Align direction to the target position
          current_x, current_y = env._current_state.pos
          dx, dy = x - current_x, y - current_y

          if dx == 0 and dy < 0:
              actions.append(0)  # DOWN
              env._current_state.dir = 0
          elif dx == 0 and dy > 0:
              actions.append(1)  # UP
              env._current_state.dir = 1
          elif dx < 0 and dy == 0:
              actions.append(2)  # LEFT
              env._current_state.dir = 2
          elif dx > 0 and dy == 0:
              actions.append(3)  # RIGHT
              env._current_state.dir = 3

          actions.append(4)  # USE to pick up the item
          env._current_state.inventory[primitive] += 1

      def craft_at_workshop():
          for workshop in env.world.workshop_indices:
              move_to_position(workshop // env._current_state.grid.shape[1],
                              workshop % env._current_state.grid.shape[1])
              actions.append(4)  # USE to craft the item
              break

      # Main crafting logic
      recipe = env.world.cookbook.primitives_for(item)

      if not recipe:
          raise ValueError("No recipe available to craft the desired item.")

      actions = []

      # Collect all required primitives
      for primitive, count in recipe.items():
          positions = get_primitive_positions(primitive)

          if len(positions) < count:
              raise ValueError(f"Not enough primitives {env.world.cookbook.index.get(primitive)} available to craft the desired item.")

          while env._current_state.inventory[primitive] < count:
              for x, y in positions:
                  pick_up_at_position(x, y)

      # Craft at a workshop
      craft_at_workshop()
      # print("here", env._current_state.satisfies(None, 14))
      print(env._current_state.pos)
      print(env)
      return actions


print(evaluate()) 