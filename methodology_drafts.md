Methodology for Part 1: Grid Data Generation Framework

1. Objective and Rationale

The primary objective of this phase was to develop a robust and flexible system for programmatically generating N x N grid-based environments. These environments serve as the foundational "ground truth" for the subsequent automated creation of spatial reasoning scenarios and questions. The need for such a system arose from the requirement to produce a large, diverse, and error-free benchmark dataset for evaluating the spatial reasoning capabilities of Large Language Models (LLMs), particularly concerning relative directions. This approach aims to extend previous research, such as that by Cohn and Blackwell which also utilized template-based generation for cardinal directions, by providing a controlled yet varied set of spatial configurations. The automated nature of grid and answer generation is critical for ensuring accuracy and scalability, mitigating the potential for human error in manual scenario design.

2. System Design and Core Components

The grid generation system was designed through an iterative process, incorporating specific requirements for object representation, placement, and output format.

2.1. Grid Structure:
* A parameterizable N x N 2D grid was adopted as the base structure.
* A Cartesian coordinate system (x,y) was defined for object placement and JSON output, with (0,0) designated as the bottom-left corner and (N-1, N-1) as the top-right. For internal Python list-of-lists representation (used for console display), grid[row][column] indexing was used with row 0, col 0 being top-left.

2.2. Object Representation:
* Categorization: Objects were defined based on three main categories provided as input lists: Humans (e.g., "Man," "Woman," "Child"), Animals (e.g., "Dog," "Cat," "Horse"), and Vehicles (e.g., "Car," "Bike," "Train").
* Uniqueness: A critical requirement was that each object instance placed on the grid be unique. This was achieved by appending a numerical suffix to the object's base type (e.g., "Man1", "Man2", "Cat1"). A dictionary (type_counts) tracks the count of each base type to ensure correct suffixing.
* Orientation: Each object instance is assigned a "fixed" orientation upon creation (randomly chosen from 'N', 'S', 'E', 'W'). This attribute is stored as part of the object's representation in the output. Initially, orientation was removed but then re-introduced to support more complex reasoning tasks.

2.3. Grid Population Logic:
* Fill Ratio: The density of objects on the grid is controlled by a fill_ratio parameter (a float between 0 and 1), which determines the percentage of total cells to be occupied. The number of cells to fill is calculated as int(N*N * fill_ratio).
* Diversity Constraint: To ensure a varied representation of object categories, a specific seeding strategy was implemented. The inputs are assumed to be configured such that it's possible for at least one instance from each non-empty input category list (Humans, Animals, Vehicles) to be placed on the grid.
* The system first identifies non-empty input categories.
* It then places one randomly chosen object type from each of these non-empty categories, assigning unique IDs and orientations. The order of initial category seeding is shuffled to prevent bias if num_cells_to_fill exactly matches the number of categories.
* If additional cells still need to be filled after this initial diverse seeding (i.e., num_cells_to_fill is greater than the number of non-empty categories), these remaining slots are populated by randomly selecting object types from the combined pool of all available types.
* Random Placement: The generated unique object instances (with their orientations) are placed into randomly selected empty cells on the N x N grid.

3. Output and Persistence

Primary Output (JSON): The state of the populated grid is persisted to a JSON file.
The JSON structure is a single object (dictionary).
Keys are coordinate strings in the format "(x,y)", representing the Cartesian coordinates (0,0 at bottom-left).
Values are strings representing the object instance in the format "[objectTypeLowercase][ID],[OrientationInBrackets]" (e.g., "man1,[N]", "car2,[E]").
Only occupied cells are included as keys in the JSON object, providing a sparse representation of the grid.
Secondary Output (Console/Return Value): The Python function also generates and returns a 2D list-of-lists representation of the grid, primarily for immediate console display and debugging. Empty cells are represented by . in this display format.
4. Implementation Details

The grid generation logic was encapsulated in a Python function, currently named generate_grid_and_save_json_custom_format.
Standard Python libraries, random (for selection of types, orientations, and coordinates) and json (for file output), were utilized.
5. Rules for Future Interaction (Defined during this phase to inform grid utility)

Although not directly part of the grid generation code itself, rules for how objects (specifically "Persons") might later interact with or move within this grid were established to ensure the generated grid data would be suitable for dynamic scenarios:

Movement: Only "Person" objects can move, one step at a time, in directions relative to their current orientation (Front, Behind, Left, Right). Orientation is maintained during these translational moves.
Static Environment: All other objects are immobile.
Valid Moves:
Boundary Checks: Moves that would take a person off the grid are invalid and ignored.
Occupancy Checks: Moves into a cell already occupied by another immovable object are invalid and ignored.
This methodology resulted in a Python tool capable of producing diverse, structured, and verifiable grid-based environments, which form the essential data foundation for generating the spatial reasoning benchmark questions planned for subsequent stages of the dissertation.

