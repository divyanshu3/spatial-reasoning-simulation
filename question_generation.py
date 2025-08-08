import json
import random
from typing import List, Dict, Tuple, Any

def generate_questions(grid_details_filename, templates_filename, actions_filename,
                                           orientations_list, output_prompts_filename, prompts_count):
    """
    Generates prompts from Tier 1 templates (with all object orientations stated)
    using grid data and saves them to a JSON file.
    """
    try:
        with open(grid_details_filename, 'r') as f:
            grid_data_raw = json.load(f)
    except FileNotFoundError:
        print(f"Error: Grid details file '{grid_details_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{grid_details_filename}'.")
        return

    try:
        with open(templates_filename, 'r') as f:
            templates_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Templates file '{templates_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{templates_filename}'.")
        return
    
    try:
        with open(actions_filename, 'r') as f: actions_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Action file '{actions_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{actions_filename}'.")
        return

    if not grid_data_raw:
        print("Error: Grid data from file is empty.")
        return
        
    object_positions = {} 
    all_object_ids_on_grid = list(grid_data_raw.values()) # Get all object IDs present on the grid

    for coord_str, obj_id in grid_data_raw.items():
        try:
            x, y = parse_coordinates(coord_str)
            object_positions[obj_id] = (x, y) 
        except ValueError as e:
            print(f"Warning: Skipping invalid coordinate string '{coord_str}' in grid data: {e}")
            continue # Skip this entry
    
    if not object_positions: # No valid objects were parsed from grid_data_raw
        print("Error: No valid objects could be parsed from the grid data.")
        return
    
    # Ensure all_object_ids_on_grid only contains objects that were successfully parsed
    all_object_ids_on_grid = [obj_id for obj_id in all_object_ids_on_grid if obj_id in object_positions]
    if not all_object_ids_on_grid:
        print("Error: No objects available after parsing grid positions.")
        return

    max_coord = max(c for pos in object_positions.values() for c in pos) if object_positions else -1
    N = max_coord + 1
    all_actions = actions_data.get("performable_actions", [])

    all_generated_prompts = []
    global_prompt_id_counter = 1
    
    complexity_level = (templates_data.get("complexity_level")).lower()

    for template_info in templates_data.get("prompt_templates", []):
        template_id_source = template_info["id"]
        template_string = template_info["template_string"]
        placeholders_in_template = set(template_info.get("placeholders", [])) # For checking substitutions
        
        generated_count_for_template = 0
        used_prompt_params_keys = set() 
        max_attempts_per_unique_prompt = 100 # Try up to 100 times to find a unique set of params

        for attempt_num in range(max_attempts_per_unique_prompt * prompts_count):
            if generated_count_for_template >= prompts_count:
                break

            prompt_params = {}
            current_selection_key_parts = [] # To build a key for uniqueness check

            # Select Agent
            if not all_object_ids_on_grid: continue
            agent_id = random.choice(all_object_ids_on_grid)
            agent_x, agent_y = object_positions[agent_id]
            agent_orientation = random.choice(orientations_list)
            
            prompt_params["[AGENT_ID]"] = agent_id
            prompt_params["[AGENT_X]"] = str(agent_x)
            prompt_params["[AGENT_Y]"] = str(agent_y)
            prompt_params["[AGENT_ORIENTATION]"] = agent_orientation
            current_selection_key_parts.extend([agent_id, agent_orientation])

            if template_id_source in ("1","2") and complexity_level == "low": # reading templates from level 1 file
                available_targets = [oid for oid in all_object_ids_on_grid if oid != agent_id]
                if not available_targets: continue
                
                target_object_id = random.choice(available_targets)
                target_x, target_y = object_positions[target_object_id]
                target_object_orientation = random.choice(orientations_list) # New

                prompt_params["[TARGET_OBJECT_ID]"] = target_object_id
                prompt_params["[TARGET_OBJECT_X]"] = str(target_x)
                prompt_params["[TARGET_OBJECT_Y]"] = str(target_y)
                prompt_params["[TARGET_OBJECT_ORIENTATION]"] = target_object_orientation # New
                current_selection_key_parts.extend([target_object_id, target_object_orientation])

            elif template_id_source == "1" and complexity_level == "medium": # Template T1.C equivalent
                potential_obj_for_a_b = [oid for oid in all_object_ids_on_grid if oid != agent_id]
                if len(potential_obj_for_a_b) < 2: continue
                
                obj_a_id, obj_b_id = random.sample(potential_obj_for_a_b, 2)
                obj_a_x, obj_a_y = object_positions[obj_a_id]
                obj_b_x, obj_b_y = object_positions[obj_b_id]
                
                obj_a_orientation = random.choice(orientations_list) # New
                obj_b_orientation = random.choice(orientations_list) # New

                rel_dir_a = determine_relative_direction(agent_x, agent_y, agent_orientation, obj_a_x, obj_a_y)
                rel_dir_b = determine_relative_direction(agent_x, agent_y, agent_orientation, obj_b_x, obj_b_y)

                if not rel_dir_a or not rel_dir_b or rel_dir_a == "In the same cell as" or rel_dir_b == "In the same cell as":
                    continue

                prompt_params["[OBJECT_A_ID]"] = obj_a_id
                prompt_params["[OBJECT_A_X]"] = str(obj_a_x)
                prompt_params["[OBJECT_A_Y]"] = str(obj_a_y)
                prompt_params["[OBJECT_A_ORIENTATION]"] = obj_a_orientation # New
                prompt_params["[RELATIVE_DIR_A_FROM_AGENT]"] = rel_dir_a
                
                prompt_params["[OBJECT_B_ID]"] = obj_b_id
                prompt_params["[OBJECT_B_X]"] = str(obj_b_x)
                prompt_params["[OBJECT_B_Y]"] = str(obj_b_y)
                prompt_params["[OBJECT_B_ORIENTATION]"] = obj_b_orientation # New
                prompt_params["[RELATIVE_DIR_B_FROM_AGENT]"] = rel_dir_b
                current_selection_key_parts.extend(sorted([obj_a_id, obj_a_orientation, obj_b_id, obj_b_orientation]))
            
            elif template_id_source == "2" and complexity_level == "medium": # Hypothetical Reorientation Template
                specific_params, specific_key_parts = generate_params_for_t2_hypothetical(
                    agent_id, object_positions, all_object_ids_on_grid, orientations_list)
                if specific_params and specific_key_parts:
                    prompt_params.update(specific_params)
                    current_selection_key_parts.extend(specific_key_parts)
                else: continue

            elif template_id_source == "1" and complexity_level == "high":
                if len(all_actions) < 2:
                    print(f"Warning: Cannot generate multi-step prompt for template '{template_id_source}'. Need at least 2 performable actions, but found {len(all_actions)}.")
                    continue
                num_actions = random.randint(2, len(all_actions)) # Generate a sequence of 2 to N actions
                specific_params, specific_key_parts = _generate_params_for_dynamic_t3(agent_id, num_actions, object_positions, all_object_ids_on_grid, N, orientations_list, all_actions)
                if specific_params and specific_key_parts:
                    prompt_params.update(specific_params)
                    current_selection_key_parts.extend(specific_key_parts)
                else:
                    continue

            selection_key = tuple(current_selection_key_parts)
            if selection_key in used_prompt_params_keys:
                continue
            
            current_prompt_text = template_string
            all_placeholders_successfully_replaced = True
            for placeholder_name in placeholders_in_template:
                if placeholder_name in prompt_params:
                    current_prompt_text = current_prompt_text.replace(placeholder_name, prompt_params[placeholder_name])
                else:
                    # This means a required placeholder for this template was not assigned a value
                    # print(f"Warning: Placeholder {placeholder_name} for template {template_id_source} was not in prompt_params.")
                    all_placeholders_successfully_replaced = False
                    break 
            
            if all_placeholders_successfully_replaced:
                all_generated_prompts.append({
                    "complexity_level":complexity_level,
                    "prompt_id": f"{global_prompt_id_counter}",
                    "template_id_source": template_id_source,
                    "generated_prompt_text": current_prompt_text
                })
                used_prompt_params_keys.add(selection_key)
                generated_count_for_template += 1
                global_prompt_id_counter += 1

        if generated_count_for_template < 3:
            print(f"Warning: Could only generate {generated_count_for_template} unique prompts for template ID '{template_id_source}' after {max_attempts_per_unique_prompt * prompts_count} attempts for template file {templates_filename}")


    try:
        with open(output_prompts_filename, 'w') as f:
            json.dump(all_generated_prompts, f, indent=4)
        print(f"\nSuccessfully generated {len(all_generated_prompts)} prompts and saved to '{output_prompts_filename}'.")
    except IOError:
        print(f"Error: Could not write prompts to file '{output_prompts_filename}'.")
