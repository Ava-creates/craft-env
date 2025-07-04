"""DMLab-like wrapper for a Craft environment."""

from __future__ import division
from __future__ import print_function

import collections
import curses
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import seaborn as sns
import time

Task = collections.namedtuple("Task", ["goal", "steps"])


class CraftLab(object):
  """DMLab-like wrapper for a Craft state."""

  def __init__(self,
               scenario,
               task_name,
               task,
               max_steps=100,
               visualise=False,
               render_scale=10,
               extra_pickup_penalty=0.3):
    """DMLab-like interface for a Craft environment.

    Given a `scenario` (basically holding an initial world state), will provide
    the usual DMLab API for use in RL.
    """

    self.world = scenario.world
    self.scenario = scenario
    self.task_name = task_name
    self.task = task
    self.max_steps = max_steps
    self._visualise = visualise
    self.steps = 0
    self._extra_pickup_penalty = extra_pickup_penalty
    self._current_state = self.scenario.init()
    self._picked_up_counts = {}  # Track how many of each item we've picked up
    self._last_inventory = None  # Track last inventory state to detect pickups

    # Rendering options
    self._render_state = {}
    self._width, self._height, _ = self._current_state.grid.shape
    self._render_scale = render_scale
    self._inventory_bar_height = 10
    self._goal_bar_height = 30
    self._render_width = self._width * self._render_scale
    self._render_height = (self._height * self._render_scale +
                           self._goal_bar_height + self._inventory_bar_height)
    # Colors of entities for rendering
    self._colors = {
        'player': sns.xkcd_palette(('red', ))[0],
        'background': sns.xkcd_palette(('white', ))[0],
        'boundary': sns.xkcd_palette(('black', ))[0],
        'workshop0': sns.xkcd_palette(('blue', ))[0],
        'workshop1': sns.xkcd_palette(('pink', ))[0],
        'workshop2': sns.xkcd_palette(('violet', ))[0],
        'water': sns.xkcd_palette(('water blue', ))[0],
        'wood': sns.xkcd_palette(('sienna', ))[0],
        'cloth': sns.xkcd_palette(('off white', ))[0],
        'flag': sns.xkcd_palette(('cyan', ))[0],
        'grass': sns.xkcd_palette(('grass', ))[0],
        'iron': sns.xkcd_palette(('gunmetal', ))[0],
        'stone': sns.xkcd_palette(('stone', ))[0],
        'rock': sns.xkcd_palette(('light peach', ))[0],
        'hammer': sns.xkcd_palette(('chestnut', ))[0],
        'knife': sns.xkcd_palette(('greyblue', ))[0],
        'slingshot': sns.xkcd_palette(('dusty orange', ))[0],
        'bench': sns.xkcd_palette(('umber', ))[0],
        'arrow': sns.xkcd_palette(('cadet blue', ))[0],
        'bow': sns.xkcd_palette(('dark khaki', ))[0],
        'gold': sns.xkcd_palette(('gold', ))[0],
        'gem': sns.xkcd_palette(('bright purple', ))[0],
        'bridge': sns.xkcd_palette(('grey', ))[0],
        'stick': sns.xkcd_palette(('sandy brown', ))[0],
        'bundle': sns.xkcd_palette(('toupe', ))[0],
        'shears': sns.xkcd_palette(('cherry', ))[0],
        'plank': sns.xkcd_palette(('brown', ))[0],
        'ladder': sns.xkcd_palette(('metallic blue', ))[0],
        'goldarrow': sns.xkcd_palette(('golden', ))[0],
        'bed': sns.xkcd_palette(('fawn', ))[0],
        'rope': sns.xkcd_palette(('beige', ))[0],
        'axe': sns.xkcd_palette(('charcoal', ))[0]
    }

  def obs_specs(self):
    obs_specs = collections.OrderedDict()
    obs_specs['features'] = {
        'dtype': 'float32',
        'shape': (self.world.n_features, )
    }
    obs_specs['task_name'] = {'dtype': 'string', 'shape': tuple()}

    if self._visualise:
      obs_specs['image'] = {
          'dtype': 'float32',
          'shape': (self._render_height, self._render_width, 3)
      }
    return obs_specs

  def action_specs(self):
    # last action is termination of current option, we don't use it.
    return {
        'DOWN': 0,
        'UP': 1,
        'LEFT': 2,
        'RIGHT': 3,
        'USE': 4,
        # 'TERMINATE': 5
    }

  def reset(self, seed=0):
    """Reset the environment.

    Agent will loop in the same world, from the same starting position.
    """
    del seed
    self._current_state = self.scenario.init()
    self.steps = 0
    self._picked_up_counts = {}  # Reset picked up counts
    self._last_inventory = np.zeros_like(self._current_state.inventory)  # Initialize last inventory
    return self.observations()

  def observations(self):
    """Return observation dict."""
    obs = {
        'features': self._current_state.features().astype(np.float32),
        'features_dict': self._current_state.features_dict(),
        'task_name': self.task_name
    }
    if self._visualise:
      obs['image'] = self.render_frame().astype(np.float32)
    return obs

  def step(self, action, num_steps=1):
    """Step the environment, getting reward, done and observation."""
    assert num_steps == 1, "No action repeat in this environment"

    # Step environment
    # (state_reward is 0 for all existing Craft environments)
    state_reward, self._current_state = self._current_state.step(action)
    self.steps += 1

    done = self._is_done()
    reward = np.float32(self._get_reward() + state_reward)

    if done:
      self.reset()
    observations = self.observations()
    return reward, done, observations

  def _is_done(self):
    goal_name, goal_arg = self.task.goal
    # print(goal_name, goal_arg)
    if(self.steps >= self.max_steps):
      print("ran out of steps")
    done = (self._current_state.satisfies(goal_name, goal_arg)
            or self.steps >= self.max_steps)
    return done
    
  def _get_reward(self):
    goal_name, goal_arg = self.task.goal

    # Get all items needed in the recipe for the goal
    needed_items = self.world.cookbook.primitives_for(goal_arg)
    
    # Calculate reward based on new pickups of needed items
    reward = 0.0
    
    # Check for new pickups by comparing current inventory with last inventory
    if self._last_inventory is not None:
      for item, needed_count in needed_items.items():
        # If we have more of this item than before, it was just picked up
        if self._current_state.inventory[item] > self._last_inventory[item]:
          reward += 0.5  # Give reward for picking up a needed item
          
      # Check for goal item pickup
      if self._current_state.inventory[goal_arg] > self._last_inventory[goal_arg]:
        reward = 1.0  # Give full reward for picking up goal item
    
    # Update last inventory for next step
    self._last_inventory = self._current_state.inventory.copy()
      
    # Penalize picking up items not needed for the recipe
    items_index = np.arange(self._current_state.inventory.size)
    # Create mask for items that aren't needed (not in needed_items and not the goal)
    not_needed_mask = np.ones_like(items_index, dtype=bool)
    for item in needed_items:
      not_needed_mask[item] = False
    not_needed_mask[goal_arg] = False
    
    # Only penalize items that aren't needed for the recipe
    reward -= self._extra_pickup_penalty * np.sum(
        self._current_state.inventory[not_needed_mask])
    reward = np.maximum(reward, 0)
    return reward

  # def _get_reward(self):
  #   goal_name, goal_arg = self.task.goal

  #   # We want the correct pickup to be in inventory.
  #   # But we will penalise the agent for picking up extra stuff.
  #   items_index = np.arange(self._current_state.inventory.size)
  #   reward = float(self._current_state.inventory[goal_arg] > 0)
  #   print(self._current_state.inventory[items_index != goal_arg])
  #   # print(goal_arg)
  #   reward -= self._extra_pickup_penalty * np.sum(
  #       self._current_state.inventory[items_index != goal_arg])
  #   # reward = np.maximum(reward, 0)
  #   return reward


  # #llm provided  40 mini

  # def _get_reward(self):
  #       """
  #       Computes a shaped reward for FunSearch:
  #         - +1.0 for achieving the goal
  #         - +0.1 * fraction of required primitives already collected
  #         - +0.2 bonus if near a workshop and the goal requires crafting
  #         - -extra_pickup_penalty for each USE action
  #       """
  #       reward = 0.0
  #       goal_name, goal_idx = self.task.goal
  #       satisfies = self._current_state.satisfies(goal_name, goal_idx)

  #       if satisfies:
  #           reward += 1.0
  #       else:
  #           # Shaped reward based on how many goal ingredients are collected
  #           recipe = self.world.cookbook.recipes.get(goal_idx, {})
  #           total_required = sum(v for k, v in recipe.items() if isinstance(k, int))
  #           if total_required > 0:
  #               collected = sum(
  #                   min(self._current_state.inventory[k], v)
  #                   for k, v in recipe.items()
  #                   if isinstance(k, int)
  #               )
  #               reward += 0.1 * (collected / total_required)

  #           # Bonus if next to workshop and this is a craftable goal
  #           if any(isinstance(k, int) for k in recipe):
  #               if any(self._current_state.next_to(wk) for wk in self.world.workshop_indices):
  #                   reward += 0.2

  #       # Penalty for excessive USE
  #       USE = self.action_specs()['USE']
  #       if getattr(self, '_last_action', None) == USE:
  #           reward -= self._extra_pickup_penalty

  #       return reward


  def close(self):
    """Not used."""
    pass

  def render_matplotlib(self, frame=None, delta_time=0.1):
    """Render the environment with matplotlib, updating itself."""

    # Get current frame of environment or draw whatever we're given.
    if frame is None:
      frame = self.render_frame()

    # Setup if needed
    if not self._render_state:
      plt.ion()
      f, ax = plt.subplots()
      im = ax.imshow(frame)
      self._render_state['fig'] = f
      self._render_state['im'] = im
      ax.set_yticklabels([])
      ax.set_xticklabels([])
    # Update current frame
    self._render_state['im'].set_data(frame)
    self._render_state['fig'].canvas.draw()
    self._render_state['fig'].canvas.flush_events()
    time.sleep(delta_time)

    return frame

  def render_frame(self):
    """Render the current state as a 2D observation."""
    state = self._current_state

    ### Environment canvas
    env_canvas = np.zeros((self._width, self._height, 3))
    env_canvas[..., :] = self._colors['background']

    # Place all components
    for name, component_i in state.world.cookbook.index.contents.items():
      # Check if the component is there, if so, color env_canvas accordingly.
      x_i, y_i = np.nonzero(state.grid[..., component_i])
      env_canvas[x_i, y_i] = self._colors[name]

    # Place self
    env_canvas[state.pos] = self._colors['player']
    # Upscale to render at higher resolution
    env_img = Image.fromarray(
        (env_canvas.transpose(1, 0, 2) * 255).astype(np.uint8), mode='RGB')
    env_large = np.array(
        env_img.resize(
            (self._render_width,
             self._height * self._render_scale), Image.NEAREST)) / 255.

    ### Inventory
    # two rows: first shows color of component, second how many are there
    inventory_canvas = np.zeros((2, len(state.world.grabbable_indices) + 1, 3))
    for i, obj_id in enumerate(state.world.grabbable_indices[1:]):
      inventory_canvas[0, i + 1] = self._colors[state.world.cookbook.index.get(obj_id)]
    for c in range(3):
      inventory_canvas[1, 1:-1, c] = np.minimum(state.inventory[state.world.grabbable_indices[1:]], 1)
    inventory_img = Image.fromarray(
        (inventory_canvas * 255).astype(np.uint8), mode='RGB')
    inventory_large = np.array(
        inventory_img.resize(
            (self._render_width,
             self._inventory_bar_height), Image.NEAREST)) / 255.

    # Show goal text
    goal_bar = Image.new("RGB", (self._render_width, self._goal_bar_height),
                         (255, 255, 255))
    goal_canvas = ImageDraw.Draw(goal_bar)
    goal_canvas.text((10, 10), self.task_name, fill=(0, 0, 0))
    goal_bar = np.array(goal_bar)
    goal_bar = goal_bar.astype(np.float64)
    goal_bar /= 255.0

    # Combine into single window
    canvas_full = np.concatenate([goal_bar, env_large, inventory_large])

    return canvas_full

  def render_curses(self, fps=60):
    """Render the current state in curses."""
    width, height, _ = self._current_state.grid.shape
    action_spec = self.action_specs()

    def _visualize(win):
      state = self._current_state
      goal_name, _ = self.task.goal

      if state is None:
        return

      curses.start_color()
      for i in range(1, 8):
        curses.init_pair(i, i, curses.COLOR_BLACK)
        curses.init_pair(i + 10, curses.COLOR_BLACK, i)
      win.clear()
      for y in range(height):
        for x in range(width):
          if not (state.grid[x, y, :].any() or (x, y) == state.pos):
            continue
          thing = state.grid[x, y, :].argmax()
          if (x, y) == state.pos:
            if state.dir == action_spec['LEFT']:
              ch1 = "<"
              ch2 = "@"
            elif state.dir == action_spec['RIGHT']:
              ch1 = "@"
              ch2 = ">"
            elif state.dir == action_spec['UP']:
              ch1 = "^"
              ch2 = "@"
            elif state.dir == action_spec['DOWN']:
              ch1 = "@"
              ch2 = "v"
            color = curses.color_pair(goal_name or 0)
          elif thing == state.world.cookbook.index["boundary"]:
            ch1 = ch2 = curses.ACS_BOARD
            color = curses.color_pair(10 + thing)
          else:
            name = state.world.cookbook.index.get(thing)
            ch1 = name[0]
            ch2 = name[-1]
            color = curses.color_pair(10 + thing)

          win.addch(height - y, x * 2, ch1, color)
          win.addch(height - y, x * 2 + 1, ch2, color)
      win.refresh()
      time.sleep(1 / fps)

    return _visualize
