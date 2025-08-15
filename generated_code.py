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


'''

import numpy as np
import time
import collections
import env_factory
import craft
import env
def solve(env, primitive, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  state, reward, actions_to_take = collect(env, primitive)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break
  if total_reward > 0.5:
    return 0.3
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
      env.reset()
      reward += solve(env, primitive,  visualise=visualise)

    elif(i==1):
      primitive = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      reward += solve(env, primitive, visualise=visualise)

    else:
      primitive = "gold"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
      env.reset()
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward += solve(env, primitive, visualise=visualise)

  return reward


def collect(env: env.CraftLab, primitive: str) -> list[int]:
  """Returns a sequence of actions to collect only the specified primitive, using only the agent's current inventory. Do not pick up primitives that are not passed as the argument.

  This function computes a shortest path to reach and collect a given primitive (e.g., GOLD, GEM, WOOD) in the environment.
  It accounts for obstacles and environmental constraints by allowing the agent to use tools already in inventory—
  for example:
    - Using a BRIDGE to cross WATER in order to reach GOLD.
    - Using a PICKAXE to mine GEM.

  The function assumes the world is static except for changes resulting from tool use (e.g., placing a bridge).
  It does not perform crafting or attempt to acquire new items—only available tools in the inventory are used.

  Args:
      env (env.CraftLab): The CraftLab environment instance.
      primitive (str): The name of the primitive to collect.

  Returns:
      List[int]: A list of action indices the agent can execute to collect the primitive.
  """
  # Get the index of the target primitive
  target_primitive_index = env.world.cookbook.index(primitive)
  
  # Initialize the queue for BFS and a set to keep track of visited positions
  q = collections.deque([(state.pos, state.dir, [])])  # (position, direction, path_taken)
  visited = set()
  visited.add((state.pos, state.dir))
  
  while q:
      current_pos, current_dir, path_taken = q.popleft()
      
      # Get the current state
      current_state = CraftState(scenario=env.scenario, grid=state.grid.copy(), pos=current_pos, dir=current_dir, inventory=state.inventory.copy())
      
      # Check if the target primitive is next to the agent
      if current_state.next_to(target_primitive_index):
          # Collect the primitive and return the path taken
          action_list = path_taken + [env.action_specs()[USE]]
          state, reward, _ = env.step(action_list)
          return state, reward, action_list
      
      # Try moving in all four directions
      for direction_name, action_id in env.action_specs().items():
          if direction_name == USE:
              continue  # Skip the USE action since we are only trying to move
          
          new_pos = current_state.pos
          new_dir = current_state.dir
          
          if direction_name == DOWN:
              new_pos = (current_pos[0], current_pos[1] + 1)
          elif direction_name == UP:
              new_pos = (current_pos[0], current_pos[1] - 1)
          elif direction_name == LEFT:
              new_pos = (current_pos[0] - 1, current_pos[1])
          elif direction_name == RIGHT:
              new_pos = (current_pos[0] + 1, current_pos[1])
          
          # Check if the new position is within bounds and not visited
          if (new_pos[0] >= 0 and new_pos[0] < state.grid.shape[0] and
              new_pos[1] >= 0 and new_pos[1] < state.grid.shape[1]):
              
              # Add the move action to the path taken
              new_path = path_taken + [action_id]
              
              # Add the new position to the queue if it hasn't been visited
              if (new_pos, current_dir) not in visited:
                  q.append((new_pos, current_dir, new_path))
                  visited.add((new_pos, current_dir))
      
      # Try turning around
      for turn_action_id in [env.action_specs()[LEFT], env.action_specs()[RIGHT]]:
          new_dir = (current_state.dir + 1) % 4 if action_id == env.action_specs()[LEFT] else (current_state.dir - 1) % 4
          
          # Add the turn action to the path taken
          new_path = path_taken + [turn_action_id]
          
          # Add the new direction to the queue if it hasn't been visited
          if (current_pos, new_dir) not in visited:
              q.append((current_pos, new_dir, new_path))
              visited.add((current_pos, new_dir))
  
  return state, reward, action_list

 
print(evaluate())