def parse_coordinates(coord_str):
    """Converts a coordinate string like "(x,y)" to an (int(x), int(y)) tuple."""
    try:
        parts = coord_str.strip("()").split(',')
        return int(parts[0]), int(parts[1])
    except Exception as e: # More general exception for parsing
        raise ValueError(f"Invalid coordinate string format: {coord_str} (Error: {e})")

def get_object_at_coord(grid_data, x, y): # Not directly used in generate_prompts but good helper
    """Gets the object ID at a given (x,y) in the grid_data dictionary."""
    return grid_data.get(f"({x},{y})")

def determine_relative_direction(agent_x, agent_y, agent_orientation, target_x, target_y):
    # """
    # Determines the primary relative direction of a target from an agent's perspective.
    # Returns one of "Left", "Right", "In-Front", "Behind", or None if ambiguous/same cell.
    # """
    # dx = target_x - agent_x
    # dy = target_y - agent_y

    # if dx == 0 and dy == 0:
    #     return "In the same cell as" # Or None, depending on how you want to handle

    # if agent_orientation == 'North':
    #     if dx == 0 and dy > 0: return "In-Front"
    #     if dx == 0 and dy < 0: return "Behind"
    #     if dy == 0 and dx < 0: return "Left"
    #     if dy == 0 and dx > 0: return "Right"
    #     if abs(dy) >= abs(dx): return "In-Front" if dy > 0 else "Behind"
    #     else: return "Right" if dx > 0 else "Left"
    # elif agent_orientation == 'South':
    #     if dx == 0 and dy < 0: return "In-Front"
    #     if dx == 0 and dy > 0: return "Behind"
    #     if dy == 0 and dx > 0: return "Left"
    #     if dy == 0 and dx < 0: return "Right"
    #     if abs(dy) >= abs(dx): return "In-Front" if dy < 0 else "Behind"
    #     else: return "Left" if dx > 0 else "Right"
    # elif agent_orientation == 'East':
    #     if dy == 0 and dx > 0: return "In-Front"
    #     if dy == 0 and dx < 0: return "Behind"
    #     if dx == 0 and dy > 0: return "Left"
    #     if dx == 0 and dy < 0: return "Right"
    #     if abs(dx) >= abs(dy): return "In-Front" if dx > 0 else "Behind"
    #     else: return "Left" if dy > 0 else "Right"
    # elif agent_orientation == 'West':
    #     if dy == 0 and dx < 0: return "In-Front"
    #     if dy == 0 and dx > 0: return "Behind"
    #     if dx == 0 and dy < 0: return "Left"
    #     if dx == 0 and dy > 0: return "Right"
    #     if abs(dx) >= abs(dy): return "In-Front" if dx < 0 else "Behind"
    #     else: return "Left" if dy < 0 else "Right"
    # return None # Should ideally not be reached if logic above is comprehensive
    """
    Determines the relative direction (8-way) of a target from an agent's perspective.
    Returns one of 8 relative directions (e.g., "In-Front", "In-Front-Right", "Right", etc.)
    """
    dx = target_x - agent_x
    dy = target_y - agent_y

    if dx == 0 and dy == 0:
        return "Error: Reference and Target are in the same cell."

    # Step 1: Determine the absolute grid direction from agent to target
    # This simplified logic uses quadrants. Any non-axial vector is considered diagonal.
    dx_sign = 1 if dx > 0 else -1 if dx < 0 else 0
    dy_sign = 1 if dy > 0 else -1 if dy < 0 else 0
    
    absolute_direction = ""
    if   (dx_sign, dy_sign) == (0, 1):   absolute_direction = "North"
    elif (dx_sign, dy_sign) == (1, 1):   absolute_direction = "North-East"
    elif (dx_sign, dy_sign) == (1, 0):   absolute_direction = "East"
    elif (dx_sign, dy_sign) == (1, -1):  absolute_direction = "South-East"
    elif (dx_sign, dy_sign) == (0, -1):  absolute_direction = "South"
    elif (dx_sign, dy_sign) == (-1, -1): absolute_direction = "South-West"
    elif (dx_sign, dy_sign) == (-1, 0):  absolute_direction = "West"
    elif (dx_sign, dy_sign) == (-1, 1):  absolute_direction = "North-West"
    
    if not absolute_direction:
        return "Error: Could not determine absolute direction." # Should not happen

    # Step 2: Translate absolute direction to relative direction
    # Define compass roses for absolute and relative directions
    absolute_rose = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    relative_rose = ["In-Front", "In-Front-Right", "Right", "Behind-Right", "Behind", "Behind-Left", "Left", "In-Front-Left"]

    try:
        # Find the index of the agent's orientation and the target's absolute direction
        agent_dir_index = absolute_rose.index(agent_orientation)
        target_abs_dir_index = absolute_rose.index(absolute_direction)

        # The relative direction is found by the difference in indices on the compass rose
        # We use modulo arithmetic to wrap around the compass
        relative_index = (target_abs_dir_index - agent_dir_index) % 8
        return relative_rose[relative_index]
        
    except ValueError:
        return f"Error: Invalid orientation '{agent_orientation}' or calculated direction '{absolute_direction}'."

