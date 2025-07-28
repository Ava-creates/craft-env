# -*- coding: utf-8 -*-
import numpy as np
import time

import env_factory

def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 14
  action_to_take = craft(env, 14)

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


def craft(env, item) -> float:

    total_reward = 0.0

    # Get the index of the item to craft
    item_idx = env.world.cookbook.index[item]
    
    # Check if the item is craftable (i.e., has a recipe)
    if item_idx not in env.world.cookbook.recipes:
        return total_reward  # Not craftable, e.g., primitive item like "wood"

    recipe = env.world.cookbook.recipes[item_idx]
    
    # Determine if a crafting station is required
    if "_at" in recipe:
        station_name = recipe["_at"]
        station_idx = env.world.cookbook.index[station_name]

        # Find the crafting station's location on the grid
        station_x, station_y = -1, -1
        for x_grid in range(WIDTH):
            for y_grid in range(HEIGHT):
                if env._current_state.grid[x_grid, y_grid, station_idx] == 1:
                    station_x, station_y = x_grid, y_grid
                    break
            if station_x != -1:
                break

        if station_x == -1:
            return total_reward  # Station not found

        # Define approach points (adjacent tiles + required facing direction)
        target_approach_points = [
            (station_x, station_y - 1, UP),
            (station_x - 1, station_y, RIGHT),
            (station_x, station_y + 1, DOWN),
            (station_x + 1, station_y, LEFT)
        ]

        station_reached_and_oriented = False
        for target_px, target_py, target_d in target_approach_points:
            moves_count = 0
            max_moves_to_reach_pos = 2 * (WIDTH + HEIGHT) + 10

            # Move agent to adjacent tile
            while env._current_state.pos != (target_px, target_py) and moves_count < max_moves_to_reach_pos:
                current_x, current_y = env._current_state.pos
                action_to_take = -1
                if current_x < target_px:
                    action_to_take = RIGHT
                elif current_x > target_px:
                    action_to_take = LEFT
                elif current_y < target_py:
                    action_to_take = UP
                elif current_y > target_py:
                    action_to_take = DOWN

                prev_pos = env._current_state.pos
                reward, done, _ = env.step(action_to_take)
                total_reward += reward
                moves_count += 1
                if done:
                    return total_reward
                if env._current_state.pos == prev_pos:
                    break  # Stuck, try next approach point

            if env._current_state.pos != (target_px, target_py):
                continue  # Failed to reach this position

            # Orient the agent
            spins_count = 0
            max_spins = 4
            while env._current_state.dir != target_d and spins_count < max_spins:
                reward, done, _ = env.step(target_d)
                total_reward += reward
                spins_count += 1
                if done:
                    return total_reward

            if env._current_state.dir == target_d:
                station_reached_and_oriented = True
                break  # Found suitable approach point

        if not station_reached_and_oriented:
            return total_reward  # Failed to position and orient

    # Perform the USE action
    reward, done, _ = env.step(USE)
    total_reward += reward
    if done:
        return total_reward

    return total_reward

print(evaluate()) 