'''
You are an expert in solving tasks some simulation environments using programmatic strategies. You will be given the details on the simulation environment (in the form of its code base), a domain-specific language (DSL) that is designed to solve the task in a compositional way, and you will be asked to come up with the implementation of specific functions in the DSL to using the provided code base. You are safe to assume that other than the function we ask you to implement, the rest of the constructs in the DSL are already implemented properly. 
## Code base for the game
The code base contains the following information:
- Classes: Each class includes informations about data attributes, class constructors and functions. We also provide information about the inputs to the constructors, and inputs, outputs and type signatures of the functions. 
- Functions: These are functions that do not belong to any class. We provide the input, output and the type signatures of the functions.

Class: Struct
Data Attributes
- Dynamic attributes set from the `entries` dict passed to `__init__`
Constructor **init**(\*\*entries)
Inputs
- entries: dict of nested dicts/lists/values
Outputs
- None (populates self.**dict** with attributes matching entries)
**str**(self) → str
Inputs
- self
Outputs
- Indented multiline string of all attributes
**repr**(self) → str
Inputs
- self
Outputs
- “Struct({…})” showing internal attribute dict
---
Class: Index
Data Attributes
- contents: dict mapping names → indices
- ordered\_contents: list of names in insertion order
- reverse\_contents: dict mapping indices → names
Constructor **init**()
Inputs
- None
Outputs
- None (initializes the three data attributes)
**getitem**(self, item) → int or None
Inputs
- item: str
Outputs
- Index for item or None if not present
index(self, item) → int
Inputs
- item: str
Outputs
- New or existing index (starts at 1), updates contents, ordered\_contents, reverse\_contents
get(self, idx) → str
Inputs
- idx: int
Outputs
- Name for idx or “*invalid*” if idx == 0
**len**(self) → int
Inputs
- self
Outputs
- Number of entries + 1
**iter**(self) → iterator
Inputs
- self
Outputs
- Iterator over ordered\_contents
**str**(self) → str
Inputs
- self
Outputs
- “Index: {}” dictionary with strings mapped to int
---
Function: flatten(lol) → list
Inputs
- lol: tuple or list (possibly nested)
Outputs
- Flat list of all non-list/tuple elements
Data Attributes
- None
Function: postorder(tree) → generator
Inputs
- tree: tuple or leaf
Outputs
- Yields nodes in post-order traversal
Data Attributes
- None
Function: tree\_map(function, tree) → same-structured tree
Inputs
- function: callable
- tree: tuple or leaf
Outputs
- New tree with function applied to each node
Data Attributes
- None
Function: tree\_zip(\*trees) → tuple
Inputs
- trees: multiple tuples with identical structure
Outputs
- Tuple of zipped elements at each position
Data Attributes
- None
Function: parse\_fexp(fexp) → (str, str)
Inputs
- fexp: str of form “name\[arg]”
Outputs
- (name, arg) extracted via regex
Data Attributes
- None
---
Class: Cookbook
Holds world components and crafting rules parsed from a YAML file.
Constructor init(recipes_path)
Inputs
- recipes_path: str (path to YAML recipes)
Outputs
- None (initializes index, environment set, primitives set, recipes dict, kinds set, n_kinds)
primitives_for(self, goal) → dict
Inputs
- self
- goal: int (index of desired output)
Outputs
- dict mapping primitive-kind indices (int) to counts (int) required to craft one goal; empty if goal has no recipe
Data Attributes
- index: Index instance mapping names to integer IDs
- environment: set of int indices for non-grabbable entities
- primitives: set of int indices for primitive resources
- recipes: dict {output_index: {ingredient_index or "_key": count}}
- kinds: set of all int indices (environment ∪ primitives ∪ recipe outputs)
- n_kinds: int (total number of kinds)
---
Class: CraftWorld
A class for generating grid-based crafting scenarios and sampling tasks.
Constructor init(recipes_path, seed=0)
Inputs
- recipes_path: str
- seed: int (optional)
Outputs
- None (initializes cookbook, feature/action counts, index lists, RNG)
sample_scenario_with_goal(self, goal) → CraftScenario
Inputs
- self
- goal: int (index of desired item)
Outputs
- CraftScenario instance configured to make the goal achievable (raises ValueError if goal unknown)
sample_scenario(self, make_island=False, make_cave=False) → CraftScenario
Inputs
- self
- make_island: bool (optional)
- make_cave: bool (optional)
Outputs
- CraftScenario instance 
Data Attributes
- cookbook: Cookbook instance holding recipes, primitives, and environment indices
- n_features: int total size of the feature vector (depends on window size and n_kinds)
- n_actions: int number of possible actions (N_ACTIONS)
- non_grabbable_indices: set of int indices for entities that cannot be picked up
- grabbable_indices: list of int indices for entities that can be picked up
- workshop_indices: list of int indices for different types workshop locations
- water_index: int index for the “water” entity
- stone_index: int index for the “stone” entity
- random: numpy.random.RandomState initialized with the given seed
---
Class: CraftScenario
Represents a single episode setup for CraftWorld.
Constructor init(grid, init_pos, world)
Inputs
- grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds)
- init_pos: tuple(int, int)
- world: CraftWorld instance
Outputs
- None (stores initial grid, position, direction, and world)
init(self) → CraftState
Inputs
- self
Outputs
- CraftState
Data Attributes 
- init_grid: numpy.ndarray (the initial grid layout)
- init_pos: tuple(int, int) (the agent’s starting position)
- init_dir: int (the agent’s starting direction, default 0)
- world: CraftWorld instance (reference to the world configuration)
---
Class: CraftState
A representation of a single crafting environment state, including grid, inventory, position, and direction.
Constructor init(scenario, grid, pos, dir, inventory)
Inputs
- scenario: CraftScenario instance
- grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds)
- pos: tuple (int, int)
- dir: int
- inventory: numpy.ndarray of length n_kinds
Outputs
- None (initializes state attributes and empty caches)
satisfies(self, goal_name, goal_arg) → bool
Inputs
- self
- goal_name: identifier for goal (ignored here)
- goal_arg: int index of goal item
Outputs
- True if inventory[goal_arg] > 0, else False
features(self) → numpy.ndarray
Inputs
- self
Outputs
- 1D float32 array of length n_features, concatenating egocentric views, inventory, direction, and padding
features_dict(self) → dict
Inputs
- self
Outputs
Dict containing:
- features_ego: egocentric one-hot grid slice (numpy.ndarray)
- features_ego_large: downsampled larger egocentric view (numpy.ndarray)
- features_global: full allocentric grid copy (numpy.ndarray)
- pos: normalized position array of length 2 (numpy.ndarray)
- direction: one-hot array of length 4 (numpy.ndarray)
- inventory: copy of inventory vector (numpy.ndarray)
step(self, action) → (float, CraftState)
Inputs
- self
- action: int (DOWN, UP, LEFT, RIGHT, or USE)
Outputs
- reward: float (always 0.0 in this implementation)
- new_state: CraftState instance after applying movement or use logic, with updated grid, position, direction, and inventory
next_to(self, i_kind) → bool
Inputs
- self
- i_kind: int index of an entity kind
Outputs
- True if any cell in the 3×3 neighborhood around pos contains that kind, else False
Data Attributes
- scenario: CraftScenario instance (reference to the scenario that created this state)
- world: CraftWorld instance (reference to the world configuration)
- grid: numpy.ndarray of shape (WIDTH, HEIGHT, n_kinds) (current grid occupancy)
- inventory: numpy.ndarray of length n_kinds (current counts of each item)
- pos: tuple(int, int) (agent’s current position)
- dir: int (agent’s current facing direction)
- _cached_features_dict: dict or None (cache for computed feature slices)
- _cached_features: numpy.ndarray or None (cache for flattened feature vector)
---
Class: CraftLab
A wrapper class providing a DMLab-style interface for the CraftState class.
Constructor init(scenario, task_name, task, max_steps, visualise, render_scale, extra_pickup_penalty)
Inputs
- scenario: object
- task_name: str
- task: Task(goal, steps)
- max_steps: int
- visualise: bool
- render_scale: int
- extra_pickup_penalty: float
Outputs
- None (initializes internal state, rendering options, reward logic, color palette)
obs_specs(self) → dict
Inputs
- self
Outputs
dict with keys
- features: dict with dtype float32 and shape (n_features,)
- task_name: dict with dtype string and shape ()
- image: dict with dtype float32 and shape (render_height, render_width, 3) if visualise=True
action_specs(self) → dict
Inputs
- self
Outputs
- dict mapping DOWN→0, UP→1, LEFT→2, RIGHT→3, USE→4
reset(self, seed=0) → dict
Inputs
- self
- seed: int (optional)
Outputs
- observation dict
step(self, action, num_steps=1) → (float, bool, dict)
Inputs
- self
- action: int
num_steps: int (optional)
Outputs
- reward: float
- done: bool
- observations: dict
observations(self) → dict
Inputs
- self
Outputs
dict with keys
- features: numpy.ndarray dtype float32
- features_dict: dict
- task_name: str
- image: numpy.ndarray dtype float32 if visualise=True
close(self) → None
Inputs
- self
Outputs
- None
_get_reward(self) → float
Inputs
- self
Outputs
- float reward (≥0)
_is_done(self) → bool
Inputs
- self
Outputs
- True if goal satisfied or max_steps reached, else False
Data Structures
- Task: namedtuple(goal, steps)
Data Attributes
- world: CraftWorld instance
- scenario: CraftScenario instance
- task_name: str
- task: Task(goal, steps)
- max_steps: int
- _visualise: bool
- steps: int
- _extra_pickup_penalty: float
- _current_state: CraftState instance
"""
## DSL
The following language is the domain-specific language that we designed to solve **any** task in this game. 
"""
s ::= task SEMI s | task SEMI
task ::= move | craft | ifhas do
move ::= MOVE_FUNC LPAR dir RPAR
dir ::= UP | DOWN | LEFT | RIGHT
craft ::= CRAFT_FUNC LPAR item RPAR
collect ::= COLLECT_FUNC LPAR primitive RPAR
item ::= PLANK | STICK | CLOTH | ROPE | BRIDGE | BUNDLE | HAMMER | KNIFE | BED | AXE | SHEARS | LADDER | SLINGSHOT | ARROW | BOW | BENCH | FLAG | GOLDARROW
ifhas ::= if HAS LPAR item RPAR
primitive ::= BOUNDARY | WATER | STONE | WORKSHOP0 | WORKSHOP1 | WORKSHOP2 | WOOD | IRON | GRASS | ROCK | GOLD | GEM
do ::= then task
"""

When coming up with the code understand that processing of the action list returned by the function will be handeled on the DSL interpreter using something like below ->

  actions_to_take = collect(env, primitive)
  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

'''