Okay, here's the detailed methodology for Step 2 (Prompt Generation) and Step 3 (Prompt Answer Generation) formatted for a Markdown file.



### Step 2: Prompt Generation from Templates and Grid Data

This phase focused on automatically creating a diverse set of natural language prompts for spatial reasoning tasks. The system was designed to use predefined templates and a populated grid environment as its foundation.

**1. Objective:**
* To programmatically generate textual prompts suitable for evaluating the spatial reasoning capabilities of LLMs.
* To ensure each generated prompt is self-contained, providing all necessary information (object identities, positions, and orientations) for an LLM to attempt an answer.
* To produce a variety of prompts by leveraging different templates and randomizing object selection from a given grid state.
    

**2. Input Components:**
* [cite_start]**Populated Grid Data File (JSON):** This file (e.g., `grid_details_5_ratio_50.0.json` [cite: 1][cite_start]) provides the "ground truth" layout of objects, mapping coordinate strings like `"(x,y)"` to unique object identifiers (e.g., "Cat2", "Child1" ). [cite_start]This input grid data does *not* contain pre-set orientations for the objects.
* [cite_start]**Template Definitions File (JSON):** This file (e.g., `templates_level_1.json` ) contains a list of prompt templates. Each template definition includes:
* [cite_start]A unique `id` (e.g., "1", "2" ).
* [cite_start]A `template_string` with placeholders (e.g., `[AGENT_ID]`, `[AGENT_X]`, `[TARGET_OBJECT_ORIENTATION]` ). These templates were specifically modified to ensure all mentioned objects would have their orientations explicitly stated in the generated prompt.
* [cite_start]A list of all `placeholders` used in its `template_string`.
* [cite_start]An `expected_answer_format` field (e.g., "Spatial Direction" ).
* **List of Orientations:** A predefined Python list of possible cardinal orientations (i.e., `['North', 'South', 'East', 'West']`) to be assigned to objects within the prompt.
* **Output Filename:** A string specifying the path for the JSON file where the generated prompts will be saved.

**3. Core Prompt Generation Process (Implemented in `generate_prompts_with_all_orientations` Python function):**
* **Data Ingestion:**
* [cite_start]The system loads and parses the object IDs and their (x,y) positions from the `grid_details_filename` JSON. Coordinate strings are converted to numerical tuples, and a mapping of object IDs to their positions is created.
* [cite_start]The list of prompt templates is loaded from the `templates_filename` JSON.
* **Iterative Prompt Creation (Per Template Type):**
* [cite_start]For each template defined in the templates file, the system aims to generate a specified number of unique prompts (e.g., 3 unique prompts per template type).
* **Uniqueness Enforcement:** To ensure distinct prompts from the same template, a set tracks the combinations of key parameters (agent ID, agent orientation, target object(s) ID(s), and target object(s) orientation(s)) already used for that template.
* **Parameter Selection and Placeholder Filling Loop:**
1.  [cite_start]**Agent Selection:** An `[AGENT_ID]` is randomly chosen from the list of all objects present on the grid. Its `[AGENT_X]` and `[AGENT_Y]` coordinates are retrieved from the parsed grid data.
2.  **Dynamic Orientation Assignment:** An `[AGENT_ORIENTATION]` is randomly selected from the provided `orientations_list` and assigned to the agent for this specific prompt. [cite_start]This is critical as the input grid file does not store orientations.
3.  **Target/Other Object(s) Selection (Template-Dependent):**
    * [cite_start]For Template ID "1"  (which expects an agent and one target object): A `[TARGET_OBJECT_ID]` is randomly selected from the grid, ensuring it is distinct from the `[AGENT_ID]`. Its coordinates are retrieved. A `[TARGET_OBJECT_ORIENTATION]` is also randomly assigned from the `orientations_list`.
    * [cite_start]For Template ID "2"  (which expects an agent and two other objects, A and B): Two distinct objects, `[OBJECT_A_ID]` and `[OBJECT_B_ID]`, are randomly selected (distinct from each other and from the `[AGENT_ID]`). Their coordinates are retrieved. Random orientations (`[OBJECT_A_ORIENTATION]`, `[OBJECT_B_ORIENTATION]`) are assigned to them.
