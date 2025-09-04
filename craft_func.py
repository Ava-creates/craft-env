import numpy as np
import collections
def craft(env, item):
    cookbook = env.world.cookbook
    goal_index = cookbook.index[item]

    if goal_index is None:
        raise ValueError("Unknown item")

    workshop_indices = env.world.workshop_indices

    actions = []

    # Find the closest workshop that can craft the desired item
    closest_workshop_idx, min_distance = None, float('inf')
    pos = np.array(env._current_state.pos)

    for workshop_idx in workshop_indices:
        # Calculate the mean position of all workshops of this type
        workshop_pos_list = np.argwhere(env._current_state.grid[:, :, workshop_idx])
        
        if len(workshop_pos_list) > 0:  # Check if there is any location for the workshop
            workshop_pos_mean = workshop_pos_list.mean(axis=0)
            distance = np.linalg.norm(pos - workshop_pos_mean, ord=2)
            if distance < min_distance:
                closest_workshop_idx, min_distance = workshop_idx, distance

    if closest_workshop_idx is None:
        raise ValueError("No available workshop found")

    # Calculate the closest position to move towards
    target_positions = np.argwhere(env._current_state.grid[:, :, closest_workshop_idx])
    nearest_target_pos = None
    min_nearest_distance = float('inf')

    for target_pos in target_positions:
        distance = np.linalg.norm(pos - target_pos, ord=2)
        if distance < min_nearest_distance:
            nearest_target_pos = target_pos
            min_nearest_distance = distance

    # Move to the closest workshop position
    while not np.array_equal(pos, nearest_target_pos):
        dx, dy = nearest_target_pos - pos
        
        # Determine direction to move in
        if abs(dx) > abs(dy):  # Prioritize moving in x-direction first
            actions.append(3 if dx > 0 else 2)
            pos[0] += 1 if dx > 0 else -1
        else:  # Then move in y-direction
            actions.append(1 if dy > 0 else 0)
            pos[1] += 1 if dy > 0 else -1

    # Use the workshop to craft the item
    actions.append(4)  # USE
    # print(actions)
    return actions