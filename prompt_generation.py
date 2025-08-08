import json

def create_system_prompt(grid_data_raw: dict) -> str:
    """
    Creates a single, comprehensive system prompt containing all rules
    and the complete grid state.
    """
    # Format the grid data into a readable list
    grid_items = []
    # Sort by coordinates for a consistent order in every prompt
    try:
        sorted_coords = sorted(grid_data_raw.keys(), key=lambda c: list(map(int, c.strip("()").split(','))))
        for coord_str in sorted_coords:
            obj_id = grid_data_raw[coord_str]
            grid_items.append(f"- Object '{obj_id}' is at position {coord_str}.")
        grid_context_string = "\n".join(grid_items)
    except Exception:
        grid_context_string = "Error: Could not format grid data."


    # Combine all instructions into one system prompt
    system_prompt = (
        "You are a helpful assistant and a spatial reasoning expert. Your task is to solve a question by simulating movement on a grid based on the rules provided. Movement should only be done if it is requested in the prompt.\n"
        "First, here is the complete state of all objects on the grid of size 10x10 (0 based indexing) with coordinates on x-axis increases in east direction and coordinates on y-axis increases in north direction:\n"
        f"{grid_context_string}\n\n"
        "--- MOVEMENT RULES ---\n"
        "1. Movement should not cross the grid boundaries. It must always remain inside the grid.\n"
        "2. If after completion of the movement, the new position of the agent is already occupied by another object, that move is invalid.\n"
        "3. All mentioned actions must be performed in sequence. If any action results in a failure (due to rule 1 or 2), you must stop the process immediately and your only response should be the exact phrase: incorrect prompt\n\n"
        "--- OUTPUT FORMAT ---\n"
        "If the action sequence is valid, your answer must be only one of the 8 primary directions: "
        "Left, Right, Behind, In-Front, Behind-Left, In-Front-Left, Behind-Right, or In-Front-Right. "
        "Your answer should be given right at the end of your response, immediately in the form “###Answer:"
    )
    return system_prompt

def create_api_ready_prompts(generated_questions_filename: str, grid_details_filename: str, output_filename: str):
    """
    Loads generated questions and grid data, then creates a final JSON file
    formatted for chat-based LLM API calls.

    Args:
        generated_questions_filename (str): Path to the input JSON file containing generated questions.
        grid_details_filename (str): Path to the JSON file with grid object positions.
        output_filename (str): Path for the new JSON file to be created.
    """
    try:
        with open(generated_questions_filename, 'r') as f:
            source_questions = json.load(f)
        with open(grid_details_filename, 'r') as f:
            grid_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Could not find a required input file. {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from a file. {e}")
        return

    # Create the comprehensive system prompt once
    system_prompt_content = create_system_prompt(grid_data)

    api_ready_questions = []
    for prompt_obj in source_questions:
        prompt_id = prompt_obj.get("prompt_id")
        user_prompt_content = prompt_obj.get("generated_prompt_text")

        if not prompt_id or not user_prompt_content:
            print(f"Warning: Skipping malformed prompt object: {prompt_obj}")
            continue

        # Assemble the final structure for the API call
        final_prompt_object = {
            "id": prompt_id,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt_content
                },
                {
                    "role": "user",
                    "content": user_prompt_content
                }
            ]
        }
        api_ready_questions.append(final_prompt_object)

    # Save the final list to the output file, overriding it
    try:
        with open(output_filename, 'w') as f:
            json.dump(api_ready_questions, f, indent=4)
        print(f"Successfully created {len(api_ready_questions)} API-ready questions in '{output_filename}'.")
    except IOError as e:
        print(f"Error: Could not write to file '{output_filename}'. Details: {e}")
