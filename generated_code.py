from __future__ import division
from __future__ import print_function

"""
Class: Struct
Data Attributes
• Dynamic attributes set from the `entries` dict passed to `__init__`

Constructor **init**(\*\*entries)
Inputs
entries: dict of nested dicts/lists/values
Outputs
None (populates self.**dict** with attributes matching entries)

**str**(self) → str
Inputs
self
Outputs
Indented multiline string of all attributes

**repr**(self) → str
Inputs
self
Outputs
“Struct({…})” showing internal attribute dict

---

Class: Index
Data Attributes
contents: dict mapping names → indices
ordered\_contents: list of names in insertion order
reverse\_contents: dict mapping indices → names

Constructor **init**()
Inputs
None
Outputs
None (initializes the three data attributes)

**getitem**(self, item) → int or None
Inputs
item: str
Outputs
Index for item or None if not present

index(self, item) → int
Inputs
item: str
Outputs
New or existing index (starts at 1), updates contents, ordered\_contents, reverse\_contents

get(self, idx) → str
Inputs
idx: int
Outputs
Name for idx or “*invalid*” if idx == 0

**len**(self) → int
Inputs
self
Outputs
Number of entries + 1

**iter**(self) → iterator
Inputs
self
Outputs
Iterator over ordered\_contents

**str**(self) → str
Inputs
self
Outputs
“Index: {…}” showing contents dict

---

Function: flatten(lol) → list
Inputs
lol: tuple or list (possibly nested)
Outputs
Flat list of all non-list/tuple elements
Data Attributes
None

Function: postorder(tree) → generator
Inputs
tree: tuple or leaf
Outputs
Yields nodes in post-order traversal
Data Attributes
None

Function: tree\_map(function, tree) → same-structured tree
Inputs
function: callable
tree: tuple or leaf
Outputs
New tree with function applied to each node
Data Attributes
None

Function: tree\_zip(\*trees) → tuple
Inputs
trees: multiple tuples with identical structure
Outputs
Tuple of zipped elements at each position
Data Attributes
None

Function: parse\_fexp(fexp) → (str, str)
Inputs
fexp: str of form “name\[arg]”
Outputs
(name, arg) extracted via regex
Data Attributes
None

Class: Cookbook
Holds world components and crafting rules parsed from a YAML file.

Constructor init(recipes_path)
Inputs
recipes_path: str (path to YAML recipes)
Outputs
None (initializes index, environment set, primitives set, recipes dict, kinds set, n_kinds)

primitives_for(self, goal) → dict
Inputs
self
goal: int (index of desired output)
Outputs
dict mapping primitive-kind indices (int) to counts (int) required to craft one goal; empty if goal has no recipe

Data Attributes
index: Index instance mapping names to integer IDs
environment: set of int indices for non-grabbable entities
primitives: set of int indices for primitive resources
recipes: dict {output_index: {ingredient_index or "_key": count}}
kinds: set of all int indices (environment ∪ primitives ∪ recipe outputs)
n_kinds: int (total number of kinds)

Class: CraftWorld
A class for generating grid-based crafting scenarios and sampling tasks.

Constructor init(recipes_path, seed=0)
Inputs
recipes_path: str
seed: int (optional)
Outputs
None (initializes cookbook, feature/action counts, index lists, RNG)

sample_scenario_with_goal(self, goal) → CraftScenario
Inputs
self
goal: int (index of desired item)
Outputs
CraftScenario instance configured to make the goal achievable (raises ValueError if goal unknown)

sample_scenario(self, make_island=False, make_cave=False) → CraftScenario
Inputs
self
make_island: bool (optional)
make_cave: bool (optional)
Outputs
CraftScenario instance 

Data Attributes
cookbook: Cookbook instance holding recipes, primitives, and environment indices
n_features: int total size of the feature vector (depends on window size and n_kinds)
n_actions: int number of possible actions (N_ACTIONS)
non_grabbable_indices: set of int indices for entities that cannot be picked up
grabbable_indices: list of int indices for entities that can be picked up
workshop_indices: list of int indices for workshop locations
water_index: int index for the “water” entity
stone_index: int index for the “stone” entity
random: numpy.random.RandomState initialized with the given seed


Class: CraftScenario
Represents a single episode setup for CraftWorld.

Constructor init(grid, init_pos, world)
Inputs
grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds)
init_pos: tuple(int, int)
world: CraftWorld instance
Outputs
None (stores initial grid, position, direction, and world)

init(self) → CraftState
Inputs
self
Outputs
CraftState

Data Attributes 
init_grid: numpy.ndarray (the initial grid layout)
init_pos: tuple(int, int) (the agent’s starting position)
init_dir: int (the agent’s starting direction, default 0)
world: CraftWorld instance (reference to the world configuration)


Class: CraftState
A representation of a single crafting environment state, including grid, inventory, position, and direction.

Constructor init(scenario, grid, pos, dir, inventory)
Inputs
scenario: CraftScenario instance
grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds)
pos: tuple (int, int)
dir: int
inventory: numpy.ndarray of length n_kinds
Outputs
None (initializes state attributes and empty caches)

satisfies(self, goal_name, goal_arg) → bool
Inputs
self
goal_name: identifier for goal (ignored here)
goal_arg: int index of goal item
Outputs
True if inventory[goal_arg] > 0, else False

features(self) → numpy.ndarray
Inputs
self
Outputs
1D float32 array of length n_features, concatenating egocentric views, inventory, direction, and padding

features_dict(self) → dict
Inputs
self
Outputs
Dict containing:
features_ego: egocentric one-hot grid slice (numpy.ndarray)
features_ego_large: downsampled larger egocentric view (numpy.ndarray)
features_global: full allocentric grid copy (numpy.ndarray)
pos: normalized position array of length 2 (numpy.ndarray)
direction: one-hot array of length 4 (numpy.ndarray)
inventory: copy of inventory vector (numpy.ndarray)

step(self, action) → (float, CraftState)
Inputs
self
action: int (DOWN, UP, LEFT, RIGHT, or USE)
Outputs
reward: float (always 0.0 in this implementation)
new_state: CraftState instance after applying movement or use logic, with updated grid, position, direction, and inventory

next_to(self, i_kind) → bool
Inputs
self
i_kind: int index of an entity kind
Outputs
True if any cell in the 3×3 neighborhood around pos contains that kind, else False

Data Attributes
scenario: CraftScenario instance (reference to the scenario that created this state)
world: CraftWorld instance (reference to the world configuration)
grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds) (current grid occupancy)
inventory: numpy.ndarray of length n_kinds (current counts of each item)
pos: tuple(int, int) (agent’s current position)
dir: int (agent’s current facing direction)
_cached_features_dict: dict or None (cache for computed feature slices)
_cached_features: numpy.ndarray or None (cache for flattened feature vector)

Class: CraftLab
A wrapper class providing a DMLab-style interface for the CraftState class.

Constructor init(scenario, task_name, task, max_steps, visualise, render_scale, extra_pickup_penalty)
Inputs
scenario: object
task_name: str
task: Task(goal, steps)
max_steps: int
visualise: bool
render_scale: int
extra_pickup_penalty: float
Outputs
None (initializes internal state, rendering options, reward logic, color palette)

obs_specs(self) → dict
Inputs
self
Outputs
dict with keys
features: dict with dtype float32 and shape (n_features,)
task_name: dict with dtype string and shape ()
image: dict with dtype float32 and shape (render_height, render_width, 3) if visualise=True

action_specs(self) → dict
Inputs
self
Outputs
dict mapping DOWN→0, UP→1, LEFT→2, RIGHT→3, USE→4

reset(self, seed=0) → dict
Inputs
self
seed: int (optional)
Outputs
observation dict

step(self, action, num_steps=1) → (float, bool, dict)
Inputs
self
action: int
num_steps: int (optional)
Outputs
reward: float
done: bool
observations: dict

observations(self) → dict
Inputs
self
Outputs
dict with keys
features: numpy.ndarray dtype float32
features_dict: dict
task_name: str
image: numpy.ndarray dtype float32 if visualise=True

close(self) → None
Inputs
self
Outputs
None

_get_reward(self) → float
Inputs
self
Outputs
float reward (≥0)

_is_done(self) → bool
Inputs
self
Outputs
True if goal satisfied or max_steps reached, else False

Data Structures
Task: namedtuple(goal, steps)

Data Attributes
world: CraftWorld instance
scenario: CraftScenario instance
task_name: str
task: Task(goal, steps)
max_steps: int
_visualise: bool
steps: int
_extra_pickup_penalty: float
_current_state: CraftState instance
"""


