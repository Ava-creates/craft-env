"""Craft environment logic, forked from https://github.com/jacobandreas/psketch."""

from cookbook import Cookbook
from misc import array

import curses
import logging
import numpy as np
from skimage.measure import block_reduce
import time

WIDTH = 12
HEIGHT = 12

WINDOW_WIDTH = 5
WINDOW_HEIGHT = 5

N_WORKSHOPS = 3

DOWN = 0
UP = 1
LEFT = 2
RIGHT = 3
USE = 4
N_ACTIONS = USE + 1


def random_free(grid, random):
  pos = None
  while pos is None:
    (x, y) = (random.randint(WIDTH), random.randint(HEIGHT))
    if grid[x, y, :].any():
      continue
    pos = (x, y)
  return pos


def neighbors(pos, dir=None):
  x, y = pos
  neighbors = []
  if x > 0 and (dir is None or dir == LEFT):
    neighbors.append((x - 1, y))
  if y > 0 and (dir is None or dir == DOWN):
    neighbors.append((x, y - 1))
  if x < WIDTH - 1 and (dir is None or dir == RIGHT):
    neighbors.append((x + 1, y))
  if y < HEIGHT - 1 and (dir is None or dir == UP):
    neighbors.append((x, y + 1))
  return neighbors


class CraftWorld(object):
  def __init__(self, recipes_path, seed=0):
    self.cookbook = Cookbook(recipes_path)
    self.n_features = \
        2 * WINDOW_WIDTH * WINDOW_HEIGHT * self.cookbook.n_kinds + \
        self.cookbook.n_kinds + \
        4 + \
        1
    self.n_actions = N_ACTIONS

    self.non_grabbable_indices = self.cookbook.environment
    self.grabbable_indices = [
        i for i in range(self.cookbook.n_kinds)
        if i not in self.non_grabbable_indices
    ]
    self.workshop_indices = [
        self.cookbook.index["workshop%d" % i] for i in range(N_WORKSHOPS)
    ]
    self.water_index = self.cookbook.index["water"]
    self.stone_index = self.cookbook.index["stone"]

    self.random = np.random.RandomState(seed)

  def sample_scenario_with_goal(self, goal):
    assert goal not in self.cookbook.environment
    # print(goal, "in the scenarion")
    ingredients = self.cookbook.primitives_for(goal)
    make_island = (goal == self.cookbook.index["gold"] or
                   self.cookbook.index["gold"] in ingredients)
    make_cave = (goal == self.cookbook.index["gem"] or
                 self.cookbook.index["gem"] in ingredients)

    if (goal not in self.cookbook.primitives and goal not in self.cookbook.recipes):
      raise ValueError("Don't know how to build a scenario for %s" % goal)

    return self.sample_scenario_simple(make_island=make_island, make_cave=make_cave)

  def sample_scenario(self, make_island=False, make_cave=False):
    # generate grid
    # print(self.cookbook.n_kinds)
    grid = np.zeros((WIDTH, HEIGHT, self.cookbook.n_kinds))
    i_bd = self.cookbook.index["boundary"]
    grid[0, :, i_bd] = 1
    grid[WIDTH - 1:, :, i_bd] = 1
    grid[:, 0, i_bd] = 1
    grid[:, HEIGHT - 1:, i_bd] = 1

    # treasure
    if make_island or make_cave:
      (gx, gy) = (1 + self.random.randint(WIDTH - 2), 1)
      treasure_index = \
          self.cookbook.index["gold"] if make_island else self.cookbook.index["gem"]
      wall_index = \
          self.water_index if make_island else self.stone_index
      grid[gx, gy, treasure_index] = 1
      for i in range(-1, 2):
        for j in range(-1, 2):
          if not grid[gx + i, gy + j, :].any():
            grid[gx + i, gy + j, wall_index] = 1

    # ingredients
    for primitive in self.cookbook.primitives:
      if (primitive == self.cookbook.index["gold"] or
              primitive == self.cookbook.index["gem"]):
        continue
      for i in range(4):
        (x, y) = random_free(grid, self.random)
        grid[x, y, primitive] = 1

    # generate crafting stations
    for i_ws in range(N_WORKSHOPS):
      ws_x, ws_y = random_free(grid, self.random)
      grid[ws_x, ws_y, self.cookbook.index["workshop%d" % i_ws]] = 1

    # generate init pos
    init_pos = random_free(grid, self.random)

    return CraftScenario(grid, init_pos, self)

  def sample_scenario_simple(self, make_island=False, make_cave=False):
        # Create empty grid
        grid = np.zeros((WIDTH, HEIGHT, self.cookbook.n_kinds))
        
        # Add boundary
        i_bd = self.cookbook.index["boundary"]
        grid[0, :, i_bd] = 1
        grid[WIDTH - 1:, :, i_bd] = 1
        grid[:, 0, i_bd] = 1
        grid[:, HEIGHT - 1:, i_bd] = 1
        
        # Place agent at (5,5)
        init_pos = (5, 5)
        
        # Place wood at (5,6) - right next to agent
        wood_index = self.cookbook.index["wood"]
        grid[5, 6, wood_index] = 1
        
        # Place workshop1 at (5,7) - right next to wood
        workshop1_index = self.cookbook.index["workshop1"]
        grid[5, 7, workshop1_index] = 1
        
        return CraftScenario(grid, init_pos, self)

  def visualize(self, transitions):
    def _visualize(win):
      curses.start_color()
      for i in range(1, 8):
        curses.init_pair(i, i, curses.COLOR_BLACK)
        curses.init_pair(i + 10, curses.COLOR_BLACK, i)
      states = [transitions[0].s1] + [t.s2 for t in transitions]
      mstates = [transitions[0].m1] + [t.m2 for t in transitions]
      for state, mstate in zip(states, mstates):
        win.clear()
        for y in range(HEIGHT):
          for x in range(WIDTH):
            if not (state.grid[x, y, :].any() or
                    (x, y) == state.pos):
              continue
            thing = state.grid[x, y, :].argmax()
            if (x, y) == state.pos:
              if state.dir == LEFT:
                ch1 = "<"
                ch2 = "@"
              elif state.dir == RIGHT:
                ch1 = "@"
                ch2 = ">"
              elif state.dir == UP:
                ch1 = "^"
                ch2 = "@"
              elif state.dir == DOWN:
                ch1 = "@"
                ch2 = "v"
              color = curses.color_pair(mstate.arg or 0)
            elif thing == self.cookbook.index["boundary"]:
              ch1 = ch2 = curses.ACS_BOARD
              color = curses.color_pair(10 + thing)
            else:
              name = self.cookbook.index.get(thing)
              ch1 = name[0]
              ch2 = name[-1]
              color = curses.color_pair(10 + thing)

            win.addch(HEIGHT - y, x * 2, ch1, color)
            win.addch(HEIGHT - y, x * 2 + 1, ch2, color)
        win.refresh()
        time.sleep(1)

    curses.wrapper(_visualize)


