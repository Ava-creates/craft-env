import numpy as np
import time
import collections
import env_factory
import craft
import env
def collect(env, primitive):    # Step 1: Extract the current state from the environment
    current_state = env._current_state

    # Step 2: Identify the index of the primitive to collect
    primitive_index = current_state.world.cookbook.index[primitive]

    # Step 3: Define a simple BFS (Breadth-First Search) algorithm to find the shortest path
    def bfs(start_pos, target_kind):
        """Performs Breadth-First Search to find the shortest path to a cell with the target kind."""
        queue = collections.deque([(start_pos, [])])
        visited = set()
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            # Check all four possible directions: UP, DOWN, LEFT, RIGHT
            for dx, dy, action in [(-1, 0, 2), (1, 0, 3), (0, -1, 0), (0, 1, 1)]:
                nx, ny = x + dx, y + dy
                # Ensure the new position is within bounds and not blocked by non-grabbable entities
                if 0 <= nx < current_state.grid.shape[0] and 0 <= ny < current_state.grid.shape[1]:
                    kind_index = np.argmax(current_state.grid[nx, ny])
                    if kind_index in current_state.world.non_grabbable_indices:
                        continue
                    new_path = path + [action]
                    # Check if the target primitive is found at this cell
                    if kind_index == target_kind:
                        return new_path
                    queue.append(((nx, ny), new_path))
        return []

    # Step 4: Use the BFS to find a path to any cell containing the primitive
    actions = bfs(current_state.pos, primitive_index)

    # Step 5: Append the USE action to collect the primitive
    if actions:
        actions.append(4)  # The index for the USE action

    return actions