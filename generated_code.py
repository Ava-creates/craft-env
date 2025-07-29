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
  item = 22 
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
      recipes_path, hints_path, 2, max_steps=200, reuse_environments=False,
      visualise=visualise)

  env = env_sampler.sample_environment(task_name='make[axe]')
  return solve(env, visualise=visualise)


def craft(env, item) -> list[int]:
  """Returns a list of actions to craft the item which is the index of the item in the env.world.cookbook.index"""
  import collections
  import numpy as np

  # Get the mapping of action names to their integer values.
  action_specs = env.action_specs()
  # Extract the integer values for all possible actions.
  # This version iterates directly over the values view, which is efficient.
  ACTION_VALUES = action_specs.values()

  # Reset the environment to its initial state.
  # This ensures the search starts from a clean and known configuration.
  # The `_` is used as a placeholder for the returned observation dictionary,
  # which we don't directly need here, but the call updates `env._current_state`.
  _ = env.reset()
  initial_craft_state = env._current_state

  # Initialize a queue for Breadth-First Search (BFS).
  # Each element in the queue is a tuple:
  # (current_CraftState_object, list_of_actions_to_reach_this_state).
  queue = collections.deque([(initial_craft_state, [])])

  # Initialize a set to keep track of visited states.
  # This prevents infinite loops and redundant computation, ensuring the shortest path is found.
  # A state is represented as a hashable tuple:
  # (grid_as_bytes, inventory_as_bytes, agent_position_tuple, agent_direction_integer).
  visited = set()

  # Add the initial state to the visited set.
  initial_grid_bytes = initial_craft_state.grid.tobytes()
  initial_inventory_bytes = initial_craft_state.inventory.tobytes()
  initial_hashable_state = (initial_grid_bytes, initial_inventory_bytes,
                            initial_craft_state.pos, initial_craft_state.dir)
  visited.add(initial_hashable_state)

  # Define the maximum search depth based on the environment's max_steps.
  # This aligns the planning horizon with the environment's episode length,
  # preventing paths that are too long to be executed.
  MAX_SEARCH_DEPTH = env.max_steps

  # Start the BFS loop
  while queue:
    current_state, actions_taken = queue.popleft()

    # Check if the current state satisfies the goal (i.e., the item is in the inventory).
    # CraftState.satisfies expects a goal_name (ignored here) and goal_arg (the item index).
    if current_state.satisfies(None, item):
      return actions_taken

    # If the current path has reached or exceeded the maximum allowed depth, prune it.
    # We prune *before* exploring actions from this state to prevent overly long paths.
    if len(actions_taken) >= MAX_SEARCH_DEPTH:
      continue

    # Generate a hashable representation of the current state for comparison with next states.
    # This is done here to enable the "no-op" optimization below.
    current_grid_bytes = current_state.grid.tobytes()
    current_inventory_bytes = current_state.inventory.tobytes()
    current_hashable_state = (current_grid_bytes, current_inventory_bytes,
                              current_state.pos, current_state.dir)

    # Explore all possible actions from the current state.
    for action_value in ACTION_VALUES:
      # Simulate the action. CraftState.step returns a new CraftState object.
      # The reward is not used for pathfinding in this context.
      _, next_state = current_state.step(action_value)

      # Create a hashable representation of the next state.
      next_grid_bytes = next_state.grid.tobytes()
      next_inventory_bytes = next_state.inventory.tobytes()
      next_hashable_state = (next_grid_bytes, next_inventory_bytes,
                             next_state.pos, next_state.dir)

      # Optimization: If the action results in no state change, skip it.
      # This prevents adding redundant entries to the queue and visited set
      # for actions that are effectively "no-ops" in the current context (e.g.,
      # moving into a wall, or using an item when nothing is nearby).
      if next_hashable_state == current_hashable_state:
          continue

      # If this next state has not been visited before, add it to the visited set
      # and enqueue it for further exploration.
      if next_hashable_state not in visited:
        visited.add(next_hashable_state)
        queue.append((next_state, actions_taken + [action_value]))

  # If the queue becomes empty and the goal was never reached,
  # it means the item cannot be crafted or reached within the defined search limits.
  return []

 
print(evaluate())