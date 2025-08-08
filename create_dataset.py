from grid_generation import generate_populated_grid
from question_generation import generate_questions
from question_answer_generation import solve_questions_from_file,filter_question_answer
from prompt_generation import create_api_ready_prompts

if __name__ == '__main__':
    # Example Usage:
    humans = ["Man", "Woman", "Child"]
    animals = ["Dog", "Cat", "Horse", "Cow"]
    vehicles = ["Car", "Bike", "Cycle", "Plane", "Ship", "Train"]
    orientations = ['North', 'South', 'East', 'West']

    generated_questions_filenames = ['generated_questions_level_1.json','generated_questions_level_2.json','generated_questions_level_3.json']
    questions_pool_filenames = ['questions_pool_level_1.json','questions_pool_level_2.json','questions_pool_level_3.json']

    prompts_filenames = ['prompts_level_1.json','prompts_level_2.json','prompts_level_3.json']

    expected_answer_filenames = ['expected_answer_file_level_1.json','expected_answer_file_level_2.json','expected_answer_file_level_3.json']
    answer_pool_filenames = ['answer_pool_level_1.json','answer_pool_level_2.json','answer_pool_level_3.json']

    templates_filenames = ['templates_level_1.json','templates_level_2.json','templates_level_3.json']

    actions_filename = "actions.json"
    questions_pool_count = 10000
    question_dataset_needed = 50
    
    grid_size = 10
    fill = 0.6 

    print(f"Generating a {grid_size}x{grid_size} grid with {fill*100}% fill ratio\n")
    populated_grid, grid_details_file_name = generate_populated_grid(grid_size, fill, humans, animals, vehicles)

    for i in range(0,3):
        generate_questions(grid_details_file_name, templates_filenames[i],actions_filename, orientations, questions_pool_filenames[i],questions_pool_count)
        solve_questions_from_file(questions_pool_filenames[i],answer_pool_filenames[i],populated_grid)
        filter_question_answer(questions_pool_filenames[i],answer_pool_filenames[i],question_dataset_needed,generated_questions_filenames[i],expected_answer_filenames[i])
    for row in populated_grid:
        # Adjusted formatting for potentially shorter strings
        print(" ".join(f"{cell: <8}" for cell in row)) 

    for i in range(0,3):
        create_api_ready_prompts(generated_questions_filenames[i], grid_details_file_name, prompts_filenames[i])
    #print(f"\nGenerating a 10x10 grid with 30% fill ratio\n")
    # populated_grid_3x3 = generate_populated_grid(10, 0.3, humans, animals, vehicles)
    # for row in populated_grid_3x3:
    #     print(" ".join(f"{cell: <8}" for cell in row))
