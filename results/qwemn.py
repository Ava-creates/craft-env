
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
            return path

        for action in range(env.world.n_actions):
            _, new_state = current_state.step(action)
            queue.append((new_state, path + [action]))
    
    return []

start_state = env._current_state
return bfs(start_state)




  from collections import deque

  queue = deque([([], env._current_state)])
  visited_states = set()

  while queue:
    path, state = queue.popleft()
    
    # Convert the current state to a hashable form
    state_hash = tuple(state.grid.flatten()) + tuple(state.inventory) + (state.pos,) + (state.dir,)
    
    if state_hash in visited_states:
        continue
    
    visited_states.add(state_hash)

    # Check if the goal is satisfied
    if state.satisfies(None, item):
      return path

    for action in range(env.world.n_actions):
      reward, new_state = state.step(action)
      
      # Add the new state and the corresponding action to the queue
      queue.append((path + [action], new_state))

  raise ValueError("No crafting sequence found")


from collections import deque
import heapq

def heuristic(state):
    # Example heuristic: number of items in inventory
    return len(state.inventory)

def a_star_search(env, item):
    queue = []
    heapq.heappush(queue, (0, [], env._current_state))

    visited_states = set()

    while queue:
        cost, path, state = heapq.heappop(queue)

        # Convert the current state to a hashable form
        state_hash = (
            tuple(state.grid.flatten()) +
            tuple(state.inventory) +
            (state.pos,) +
            (state.dir,)
        )

        if state_hash in visited_states:
            continue

        visited_states.add(state_hash)

        # Check if the goal is satisfied
        if state.satisfies(None, item):
            return path

        for action in range(env.world.n_actions):
            reward, new_state = state.step(action)

            # Push the new state to the priority queue with updated cost
            new_cost = cost + 1 + heuristic(new_state)
            heapq.heappush(queue, (new_cost, path + [action], new_state))

    raise ValueError("No crafting sequence found")





def find_ingredients(recipe):
    ingredients = []
    counts = []
    for key, count in recipe.items():
        if isinstance(key, int):
            ingredients.append(key)
            counts.append(count)
    return ingredients, counts

actions = []
cookbook = env.world.cookbook
goal_index = cookbook.index.get(item)
if goal_index is None:
    raise ValueError("Item not found in cookbook")

recipe = cookbook.recipes.get(goal_index)
if not recipe:
    return actions

ingredients, counts = find_ingredients(recipe)
inventory = env._current_state.inventory

for i in range(len(ingredients)):
    while inventory[ingredients[i]] < counts[i]:
        # Try to pick up the ingredient if not enough in inventory
        actions += pickup_item(env, ingredients[i])
        inventory = env._current_state.inventory  # Update the inventory after pickup

    action = use_item(env, ingredients[i], counts[i])
    if action is not None:
        actions.append(action)

return actions
