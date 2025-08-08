import json, re
from typing import List, Dict, Tuple, Any
from collections import defaultdict

def filter_question_answer(question_pool_file, answer_pool_file, total_questions_required, question_set_file, answer_set_file):
    """
    Filters questions based on template_id and answer type, creates a balanced 
    dataset for each template, and returns a combined analysis.

    It ensures that for each template_id_source, there is a balanced set of questions
    for all 8 directions.

    Args:
        question_pool_file (str): The file path for the JSON question pool.
        answer_pool_file (str): The file path for the JSON answer pool.
        total_questions_required (int): The desired number of questions per direction, per template.
        question_set_file (str): The filename to save the new balanced question set.
        answer_set_file (str): The filename to save the new balanced answer set.

    Returns:
        dict: A dictionary containing the analysis, or an empty dict if validation fails.
    """
    try:
        # Load the question and answer pools from their respective JSON files
        with open(question_pool_file, 'r') as f:
            question_pool = json.load(f)

        with open(answer_pool_file, 'r') as f:
            answer_pool = json.load(f)

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the file paths are correct.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from a file: {e}")
        return {}

    # Create a dictionary to map prompt_id to expected_answer for quick lookup
    answer_map = {item['prompt_id']: item['expected_answer'] for item in answer_pool}

    # Group questions first by template_id, then by expected answer type
    questions_by_template_and_answer = defaultdict(lambda: defaultdict(list))
    for question in question_pool:
        prompt_id = question.get('prompt_id')
        template_id = question.get('template_id_source')
        if prompt_id in answer_map and template_id:
            answer_text = answer_map[prompt_id]
            if answer_text == 'incorrect prompt':
                continue
            questions_by_template_and_answer[template_id][answer_text].append(question)

    # --- VALIDATION AND ANALYSIS PER TEMPLATE ---
    template_analysis = {}
    if not questions_by_template_and_answer:
        print("Error: No questions could be grouped by template_id and answer. Check your input files.")
        return {}
    
    for template_id, answer_groups in questions_by_template_and_answer.items():
        # Check if each template has all 8 directions
        if len(answer_groups) != 8:
            print(f"Error: Template ID '{template_id}' must have questions for exactly 8 unique answer types, but found {len(answer_groups)}.")
            return {}
        
        answer_counts = {key: len(value) for key, value in answer_groups.items()}
        min_count_for_template = min(answer_counts.values())
        template_analysis[template_id] = {
            'distribution': answer_counts,
            'min_count': min_count_for_template
        }

    # --- DETERMINE GLOBAL LIMITS ---
    # Find the overall minimum count across all templates, which is the true bottleneck
    global_min_count = min(info['min_count'] for info in template_analysis.values())
    
    # Compare this global minimum with the user's requested number
    final_questions_per_type = min(global_min_count, total_questions_required)

    # --- CREATE AND WRITE NEW DATASETS ---
    final_question_set = []
    final_answer_set = []
    new_prompt_id_counter = 1 # Initialize counter for new prompt_ids

    # Iterate through the grouped data to build the final balanced set
    for template_id, answer_groups in questions_by_template_and_answer.items():
        for answer_type, questions in answer_groups.items():
            # Select the required number of questions for this slot
            selected_questions = questions[:final_questions_per_type]
            
            for original_question in selected_questions:
                new_question = original_question.copy()
                new_question['prompt_id'] = str(new_prompt_id_counter)
                final_question_set.append(new_question)
                
                answer_obj = {
                    'prompt_id': str(new_prompt_id_counter),
                    'expected_answer': answer_type
                }
                final_answer_set.append(answer_obj)
                new_prompt_id_counter += 1
    
    try:
        with open(question_set_file, 'w') as f:
            json.dump(final_question_set, f, indent=4)
        print(f"\nSuccessfully created '{question_set_file}' with {len(final_question_set)} total questions.")

        with open(answer_set_file, 'w') as f:
            json.dump(final_answer_set, f, indent=4)
        print(f"Successfully created '{answer_set_file}' with {len(final_answer_set)} total answers.")
    except IOError as e:
        print(f"Error: Could not write to output files. {e}")
        return {}


    # Return the analysis results
    return {
        'template_analysis': template_analysis,
        'overall_minimum_count': global_min_count,
        'final_questions_per_type_per_template': final_questions_per_type
    }