4.  [cite_start]**Premise Calculation (Specifically for Template ID "2" ):** The descriptive relative directions `[RELATIVE_DIR_A_FROM_AGENT]` and `[RELATIVE_DIR_B_FROM_AGENT]` are programmatically determined. This involves using a helper function (`determine_relative_direction`) that takes the agent's current state (position and dynamically assigned orientation) and the respective object's position to calculate the primary relative direction (Left, Right, In front, or Behind).
5.  **Uniqueness Verification:** The combination of selected objects and their assigned orientations is checked against the set of already used combinations for the current template. If a duplicate is found, the selection process for this particular prompt attempt is restarted.
6.  **Placeholder Substitution:** A dictionary mapping placeholders to their selected or calculated values is created. [cite_start]These values are then substituted into the raw `template_string`  to form the final `generated_prompt_text`.
7.  [cite_start]**Storage:** The successfully generated prompt (including a globally unique `prompt_id`, the `template_id_source`, and the `generated_prompt_text`) is added to a list of all prompts.
* A maximum number of attempts is set to generate each unique prompt to prevent infinite loops, especially if the grid is sparse or object combinations are limited.
* **File Output:** The complete list of generated prompt objects is written to the specified `output_prompts_filename` in JSON format, overriding any pre-existing file. Each prompt object contains its unique ID, source template ID, and the fully formed prompt text.

---
### Step 3: Prompt Answer Generation (Solver)

This phase focused on programmatically determining the correct answer for each generated spatial reasoning prompt, using the prompt's explicit information and the grid's ground truth.

**1. Objective:**
    * To automatically solve the generated prompts to establish a "ground truth" answer for each.
    * To provide a systematic way of evaluating LLM responses by comparing them against these programmatically derived answers.

**2. Input Components:**
    * **Generated Prompts File (JSON):** The output file from Step 2, containing a list of prompt objects, each with `prompt_id`, `template_id_source`, and `generated_prompt_text`.
    * [cite_start]**Grid Details File (JSON):** The same file used in Step 2 (e.g., `grid_details_5_ratio_50.0.json` ), providing the mapping of `"(x,y)"` coordinates to `ObjectID`.
    * **Output Filename:** A string specifying the path for the JSON file where the prompts and their solved answers will be saved.

**3. Core Answer Generation Process (Implemented in `solve_prompts_from_file` Python function):**
    * **Data Ingestion:**
        * The system loads the list of prompt objects from the `input_prompts_filename`.
        * The raw grid data (dictionary of `"(x,y)": "ObjectID"` ) is loaded from the `grid_details_json_filename`.
    * **Grid Data Preparation:**
        * The raw grid data  is parsed to determine the grid dimensions (`N`) by identifying the maximum x and y coordinates from the keys.
        * This data is then converted into a 2D list-of-lists representation (`grid_details_2d_array`), primarily for contextual reference or potential validation steps within individual solver functions.
    * **Iterative Prompt Solving:** For each prompt object in the loaded list:
        * The `prompt_id`, `generated_prompt_text`, and `template_id_source` are extracted.
        * **Solver Invocation (Template-Specific):**
            * [cite_start]Based on the `template_id_source` (e.g., "1" ), the corresponding solver function (e.g., `solve_template1_prompt`) is called. This solver function is designed to handle the specific structure and reasoning type of that template.
            * **Inside the Solver Function (e.g., `solve_template1_prompt`):**
                1.  **Prompt Parsing:** Regular expressions are employed to meticulously parse the `generated_prompt_text`. This extracts all explicitly stated entities and their attributes: Agent ID, Agent (X,Y) coordinates, Agent Orientation; [cite_start]Target Object ID, Target Object (X,Y) coordinates, and Target Object Orientation (as defined in the modified templates ).
                2.  **Coordinate Conversion:** Extracted coordinate strings are converted to integer values.
                3.  **Core Spatial Reasoning Logic:** The `determine_relative_direction` helper function is invoked. This function receives the *parsed* agent's position (x,y) and agent's orientation (as stated in the prompt), and the *parsed* target object's position (x,y). It calculates the displacement vector between the agent and the target. Based on this vector and the agent's orientation, it determines the primary relative direction (Left, Right, In front, or Behind) of the target object from the agent's perspective.
                4.  [cite_start]The orientations of non-agent objects (like `TARGET_OBJECT_ORIENTATION`), though parsed from the prompt, do not influence the calculation for these specific Tier 1 relative direction questions, which focus on the agent's egocentric perspective of object locations.
            * The string returned by the solver function is considered the `expected_answer`.
            * If a prompt's `template_id_source` does not match a currently implemented solver, its answer is marked accordingly (e.g., "Error: Unsupported template ID").
        * **Result Aggregation:** A dictionary containing the `prompt_id` and the determined `expected_answer` is created and added to a list of all solved answers.
    * **File Output:** The complete list of answer objects is written to the specified `output_answers_filename` in JSON format, overriding any pre-existing file. Each object in the output contains the `prompt_id` and its corresponding `expected_answer`.

---