class CraftScenario(object):
  def __init__(self, grid, init_pos, world):
    self.init_grid = grid
    self.init_pos = init_pos
    self.init_dir = 0
    self.world = world

  def init(self):
    inventory = np.zeros(self.world.cookbook.n_kinds)
    state = CraftState(self, self.init_grid, self.init_pos, self.init_dir,
                       inventory)
    return state


class CraftState(object):
  def __init__(self, scenario, grid, pos, dir, inventory):
    self.scenario = scenario
    self.world = scenario.world
    self.grid = grid
    self.inventory = inventory
    self.pos = pos
    self.dir = dir
    self._cached_features_dict = None
    self._cached_features = None

  def satisfies(self, goal_name, goal_arg):
    return self.inventory[goal_arg] > 0

  def features(self):
    if self._cached_features is None:
      features_dict = self.features_dict()
      features = np.concatenate((features_dict['features_ego'].ravel(),
                                 features_dict['features_ego_large'].ravel(),
                                 features_dict['inventory'],
                                 features_dict['direction'],
                                 [0]))
      assert len(features) == self.world.n_features
      self._cached_features = features.astype(np.float32)
    return self._cached_features

  def features_dict(self):
    if self._cached_features_dict is None:
      x, y = self.pos

      # Egocentric view, one-hot of features
      hw = int(WINDOW_WIDTH / 2)
      hh = int(WINDOW_HEIGHT / 2)
      grid_feats = array.pad_slice(self.grid, (x - hw, x + hw + 1),
                                   (y - hh, y + hh + 1))

      # Larger egocentric view, downsampled
      bhw = int((WINDOW_WIDTH * WINDOW_WIDTH) / 2)
      bhh = int((WINDOW_HEIGHT * WINDOW_HEIGHT) / 2)
      grid_feats_big = array.pad_slice(self.grid, (x - bhw, x + bhw + 1),
                                       (y - bhh, y + bhh + 1))
      grid_feats_big_downsampled = block_reduce(
          grid_feats_big, (WINDOW_WIDTH, WINDOW_HEIGHT, 1), func=np.max)

      # Position
      pos_feats = np.asarray(self.pos)
      pos_feats[0] /= WIDTH
      pos_feats[1] /= HEIGHT

      # Direction
      dir_features = np.zeros(4)
      dir_features[self.dir] = 1

      features_dict = {
          'features_ego': grid_feats,
          'features_ego_large': grid_feats_big_downsampled,
          'features_global': self.grid.copy(),  # Global allocentric view
          'pos': pos_feats,
          'direction': dir_features,
          'inventory': self.inventory.copy()
      }
      # print("$$$$", self.inventory, "$$$")
      self._cached_features_dict = features_dict

    return self._cached_features_dict

  def step(self, action):
    x, y = self.pos
    n_dir = self.dir
    n_inventory = self.inventory
    n_grid = self.grid

    reward = 0.0
    # print(x, y)
    # move actions
    if action == DOWN:
      dx, dy = (0, -1)
      # print("in down action")
      n_dir = DOWN
    elif action == UP:
      # print("in up action")
      dx, dy = (0, 1)
      n_dir = UP
    elif action == LEFT:
      dx, dy = (-1, 0)
      n_dir = LEFT
    elif action == RIGHT:
      dx, dy = (1, 0)
      n_dir = RIGHT

    # use actions
    elif action == USE:
      cookbook = self.world.cookbook
      dx, dy = (0, 0)
      success = False
      for nx, ny in neighbors(self.pos, self.dir):
        here = self.grid[nx, ny, :]
        if not self.grid[nx, ny, :].any():
          continue

        if here.sum() > 1:
          print("impossible world configuration:")
          logging.error(here.sum())
          logging.error(self.grid.sum(axis=2))
          logging.error(self.grid.sum(axis=0).sum(axis=0))
          logging.error(cookbook.index.contents)
        assert here.sum() == 1
        thing = here.argmax()

        if not(thing in self.world.grabbable_indices or
               thing in self.world.workshop_indices or
               thing == self.world.water_index or
               thing == self.world.stone_index):
          continue

        n_inventory = self.inventory.copy()
        n_grid = self.grid.copy()

        if thing in self.world.grabbable_indices:
          n_inventory[thing] += 1
          n_grid[nx, ny, thing] = 0
          success = True

        elif thing in self.world.workshop_indices:
          # TODO not with strings
          workshop = cookbook.index.get(thing)
          for output, inputs in cookbook.recipes.items():
            if inputs["_at"] != workshop:
              continue
            yld = inputs["_yield"] if "_yield" in inputs else 1
            ing = [i for i in inputs if isinstance(i, int)]
            if any(n_inventory[i] < inputs[i] for i in ing):
              continue
            n_inventory[output] += yld
            for i in ing:
              n_inventory[i] -= inputs[i]
            success = True

        elif thing == self.world.water_index:
          if n_inventory[cookbook.index["bridge"]] > 0:
            n_grid[nx, ny, self.world.water_index] = 0
            n_inventory[cookbook.index["bridge"]] -= 1

        elif thing == self.world.stone_index:
          if n_inventory[cookbook.index["axe"]] > 0:
            n_grid[nx, ny, self.world.stone_index] = 0

        break

    # other
    else:
      raise Exception("Unexpected action: %s" % action)

    n_x = x + dx
    n_y = y + dy
    if self.grid[n_x, n_y, :].any():
      n_x, n_y = x, y

    new_state = CraftState(self.scenario, n_grid, (n_x, n_y), n_dir,
                           n_inventory)
    return reward, new_state

  def next_to(self, i_kind):
    x, y = self.pos
    return self.grid[x - 1:x + 2, y - 1:y + 2, i_kind].any()
