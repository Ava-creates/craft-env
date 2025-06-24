def craft(env, item):
            def bfs(start_state):
                queue = [(start_state, [])]
                visited_states = set()
                
                while queue:
                    current_state, path = queue.pop(0)
                    # print(len(path))
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
            a = bfs(start_state)
     
            if(len(a) == 0):   
                return -1
            return a
        