def solve_questions_from_file(input_questions_filename: str, output_answers_filename: str,populated_grid):
    """
    Loads questions from a JSON file, solves them using the appropriate solver,
    and saves the answers to another JSON file.

    Args:
        input_questions_filename (str): Path to the JSON file containing questions.
                                      Each prompt object should have "prompt_id", 
                                      "template_id_source", and "generated_prompt_text".
        grid_details_json_filename (str): Path to the JSON file with grid object positions
                                          in format {"(x,y)": "ObjectID"}.
        output_answers_filename (str): Path to save the JSON file with answers.
    """
    try:
        with open(input_questions_filename, 'r') as f:
            questions_to_solve = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input questions file '{input_questions_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_questions_filename}'.")
        return

    # try:
    #     with open(grid_details_json_filename, 'r') as f:
    #         grid_data_raw = json.load(f)
    # except FileNotFoundError:
    #     print(f"Error: Grid details file '{grid_details_json_filename}' not found.")
    #     return
    # except json.JSONDecodeError:
    #     print(f"Error: Could not decode JSON from '{grid_details_json_filename}'.")
    #     return

    # if not grid_data_raw:
    #     print("Error: Loaded grid data is empty.")
    #     return

    # Convert raw grid data (dict of "(x,y)": "ID") to 2D array and determine N
    # max_x, max_y = 0, 0
    # parsed_coords = {}
    # for coord_str, obj_id in grid_data_raw.items():
    #     try:
    #         x, y = parse_coordinates(coord_str.strip("()").split(',')) # parse_coordinates expects list/tuple
    #         parsed_coords[(x,y)] = obj_id
    #         max_x = max(max_x, x)
    #         max_y = max(max_y, y)
    #     except ValueError:
    #         print(f"Warning: Skipping invalid coordinate '{coord_str}' in grid details file.")
    #         continue
    
    # N = max(max_x, max_y) + 1 # Assuming square grid starting at 0,0
    # grid_details_2d_array = [['.' for _ in range(N)] for _ in range(N)]
    # for (x,y), obj_id in parsed_coords.items():
    #     row_from_top = (N - 1) - y # Convert bottom-left (0,0) y to top-left (0,0) row index
    #     col_from_left = x
    #     if 0 <= row_from_top < N and 0 <= col_from_left < N:
    #         grid_details_2d_array[row_from_top][col_from_left] = obj_id
    #     # else: print(f"Warning: Coordinate ({x},{y}) for {obj_id} is out of inferred grid bounds (N={N}).")


    answers_list = []
    for prompt_entry in questions_to_solve:
        complexity_level = (prompt_entry.get("complexity_level")).lower()
        prompt_id = prompt_entry.get("prompt_id")
        prompt_text = prompt_entry.get("generated_prompt_text")
        template_id_source = prompt_entry.get("template_id_source")

        if not all([prompt_id, prompt_text, template_id_source]):
            print(f"Warning: Skipping invalid prompt entry: {prompt_entry}")
            continue

        answer = "Error: Unsupported template ID or prompt structure."
        # This function currently only supports solving questions from template ID "1"
        if template_id_source in ("1","2") and complexity_level == "low":
            answer = solve_template1_prompt(prompt_text)
        elif template_id_source in ("1","2") and complexity_level == "medium":
            answer = solve_template2_prompt(prompt_text,template_id_source)
        elif template_id_source in ("1") and complexity_level == "high":
            answer = solve_template3_prompt(prompt_text,populated_grid)
        
        answers_list.append({
            "prompt_id": prompt_id,
            "expected_answer": answer 
        })

    try:
        with open(output_answers_filename, 'w') as f:
            json.dump(answers_list, f, indent=4)
        print(f"Successfully processed {len(questions_to_solve)} questions. Answers saved to '{output_answers_filename}'.")
    except IOError:
        print(f"Error: Could not write answers to file '{output_answers_filename}'.")

