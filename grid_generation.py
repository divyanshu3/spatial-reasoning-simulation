import random, json

def generate_populated_grid(N, fill_ratio, humans_list, animals_list, vehicles_list):
    """
    Generates an NxN grid populated with unique object instances, ensuring at least
    one from each available category if space permits. No orientation.

    Args:
        N (int): The size of the grid (NxN).
        fill_ratio (float): The percentage of the grid to fill (e.g., 0.5 for 50%).
        humans_list (list): A list of human types (e.g., ["Man", "Woman"]).
        animals_list (list): A list of animal types (e.g., ["Dog", "Cat"]).
        vehicles_list (list): A list of vehicle types (e.g., ["Car", "Bike"]).

    Returns:
        list[list[str]]: A 2D list representing the grid, where each cell
                         contains either an object instance string (e.g., "Man1")
                         or "." for an empty cell.
    """
    if not (0 <= fill_ratio <= 1):
        raise ValueError("fill_ratio must be between 0 and 1.")
    if N <= 0:
        raise ValueError("N (grid size) must be a positive integer.")

    total_cells = N * N
    num_cells_to_fill = int(total_cells * fill_ratio)
    num_cells_to_fill = min(num_cells_to_fill, total_cells) # Cap at total_cells

    placed_instances = []
    type_counts = {} # To ensure unique IDs like Man1, Man2

    # --- Step 1: Attempt to place one from each non-empty category ---
    # Create a list of category_lists that are not empty
    potential_categories = []
    if humans_list:
        potential_categories.append(humans_list)
    if animals_list:
        potential_categories.append(animals_list)
    if vehicles_list:
        potential_categories.append(vehicles_list)
    
    random.shuffle(potential_categories) # Shuffle to avoid bias in selection order

    for category_list in potential_categories:
        if len(placed_instances) < num_cells_to_fill:
            # All lists in potential_categories are guaranteed to be non-empty here
            chosen_type = random.choice(category_list)
            type_counts[chosen_type] = type_counts.get(chosen_type, 0) + 1
            unique_id = f"{chosen_type}{type_counts[chosen_type]}"
            placed_instances.append(unique_id)
        else:
            # Reached fill limit, no need to check other categories for guaranteed pick
            break 
                
    # --- Step 2: Fill remaining slots randomly if any ---
    num_remaining_slots = num_cells_to_fill - len(placed_instances)
    
    if num_remaining_slots > 0:
        all_object_types = humans_list + animals_list + vehicles_list
        if all_object_types: # Proceed only if there are types to choose from
            for _ in range(num_remaining_slots):
                if len(placed_instances) >= num_cells_to_fill: # Defensive check
                    break
                chosen_type = random.choice(all_object_types)
                type_counts[chosen_type] = type_counts.get(chosen_type, 0) + 1
                unique_id = f"{chosen_type}{type_counts[chosen_type]}"
                placed_instances.append(unique_id)
                
    # --- Step 3: Place on grid ---
    grid = [['.' for _ in range(N)] for _ in range(N)]
    all_coordinates = [(r, c) for r in range(N) for c in range(N)]
    
    num_objects_to_actually_place = len(placed_instances)
    chosen_coordinates = random.sample(all_coordinates, num_objects_to_actually_place)

    json_data_to_save = {} 
    for i, (r, c) in enumerate(chosen_coordinates):
        grid[r][c] = placed_instances[i]
        x_coord = c
        y_coord = N - 1 - r 
        json_data_to_save[f"({x_coord},{y_coord})"] = grid[r][c]
    
    # --- Step 4: Write to JSON file ---
    output_filename = ""
    try:
        output_filename = 'grid_details_'+str(N)+'_'+'ratio_'+str(fill_ratio*100)+'.json'
        with open(output_filename, 'w') as f:
            json.dump(json_data_to_save, f, indent=4, sort_keys=True)
        print(f"Grid data successfully saved to {output_filename}")
    except IOError:
        print(f"Error: Could not write to file {output_filename}")
        
    return grid, output_filename