import numpy as np
import time
import collections
import env_factory

def solve(env, primitive, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = collect(env, primitive)

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
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"
  reward = 0 
  for i in range(3):
    if(i == 0):
      primitive = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
        
      reward += solve(env, primitive,  visualise=visualise)

    elif(i==1):
      primitive = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
        
      reward += solve(env, primitive, visualise=visualise)

    else:
      primtive = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[axe]')
        
      reward += solve(env, primitive, visualise=visualise)
  return reward


def collect(env, primitive) -> list[int]:
  """Returns a list of actions to find and collect the primitve passed int he function in the passed env. """
  import collections
  import numpy as np

  # Get the integer ID for the primitive string from the cookbook's index.
  # The `index` method will create the index if it doesn't exist, but for "primitives"
  # in this context, they are expected to be known entities.
  primitive_idx = env.world.cookbook.index.index(primitive)

  # Get current state information from the environment's internal state.
  current_state = env._current_state
  start_pos = current_state.pos # Agent's current (row, col) position
  start_dir = current_state.dir # Agent's current direction (0:North, 1:East, 2:South, 3:West)
  grid = current_state.grid     # The current grid layout for pathfinding
  grid_height, grid_width, _ = grid.shape # Grid dimensions: (rows, columns, kinds)

  # Define action mappings for movements and USE based on the environment's action specifications.
  ACTION_MAP = {
      'UP': env.action_specs()['UP'],
      'DOWN': env.action_specs()['DOWN'],
      'LEFT': env.action_specs()['LEFT'],
      'RIGHT': env.action_specs()['RIGHT'],
      'USE': env.action_specs()['USE']
  }

  # Map (delta_row, delta_col) for a move action to (action_id, new_agent_direction_int).
  # When an agent moves, its direction is updated to face the direction of movement.
  # (dr, dc) represents the change in (row, column) coordinates.
  # Dictionary format: (delta_row, delta_col): (action_to_take_id, resulting_direction_int)
  MOVE_ACTIONS_INFO = {
      (0, -1): (ACTION_MAP['UP'], 0),    # Move North: row stays, col decreases. New dir: North (0)
      (0, 1): (ACTION_MAP['DOWN'], 2),   # Move South: row stays, col increases. New dir: South (2)
      (-1, 0): (ACTION_MAP['LEFT'], 3),  # Move West: row decreases, col stays. New dir: West (3)
      (1, 0): (ACTION_MAP['RIGHT'], 1),  # Move East: row increases, col stays. New dir: East (1)
  }

  # Map agent direction integer to (delta_row, delta_col) for the cell directly in front of the agent.
  # This is crucial for 'ADJACENT_AND_FACE' interaction type, to check if the primitive is in sight.
  # Dictionary format: direction_int: (dr_relative_to_agent_pos, dc_relative_to_agent_pos)
  RELATIVE_DIR_TO_FACING_CELL_DELTA = {
      0: (0, -1), # North: If agent at (r,c) facing North, cell in front is (r, c-1).
      1: (1, 0),  # East: If agent at (r,c) facing East, cell in front is (r+1, c).
      2: (0, 1),  # South: If agent at (r,c) facing South, cell in front is (r, c+1).
      3: (-1, 0)  # West: If agent at (r,c) facing West, cell in front is (r-1, c).
  }

  # Determine the interaction type required for the primitive.
  # This dictates how the agent needs to be positioned relative to the primitive to "collect" it.
  target_is_grabbable = primitive_idx in env.world.grabbable_indices
  target_is_workshop = primitive_idx in env.world.workshop_indices

  interaction_type = None
  if target_is_grabbable:
      # Examples: WOOD, IRON. Agent typically needs to be adjacent and facing it to USE.
      interaction_type = "ADJACENT_AND_FACE"
  elif target_is_workshop:
      # Examples: WORKSHOP0, WORKSHOP1. Agent needs to be on the same square to USE.
      interaction_type = "ON_SQUARE"
  else:
      # This covers other "primitives" like BOUNDARY, WATER, STONE (if not explicitly grabbable/workshop).
      # Assumes 'collect' implies reaching the square and performing a 'USE' action there.
      interaction_type = "ON_SQUARE"

  # Breadth-First Search (BFS) Initialization
  # The queue stores tuples: (current_position (r,c), current_direction, path_of_actions_to_reach_this_state).
  q = collections.deque([((start_pos[0], start_pos[1]), start_dir, [])])
  # The visited set stores (position_r, position_c, direction) tuples to avoid redundant exploration.
  # Visiting the same grid position from a different agent direction can be a distinct and valid state.
  visited = {(start_pos[0], start_pos[1], start_dir)}

  while q:
      (r, c), current_dir, path = q.popleft()

      # --- Check if the current agent state (position, direction) satisfies the goal condition ---
      # This check is performed immediately upon popping a state, as it might be the target.
      
      # Condition for ON_SQUARE interaction: agent is on the target square.
      if interaction_type == "ON_SQUARE":
          if grid[r, c, primitive_idx] > 0:
              # If the current cell contains the primitive, a 'USE' action completes the collection.
              return path + [ACTION_MAP['USE']]
      # Condition for ADJACENT_AND_FACE interaction: agent is adjacent to and facing the target.
      elif interaction_type == "ADJACENT_AND_FACE":
          dr_facing, dc_facing = RELATIVE_DIR_TO_FACING_CELL_DELTA[current_dir]
          target_nr, target_nc = r + dr_facing, c + dc_facing
          
          # Ensure the cell the agent is facing is within grid boundaries.
          if 0 <= target_nr < grid_height and 0 <= target_nc < grid_width:
              if grid[target_nr, target_nc, primitive_idx] > 0:
                  # If the cell in front contains the primitive, a 'USE' action completes the collection.
                  return path + [ACTION_MAP['USE']]
      
      # --- Explore neighbor states by simulating potential move actions ---
      for (dr_move, dc_move), (action_val, new_dir) in MOVE_ACTIONS_INFO.items():
          nr, nc = r + dr_move, c + dc_move # Calculate new potential position after taking a move action

          # Check if the new position is within the grid boundaries.
          if not (0 <= nr < grid_height and 0 <= nc < grid_width):
              continue

          # Check for traversability of the new cell:
          # A cell is considered traversable if it does not contain any "non-grabbable"
          # entity (which are typically obstacles), *unless* that specific non-grabbable
          # entity IS our target primitive (e.g., a workshop, which you can move onto).
          is_traversable = True
          for k_idx in env.world.non_grabbable_indices:
              # If the neighbor cell (nr, nc) contains an obstacle (a non-grabbable entity)
              # AND that obstacle is NOT the primitive we are currently trying to collect.
              if grid[nr, nc, k_idx] > 0 and k_idx != primitive_idx:
                  is_traversable = False
                  break
          if not is_traversable:
              continue
          
          # Check if this new state (position, new_direction) has already been visited
          # to prevent cycles and redundant path exploration.
          if (nr, nc, new_dir) in visited:
              continue

          # If the state is valid and has not been visited, add it to the queue
          # and mark it as visited for future reference.
          visited.add((nr, nc, new_dir))
          q.append(((nr, nc), new_dir, path + [action_val]))

  # If the BFS completes and the primitive was not found on the grid or a path to it
  # could not be determined, return an empty list of actions.
  return []

 
print(evaluate())