def determine_relative_direction(agent_x, agent_y, agent_orientation, target_x, target_y):
    # """
    # Determines the primary relative direction of a target from an agent's perspective.
    # Returns one of "Left", "Right", "In front", "Behind".
    # """
    # dx = target_x - agent_x
    # dy = target_y - agent_y

    # if dx == 0 and dy == 0:
    #     return "Error: Agent and Target are in the same cell."

    # if agent_orientation == 'North':
    #     if dx == 0 and dy > 0: return "In front"
    #     if dx == 0 and dy < 0: return "Behind"
    #     if dy == 0 and dx < 0: return "Left"
    #     if dy == 0 and dx > 0: return "Right"
    #     if abs(dy) >= abs(dx):
    #         return "In front" if dy > 0 else "Behind"
    #     else:
    #         return "Right" if dx > 0 else "Left"
    # elif agent_orientation == 'South':
    #     if dx == 0 and dy < 0: return "In front"
    #     if dx == 0 and dy > 0: return "Behind"
    #     if dy == 0 and dx > 0: return "Left"
    #     if dy == 0 and dx < 0: return "Right"
    #     if abs(dy) >= abs(dx):
    #         return "In front" if dy < 0 else "Behind"
    #     else:
    #         return "Left" if dx > 0 else "Right"
    # elif agent_orientation == 'East':
    #     if dy == 0 and dx > 0: return "In front"
    #     if dy == 0 and dx < 0: return "Behind"
    #     if dx == 0 and dy > 0: return "Left"
    #     if dx == 0 and dy < 0: return "Right"
    #     if abs(dx) >= abs(dy):
    #         return "In front" if dx > 0 else "Behind"
    #     else:
    #         return "Left" if dy > 0 else "Right"
    # elif agent_orientation == 'West':
    #     if dy == 0 and dx < 0: return "In front"
    #     if dy == 0 and dx > 0: return "Behind"
    #     if dx == 0 and dy < 0: return "Left"
    #     if dx == 0 and dy > 0: return "Right"
    #     if abs(dx) >= abs(dy):
    #         return "In front" if dx < 0 else "Behind"
    #     else:
    #         return "Left" if dy < 0 else "Right"
    
    # return "Error: Unknown orientation or ambiguous case."
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
def get_absolute_direction(from_x: int, from_y: int, to_x: int, to_y: int) -> str | None:
    """
    Calculates the absolute cardinal/intercardinal direction of a vector.
    Returns "North", "North-East", etc., or None if points are the same.
    """
    dx = to_x - from_x
    dy = to_y - from_y
    if dx == 0 and dy == 0:
        return None

    dx_sign = 1 if dx > 0 else -1 if dx < 0 else 0
    dy_sign = 1 if dy > 0 else -1 if dy < 0 else 0
    
    direction_map = {
        (0, 1): "North", (1, 1): "North-East", (1, 0): "East", (1, -1): "South-East",
        (0, -1): "South", (-1, -1): "South-West", (-1, 0): "West", (-1, 1): "North-West"
    }
    return direction_map.get((dx_sign, dy_sign))
def get_new_orientation(current_orientation: str, turn_text: str) -> str:
    """Calculates the new orientation after a turn."""
    rose = ["North", "East", "South", "West"]
    current_index = rose.index(current_orientation)
    turn_text = turn_text.lower()
    if "left" in turn_text: return rose[(current_index - 1) % 4]
    if "right" in turn_text: return rose[(current_index + 1) % 4]
    if "around" in turn_text or "reverse" in turn_text: return rose[(current_index + 2) % 4]
    return current_orientation
