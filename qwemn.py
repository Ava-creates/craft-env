
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