def generate_params_for_t2_hypothetical(agent_id, object_positions, all_object_ids, orientations):
    """Finds two other distinct objects for Template T2.4."""
    potential_targets = [oid for oid in all_object_ids if oid != agent_id]
    if len(potential_targets) < 2: return None, None
    
    obj_b_id, obj_c_id = random.sample(potential_targets, 2)
    obj_b_pos = object_positions[obj_b_id]
    obj_c_pos = object_positions[obj_c_id]
    
    params = {
        "[OBJECT_B_TO_FACE_ID]": obj_b_id, "[OBJECT_B_TO_FACE_X]": str(obj_b_pos[0]), "[OBJECT_B_TO_FACE_Y]": str(obj_b_pos[1]),
        "[OBJECT_B_ORIENTATION]": random.choice(orientations),
        "[OBJECT_C_TO_LOCATE_ID]": obj_c_id, "[OBJECT_C_TO_LOCATE_X]": str(obj_c_pos[0]), "[OBJECT_C_TO_LOCATE_Y]": str(obj_c_pos[1]),
        "[OBJECT_C_ORIENTATION]": random.choice(orientations)
    }
    key_parts = sorted([obj_b_id, obj_c_id])
    return params, key_parts

# These functions are assumed to be defined as in our previous discussions.
def is_move_valid(new_pos: Tuple[int,int], N: int, object_positions: Dict[str, Tuple[int,int]]):
    x, y = new_pos
    if not (0 <= x < N and 0 <= y < N): return False
    if new_pos in object_positions: return False
    return True