def get_new_position(current_pos, current_orientation, move_text):
    # ... (This function is correct and remains unchanged) ...
    x, y = current_pos; num_steps = 1
    if "two steps" in move_text: num_steps = 2
    if "three steps" in move_text: num_steps = 3
    relative_direction_map = {'North':{'In-Front':(0,1),'Behind':(0,-1),'Left':(-1,0),'Right':(1,0)},'South':{'In-Front':(0,-1),'Behind':(0,1),'Left':(1,0),'Right':(-1,0)},'East':{'In-Front':(1,0),'Behind':(-1,0),'Left':(0,1),'Right':(0,-1)},'West':{'In-Front':(-1,0),'Behind':(1,0),'Left':(0,-1),'Right':(0,1)}}
    move_dir_text = ""
    if "Front" in move_text or "forward" in move_text: move_dir_text = "In-Front"
    elif "Behind" in move_text or "backward" in move_text: move_dir_text = "Behind"
    elif "Left" in move_text: move_dir_text = "Left"
    elif "Right" in move_text: move_dir_text = "Right"
    dx, dy = relative_direction_map.get(current_orientation, {}).get(move_dir_text, (0, 0))
    return (x + dx * num_steps, y + dy * num_steps)
def is_move_valid(new_pos: tuple, N: int, occupied_positions: set):
    """Checks if a move is valid (within bounds and not into an occupied cell)."""
    x, y = new_pos
    if not (0 <= x < N and 0 <= y < N):
        return False # Out of bounds
    if new_pos in occupied_positions:
        return False # Occupied by another object
    return True
# --- Solver function for level 1 ---
def solve_template1_prompt(prompt_text: str):
    """
    Solves prompts based on the narrative structure used for both
    Template ID "1" and "2" from your prompts_level_1.json file.
    """
    # This flexible regex first captures the two main entities (A and B),
    # then separately captures who is the observer and who is the observed in the question.
    pattern_str = re.compile(
        # Part 1: Capture Entity A (the observer mentioned first in the sentence)
        r"Consider the observer, (\w+), who is at grid position \((\d+),(\d+)\) and is facing (\w+)\.\s*"
        # Part 2: Capture Entity B (the second entity mentioned)
        r"(\w+), which is located at \((\d+),(\d+)\) and is facing (\w+)\.\s*"
        # Part 3: Capture the actual observer and target from the question itself
        r"Based on ([\w\d]+)'s current perspective, in which primary direction is ([\w\d]+) located\?",
        re.IGNORECASE
    )
    
    match = re.fullmatch(pattern_str, prompt_text.strip())

    if not match:
        return "Error: Prompt text does not match the expected structure."

    try:
        # Store details for both entities mentioned in the premise
        entity_A_details = {
            "id": match.group(1),
            "pos": (int(match.group(2)), int(match.group(3))),
            "ori": match.group(4)
        }
        entity_B_details = {
            "id": match.group(5),
            "pos": (int(match.group(6)), int(match.group(7))),
            "ori": match.group(8)
        }
        
        # Identify who is the observer and who is the target IN THE QUESTION
        observer_id_in_question = match.group(9)
        target_id_in_question = match.group(10)

        # Dynamically assign the roles for our calculation
        if observer_id_in_question == entity_A_details["id"]:
            # This handles Template ID "1" case
            agent_pos = entity_A_details["pos"]
            agent_orientation = entity_A_details["ori"]
            target_pos = entity_B_details["pos"]
        elif observer_id_in_question == entity_B_details["id"]:
            # This handles Template ID "2" case
            agent_pos = entity_B_details["pos"]
            agent_orientation = entity_B_details["ori"]
            target_pos = entity_A_details["pos"]
        else:
            return "Error: Observer in question does not match entities in premise."

    except (IndexError, ValueError):
        return "Error: Could not parse all required components from the prompt."

    # Perform the calculation with the correctly assigned roles
    calculated_direction = determine_relative_direction(
        agent_pos[0], agent_pos[1], 
        agent_orientation, 
        target_pos[0], target_pos[1]
    )
    return calculated_direction