"""Implements a craft terminal function for DSL for using the CraftLab class provided."""



import numpy as np
import time

import env_factory


def solve(env, visualise=False) -> float:
  """Runs the environment with a craft function that returns list of actions to takr and returns total reward."""
  item = 30
  actions_to_take = craft(env, item)
  observations = env.reset()
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

  return total_reward 


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = True
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"

  env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=400, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[goldarrow]')
  return solve(env, visualise=visualise)


def craft(env, item) -> list[int]:
  """Returns a list of actions to craft the item which is the index of the item in the env.world.cookbook.index"""
  import collections # Required for deque for BFS

  # Define action constants for clarity
  DOWN = 0
  UP = 1
  LEFT = 2
  RIGHT = 3
  USE = 4

  def _find_path_actions_to_adjacent(start_pos, current_grid, target_kind_idx, non_grabbable_indices):
    """
    Finds a path of movement actions (DOWN, UP, LEFT, RIGHT) from start_pos to a cell
    adjacent to an instance of target_kind_idx.
    Considers cells containing non_grabbable_indices as obstacles.
    Returns a list of actions or None if no path is found.
    The path leads to a position where `current_state.next_to(target_kind_idx)` would be True.
    """
    height, width, _ = current_grid.shape
    
    # Identify all grid locations where the target_kind_idx is present.
    target_object_cells = []
    for r in range(height):
        for c in range(width):
            if current_grid[r, c, target_kind_idx] == 1:
                target_object_cells.append((r, c))
    
    if not target_object_cells:
        return None # Target item not found on the grid at all

    q = collections.deque([(start_pos, [])]) # (current_position, path_actions_so_far)
    visited = {start_pos}

    # Define movement deltas (dr, dc) and their corresponding actions
    moves = {
        (1, 0): DOWN,
        (-1, 0): UP,
        (0, -1): LEFT,
        (0, 1): RIGHT
    }

    while q:
        (r, c), path_actions = q.popleft()

        # Check if the current position (r, c) is adjacent to any of the target objects.
        # This is the goal condition for the BFS: being in a position suitable for `USE`.
        is_adjacent_to_target = False
        for tr, tc in target_object_cells:
            # Check 3x3 neighborhood around target (tr, tc), excluding the target cell itself
            # as a valid agent position for the `next_to` concept.
            if abs(r - tr) <= 1 and abs(c - tc) <= 1 and (r,c) != (tr,tc):
                is_adjacent_to_target = True
                break
        
        if is_adjacent_to_target:
            return path_actions # Found a path to a cell adjacent to the target

        # Explore valid neighbors
        for (dr, dc), action in moves.items():
            nr, nc = r + dr, c + dc # New potential position

            # Check bounds
            if not (0 <= nr < height and 0 <= nc < width):
                continue

            # Check if already visited in this BFS path
            if (nr, nc) in visited:
                continue
            
            # Check if the next cell (nr, nc) is walkable.
            # A cell is considered an obstacle if it contains any non-grabbable item.
            is_obstacle = False
            for idx in non_grabbable_indices:
                if current_grid[nr, nc, idx] == 1: 
                    is_obstacle = True
                    break
            if is_obstacle:
                continue

            visited.add((nr, nc))
            q.append(((nr, nc), path_actions + [action]))

    return None # No path found to any cell adjacent to the target

  # --- Main craft_v2 function logic starts here ---
  all_actions = []

  # Get initial state and world information from the CraftLab environment
  current_state = env._current_state 
  cookbook = env.world.cookbook
  non_grabbable_indices = env.world.non_grabbable_indices
  workshop_indices = env.world.workshop_indices # Indices of entities that serve as workshops

  # 1. Check if the goal item is already in inventory
  if current_state.satisfies(None, item): # `goal_name` is ignored in `satisfies`
      return all_actions # Already crafted, no actions needed

  # Get the list of all primitive ingredients and their counts required for the final item.
  # The `primitives_for` method recursively breaks down recipes to their base components.
  needed_primitives = cookbook.primitives_for(item) # Returns {primitive_idx: count}

  # 2. Gather all required primitives iteratively
  # We loop until all necessary primitives are collected or a collection path is exhausted.
  max_collection_attempts = 200 # Safety limit to prevent infinite loops in complex scenarios

  for attempt in range(max_collection_attempts):
      all_primitives_satisfied = True
      missing_primitive_to_collect_idx = None # Store the index of the first encountered missing primitive

      # Check if any primitive is still missing
      for p_idx, p_count in needed_primitives.items():
          if current_state.inventory[p_idx] < p_count:
              all_primitives_satisfied = False
              missing_primitive_to_collect_idx = p_idx
              break # Found a missing primitive, focus on collecting this one

      if all_primitives_satisfied:
          break # All primitives are collected, exit the gathering loop
      
      if attempt == max_collection_attempts - 1:
          # Cannot collect all primitives within the allowed attempts.
          return [] # Indicate failure or unreachability

      # Find a path to the missing primitive and attempt to collect it
      path_to_primitive = _find_path_actions_to_adjacent(
          current_state.pos, current_state.grid, missing_primitive_to_collect_idx, non_grabbable_indices
      )

      if path_to_primitive is None:
          # Cannot find a path to the necessary primitive on the grid.
          # This primitive might be exhausted or inherently unreachable.
          return [] # Indicate failure (item likely uncraftable)

      # Execute the path to the primitive
      for action in path_to_primitive:
          # Use env.step() to apply the action and update the actual environment state
          _, _, _ = env.step(action) 
          all_actions.append(action)
          # Always re-sync `current_state` with the environment's internal state after each step
          current_state = env._current_state 

      # After moving, use the primitive if the agent is adjacent to it.
      # The pathfinding ensures adjacency, so this condition should usually be met.
      if current_state.next_to(missing_primitive_to_collect_idx):
          _, _, _ = env.step(USE)
          all_actions.append(USE)
          current_state = env._current_state # Update state after USE
      else:
          # This case indicates a problem with pathfinding or a dynamic environment
          # where the target disappeared.
          return [] # Indicate failure

  # 3. Craft the final item if a workshop is required
  # Get the specific recipe for the final goal item.
  recipe_dict = cookbook.recipes.get(item) 

  workshop_needed_idx = None
  if recipe_dict: # If a recipe exists for the goal item (i.e., it's not a primitive)
      # Check if one of the recipe's keys specifies a required workshop.
      # The workshop index might be stored as a special key in the recipe.
      for key in recipe_dict:
          if key in workshop_indices:
              workshop_needed_idx = key
              break
  
  if workshop_needed_idx is not None:
      # Pathfind to the required workshop location
      path_to_workshop = _find_path_actions_to_adjacent(
          current_state.pos, current_state.grid, workshop_needed_idx, non_grabbable_indices
      )

      if path_to_workshop is None:
          # Cannot find a path to the workshop.
          return [] # Indicate failure

      # Execute the path to the workshop
      for action in path_to_workshop:
          _, _, _ = env.step(action)
          all_actions.append(action)
          current_state = env._current_state # Update state

      # Use the workshop to craft the item
      if current_state.next_to(workshop_needed_idx):
          _, _, _ = env.step(USE)
          all_actions.append(USE)
          current_state = env._current_state # Update state after USE
      else:
          # Agent not next to workshop after pathing, implies an issue.
          return [] # Indicate failure

  # 4. Final verification: Check if the goal item is now in inventory
  # After all actions, get the latest state and check if the goal is satisfied.
  if current_state.satisfies(None, item):
      return all_actions # Successfully crafted
  else:
      # Goal not satisfied despite attempting all actions.
      # This could mean the item is uncraftable, or there's a logic gap for complex recipes.
      return []

 
print(evaluate())