def get_new_orientation(current_orientation: str, turn_text: str) -> str:
    rose = ["North", "East", "South", "West"]
    current_index = rose.index(current_orientation)
    if "Left" in turn_text: return rose[(current_index - 1) % 4]
    if "Right" in turn_text: return rose[(current_index + 1) % 4]
    if "around" in turn_text or "Reverse" in turn_text: return rose[(current_index + 2) % 4]
    return current_orientation

def get_new_position(current_pos: Tuple[int,int], current_orientation: str, move_text: str) -> Tuple[int,int]:
    x, y = current_pos
    num_steps = 1
    if "two steps" in move_text: num_steps = 2
    if "three steps" in move_text: num_steps = 3
    relative_direction = ""
    if "Front" in move_text or "forward" in move_text: relative_direction = "In-Front"
    elif "Behind" in move_text or "backward" in move_text: relative_direction = "Behind"
    elif "Left" in move_text: relative_direction = "Left"
    elif "Right" in move_text: relative_direction = "Right"
    dx, dy = 0, 0
    if current_orientation == 'North':
        if relative_direction == 'In-Front': dy = 1
        elif relative_direction == 'Behind': dy = -1
        elif relative_direction == 'Left': dx = -1
        elif relative_direction == 'Right': dx = 1
    elif current_orientation == 'South':
        if relative_direction == 'In-Front': dy = -1
        elif relative_direction == 'Behind': dy = 1
        elif relative_direction == 'Left': dx = 1
        elif relative_direction == 'Right': dx = -1
    elif current_orientation == 'East':
        if relative_direction == 'In-Front': dx = 1
        elif relative_direction == 'Behind': dx = -1
        elif relative_direction == 'Left': dy = 1
        elif relative_direction == 'Right': dy = -1
    elif current_orientation == 'West':
        if relative_direction == 'In-Front': dx = -1
        elif relative_direction == 'Behind': dx = 1
        elif relative_direction == 'Left': dy = -1
        elif relative_direction == 'Right': dy = 1
    return (x + dx * num_steps, y + dy * num_steps)