# --- Solver function for level 2 ---
def solve_template2_prompt(prompt_text: str,template_id):
   
    if(template_id == '2'): return solve_template_hypothetical_reorientation(prompt_text)

    all_8_relative_directions = "In-Front-Right|In-Front-Left|Behind-Right|Behind-Left|In-Front|Behind|Left|Right"

    # The modified pattern string using an f-string to insert the direction list
    pattern_str = re.compile(
        r"On a grid, (\w+) is at \((\d+),(\d+)\) looking towards the (\w+)\. "  # Agent: ID(1), X(2), Y(3), Ori(4)
        r"From \1's point of view, (\w+) is at \((\d+),(\d+)\) facing (\w+) and appears to their (" + all_8_relative_directions + r"), "  # ObjA: ID(5),X(6),Y(7),Ori(8),RelDirA(9)
        r"while (\w+) is at \((\d+),(\d+)\) facing (\w+) and appears to their (" + all_8_relative_directions + r")\. "  # ObjB: ID(10),X(11),Y(12),Ori(13),RelDirB(14)
        r"From \1's perspective, in which primary direction is \10 located relative to \5\?"
    )

    match = re.fullmatch(pattern_str, prompt_text.strip())

    if not match:
        return "Error: Prompt text does not match the expected Tier 2 template structure."

    try:
        # Agent details (whose perspective is used for final interpretation)
        # agent_id = match.group(1) # Not directly used in final calculation beyond its orientation
        # agent_x = int(match.group(2)) # Not directly used in final calculation
        # agent_y = int(match.group(3)) # Not directly used in final calculation
        agent_orientation = match.group(4) # CRUCIAL for final interpretation

        # Object A details (the reference point for the final question)
        # object_a_id = match.group(5)
        object_a_x = int(match.group(6))
        object_a_y = int(match.group(7))
        # object_a_orientation = match.group(8) # Descriptive, not used in this specific answer logic

        # Object B details (the target point for the final question)
        # object_b_id = match.group(9)
        object_b_x = int(match.group(11))
        object_b_y = int(match.group(12))
        # object_b_orientation = match.group(12) # Descriptive, not used in this specific answer logic
        
        # rel_dir_a_text = match.group(13) # Descriptive premise, not used in calculation
        # rel_dir_b_text = match.group(14) # Descriptive premise, not used in calculation

    except IndexError:
        return "Error: Could not parse all required components from the prompt."
    except ValueError:
        return "Error: Could not convert parsed coordinates to integers."

    # Calculate the displacement vector from Object A to Object B in absolute grid terms
    delta_x_grid = object_b_x - object_a_x
    delta_y_grid = object_b_y - object_a_y

    # Interpret this displacement vector (delta_x_grid, delta_y_grid) from the AGENT's original orientation.
    # We can use determine_relative_direction by treating the AGENT's orientation as the frame of reference,
    # and the (delta_x_grid, delta_y_grid) as the coordinates of a target relative to an origin (0,0).
    calculated_direction = determine_relative_direction(0, 0, agent_orientation, delta_x_grid, delta_y_grid)
    
    return calculated_direction


