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
import craft
import env
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
      primitive = "gold"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
        
      reward += solve(env, primitive, visualise=visualise)
  return reward


def collect(env: env.CraftLab, primitive: str) -> list[int]:
  """Returns a list of actions to find and collect the primitive in the passed env.
    
    Args:
        env (env.CraftLab): The CraftLab object.
        primitive (str): The name of the primitive to collect.

    Returns:
        List[int]: A sequence of action indices to execute.
  """
  current_state = env._current_state
  world = env.world

  # 1. Get the primitive's integer ID from the cookbook.
  try:
    i_kind = world.cookbook.index[primitive.lower()]
  except KeyError:
    # If the primitive name is not recognized, it cannot be collected.
    return []

  # 2. Check if the primitive is already in the agent's inventory.
  # If it is, no actions are needed to "collect" it.
  if current_state.inventory[i_kind] > 0:
      return []

  # 3. Semantic check: Determine if this primitive is generally collectible via the 'USE' action.
  # This includes items that can be picked up (grabbable) and specific resources like water or stone.
  # Items like workshops, boundaries, or bridges are typically not "collected" into inventory.
  # This check helps prune the search early if the goal is fundamentally uncollectible by USE.
  is_collectible_via_use = (
      i_kind in world.grabbable_indices or 
      i_kind == world.water_index or 
      i_kind == world.stone_index
  )
  
  if not is_collectible_via_use:
    return []

  # 4. Define action integers and direction deltas for movement and interaction.
  action_map = env.action_specs()
  UP_ACT = action_map["UP"]
  DOWN_ACT = action_map["DOWN"]
  LEFT_ACT = action_map["LEFT"]
  RIGHT_ACT = action_map["RIGHT"]
  USE_ACT = action_map["USE"]

  move_actions = [UP_ACT, DOWN_ACT, LEFT_ACT, RIGHT_ACT]

  # _DIR_TO_DELTA_FRONT maps the agent's integer direction (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
  # to the (row_change, col_change) needed to find the cell directly in front of the agent.
  _DIR_TO_DELTA_FRONT = {
      0: (-1, 0), # UP: row - 1, col (moves North)
      1: (0, 1),  # RIGHT: row, col + 1 (moves East)
      2: (1, 0),  # DOWN: row + 1, col (moves South)
      3: (0, -1)  # LEFT: row, col - 1 (moves West)
  }

  # Helper function to calculate the shortest sequence of turning actions
  # to face a target direction from the current direction.
  def _get_turning_actions(current_dir: int, target_dir: int) -> list[int]:
      if current_dir == target_dir:
          return [] # Already facing the target direction
      
      # Calculate the difference in directions, handling circularity (0-3).
      # Adding 4 and taking modulo 4 ensures a positive difference.
      diff = (target_dir - current_dir + 4) % 4
      
      if diff == 1: # Target is one step clockwise (e.g., UP(0) -> RIGHT(1))
          return [RIGHT_ACT]
      elif diff == 3: # Target is one step counter-clockwise (e.g., UP(0) -> LEFT(3))
          return [LEFT_ACT]
      else: # diff == 2, implies a 180-degree turn (e.g., UP(0) -> DOWN(2))
          # Two consecutive right or left turns will achieve this.
          return [RIGHT_ACT, RIGHT_ACT] # Arbitrarily choose RIGHT_ACT twice

  # 5. Initialize Breadth-First Search (BFS).
  q = collections.deque()
  # The 'visited' set stores (row, col, direction, inventory_tuple) to ensure
  # identical states with different inventories are treated distinctly.
  visited = set()

  # Start BFS from the current environment state.
  initial_inventory_tuple = tuple(current_state.inventory)
  q.append((current_state, []))
  visited.add((current_state.pos[0], current_state.pos[1], current_state.dir, initial_inventory_tuple))

  grid_width, grid_height, _ = current_state.grid.shape
  
  # MAX_EXPLORED_STATES: This limit prevents extremely long searches in complex environments.
  # For v2, we are increasing the multiplier for `MAX_EXPLORED_STATES` to allow for
  # a deeper exploration of states. This is crucial for scenarios where intermediate
  # pickups (e.g., acquiring a tool that then allows harvesting) are required before
  # the final primitive can be collected. This makes the search more robust than v1.
  MAX_EXPLORED_STATES = grid_width * grid_height * 4 * world.cookbook.n_kinds * 3 # Increased multiplier for more depth and robustness
  explored_states_count = 0

  # 6. BFS Loop.
  while q:
    state, path = q.popleft() # Dequeue the current state and the path to reach it
    explored_states_count += 1

    # Apply the soft limit: if too many states have been explored,
    # prevent further expansion from this path, but allow existing queue items to be processed.
    if explored_states_count > MAX_EXPLORED_STATES:
        continue 

    current_r, current_c = state.pos
    current_dir = state.dir
    
    # Goal Check: Can we collect the primitive from this `state`?
    # This specifically checks for the target primitive (`i_kind`) in the immediate vicinity
    # and attempts to collect it.
    if state.next_to(i_kind):
        for target_dir in range(4): # Iterate through all 4 cardinal directions (UP, RIGHT, DOWN, LEFT)
            dr, dc = _DIR_TO_DELTA_FRONT[target_dir]
            facing_r, facing_c = current_r + dr, current_c + dc

            # Ensure the cell directly in front is within grid bounds and contains the target primitive.
            if (0 <= facing_r < grid_width and 0 <= facing_c < grid_height and 
                state.grid[facing_r, facing_c, i_kind] == 1):
                
                # Simulate the turning actions required to face the primitive.
                temp_state_after_turns = state 
                turns_to_face = _get_turning_actions(current_dir, target_dir)
                for turn_action in turns_to_face:
                    # Reward is always 0.0 in this implementation, so we discard it.
                    _, temp_state_after_turns = temp_state_after_turns.step(turn_action)

                # Store inventory before attempting USE to verify successful collection.
                inventory_before_use = np.copy(temp_state_after_turns.inventory)

                # Simulate the 'USE' action. This is where the collection attempt happens.
                # Reward is always 0.0, so we discard it.
                _, state_after_use = temp_state_after_turns.step(USE_ACT)

                # Critical success check: Did the count of the primitive in inventory actually increase?
                # This verifies successful collection, accounting for any internal game rules
                # (e.g., tools needed, resource depletion) handled by `CraftState.step`.
                if state_after_use.inventory[i_kind] > inventory_before_use[i_kind]:
                    return path + turns_to_face + [USE_ACT]

    # Explore possible movement actions:
    for action in move_actions:
      # Reward is always 0.0, so we discard it.
      _, next_state = state.step(action)
      next_inventory_tuple = tuple(next_state.inventory)
      next_state_key = (next_state.pos[0], next_state.pos[1], next_state.dir, next_inventory_tuple)

      # Add the new state to the queue if it hasn't been visited with this inventory configuration.
      if next_state_key not in visited:
        visited.add(next_state_key)
        q.append((next_state, path + [action]))
    
    # Explore the USE action from the current position.
    # This is important if using an item at the current position (e.g., picking up a tool
    # or activating something) can change the inventory state or open up new paths.
    inventory_before_any_use = np.copy(state.inventory)
    # Reward is always 0.0, so we discard it.
    _, state_after_current_use = state.step(USE_ACT)
    
    # Check if the USE action resulted in a meaningful state change.
    # This prevents adding redundant states to the queue if USE had no effect (e.g., using an empty cell).
    if not (np.array_equal(state_after_current_use.inventory, inventory_before_any_use) and
            state_after_current_use.pos == state.pos and
            state_after_current_use.dir == state.dir):

        next_inventory_tuple = tuple(state_after_current_use.inventory)
        next_state_key = (state_after_current_use.pos[0], state_after_current_use.pos[1], state_after_current_use.dir, next_inventory_tuple)

        if next_state_key not in visited:
            visited.add(next_state_key)
            q.append((state_after_current_use, path + [USE_ACT]))

  # If the BFS queue is exhausted and no path to collect the primitive was found,
  # it means the primitive is unreachable from the initial state given the current conditions
  # and exploration limits.
  return []

 
print(evaluate())