# --- NEW: Helper for generating parameters for the DYNAMIC T3 template ---
def _generate_params_for_dynamic_t3(agent_id, num_actions, object_positions, all_object_ids, N, orientations, all_actions):
    """Finds a valid scenario for the dynamic Tier 3 template."""
    if len(all_object_ids) < 2: return None, None
    target_id = random.choice([oid for oid in all_object_ids if oid != agent_id])
    
    temp_obstacles = {pos for id, pos in object_positions.items() if id != agent_id}
    current_pos, current_ori = object_positions[agent_id], random.choice(orientations)
    initial_pos, initial_ori = current_pos, current_ori
    
    action_sequence, action_text_list = [], []
    for i in range(num_actions):
        found_valid_action, attempts = False, 0
        while not found_valid_action and attempts < 50:
            attempts += 1
            action_obj = random.choice(all_actions)
            next_pos, next_ori = current_pos, current_ori
            if "translational" in action_obj['type']:
                next_pos = get_new_position(current_pos, current_ori, action_obj['text'])
                if is_move_valid(next_pos, N, temp_obstacles):
                    found_valid_action = True
            elif "rotational" in action_obj['type']:
                next_ori = get_new_orientation(current_ori, action_obj['text'])
                found_valid_action = True
        
        if not found_valid_action: return None, None
        current_pos, current_ori = next_pos, next_ori
        action_sequence.append(action_obj)
        action_text_list.append(f"{i+1}. {action_obj['text']}")
    
    params = {
        "[AGENT_ID]": agent_id,
        "[AGENT_X_INITIAL]": str(initial_pos[0]), "[AGENT_Y_INITIAL]": str(initial_pos[1]),
        "[AGENT_ORIENTATION_INITIAL]": initial_ori,
        "[TARGET_OBJECT_ID]": target_id,
        "[TARGET_OBJECT_X]": str(object_positions[target_id][0]), "[TARGET_OBJECT_Y]": str(object_positions[target_id][1]),
        "[TARGET_OBJECT_ORIENTATION]": random.choice(orientations),
        "[ACTION_SEQUENCE_LIST_TEXT]": ",".join(action_text_list)
    }
    key_parts = sorted([str(target_id)] + [str(act['id']) for act in action_sequence])
    return params, key_parts