def solve_template_hypothetical_reorientation(prompt_text: str) -> str:
    """Solves the Tier 2 template involving a hypothetical turn."""
    pattern_str = re.compile(
        r"Consider (\w+) at \((\d+),(\d+)\), who is initially looking towards the (\w+)\.\s*"  # Changed to \.\s*
        r"(\w+) is at grid position \((\d+),(\d+)\) and is facing (\w+)\.\s*"           # Changed to \.\s*
        r"(\w+) is at grid position \((\d+),(\d+)\) and is facing (\w+)\.\s*"           # Changed to \.\s*
        r"If \1 reoriented itself to look directly at \5, from this new perspective, "
        r"what would be the primary direction to \9\?"
    )
    match = re.fullmatch(pattern_str, prompt_text.strip())
    if not match:
        return "Error: Prompt does not match the Hypothetical Reorientation template structure."

    try:
        agent_x, agent_y = int(match.group(2)), int(match.group(3))
        obj_b_x, obj_b_y = int(match.group(6)), int(match.group(7))
        obj_c_x, obj_c_y = int(match.group(10)), int(match.group(11))
    except (IndexError, ValueError):
        return "Error: Failed to parse components from prompt."

    # Step 1: CORRECTLY determine the agent's new hypothetical orientation 
    #         by finding the absolute direction from the agent to Object B.
    new_orientation = get_absolute_direction(agent_x, agent_y, obj_b_x, obj_b_y)
    
    if not new_orientation:
        return "Error: Could not determine new hypothetical orientation (agent and obj_b might be in same cell)."

    # Step 2: Use this new valid orientation to find the relative direction to Object C
    final_direction = determine_relative_direction(agent_x, agent_y, new_orientation, obj_c_x, obj_c_y)

    return final_direction


def solve_template3_prompt(prompt_text: str, grid_details_2d_array: list) -> str:
    """
    Solves a prompt from the dynamic Tier 3 template with step-by-step validation.
    If any step is invalid, it returns 'incorrect prompt'.
    """
    try:
        # Regex to parse the prompt
        pattern_t3_narrative = re.compile(
        r"On a grid, the initial scene is set up as follows: The agent, (\w+), is at position \((\d+),(\d+)\) and is facing (\w+)\. "
        r"The target, (\w+), is at position \((\d+),(\d+)\) and is facing (\w+)\.\s*"
        r"Now, the agent \(\1\) performs the following sequence of actions in order: \((.+?)\)\.\s*"
        r"After completing all actions, from \1's new and final perspective, in which primary direction is the target \(\5\) located\?",
        re.IGNORECASE
    )
        match = re.fullmatch(pattern_t3_narrative, prompt_text.strip())
        if not match:
            return "Error: Prompt text does not match the Tier 3 template structure."

        # Extract initial states
        agent_id = match.group(1)
        current_pos = (int(match.group(2)), int(match.group(3)))
        current_ori = match.group(4)
        target_pos = (int(match.group(6)), int(match.group(7)))
        
        # Build the set of obstacle positions from the grid array
        N = len(grid_details_2d_array)
        occupied_positions = set()
        for r_idx, row in enumerate(grid_details_2d_array):
            for c_idx, cell_content in enumerate(row):
                # The agent's own starting cell is NOT an obstacle for its first move
                if cell_content != '.' and agent_id not in cell_content:
                    x, y = c_idx, N - 1 - r_idx
                    occupied_positions.add((x, y))

        # Parse and simulate the action sequence
        actions_block = match.group(9)
        actions_to_perform = [action.strip() for action in actions_block.split(',')]
        
        for action_text in actions_to_perform:
            #print(action_text)
            if "Turn" in action_text or "Face" in action_text or "Reverse" in action_text or "Make" in action_text:
                #print("before: ",current_ori)
                current_ori = get_new_orientation(current_ori, action_text)
                #print("after: ",current_ori)
            elif "Move" in action_text or "step" in action_text or "Shift" in action_text:
                next_pos = get_new_position(current_pos, current_ori, action_text)
                #print(next_pos)
                # *** CRUCIAL VALIDATION STEP ***
                # This checks if the intended move is valid before updating the position.
                if not is_move_valid(next_pos, N, occupied_positions):
                    #print("incorrect prompt")
                    return "incorrect prompt"
                
                current_pos = next_pos
        
        # If the loop completes successfully, all moves were valid.
        return determine_relative_direction(
            current_pos[0], current_pos[1], 
            current_ori, 
            target_pos[0], target_pos[1]
        )

    except Exception as e:
        return f"Error: Failed to parse or solve prompt. Details: {e}"
