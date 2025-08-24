import json
import os
import sys
import re
import pandas as pd
from typing import List, Dict, Any

# --- Helper function (Unchanged) ---
def parse_llm_response(raw_response: str) -> str:
    """Cleans the raw LLM response to extract just the spatial direction string."""
    if not isinstance(raw_response, str) or "Error:" in raw_response:
        return "error"
    response_lower = raw_response.lower().strip().replace('.', '').replace(',', '')
    answer = "###Answer:"
    answer = answer.lower()
    if answer in response_lower:
        answer_part = response_lower.split(answer)[1]
        parsed_answer = answer_part.strip().replace('.', '').replace(',', '')
        # Standardize format (e.g., 'in front left' -> 'in-front-left')
        parsed_answer = parsed_answer.replace(' ', '-')
        return parsed_answer if parsed_answer else "unparseable"
    if "incorrect prompt" in response_lower:
        return "incorrect prompt"
    #response_lower = response_lower.replace('in front', 'in-front').replace('behind', 'behind-')
    directions_found = re.findall(r'in-front-right|in-front-left|behind-right|behind-left|in-front|behind|left|right', response_lower)
    return directions_found[0] if directions_found else "unparseable"

def read_expected_answer_file(answers_filename):
    answers_filename = '/Users/divyanshu03/Desktop/University of Leeds/Modules/Msc_Project/spatial-reasoning-simulation/data_files/expected_answers/'+answers_filename
    try:
        with open(answers_filename, 'r') as f:
            ground_truth_list = json.load(f)
    except FileNotFoundError:
        print(f"FATAL Error: Ground truth file not found at '{answers_filename}'")
        return {}
    answers_map = {item['prompt_id']: item['expected_answer'].lower().replace(' ', '-') for item in ground_truth_list}
    return answers_map
# --- MODIFIED Main Analysis Function ---
def analyze_all_results(root_results_dir: str):
    """
    Traverses all subdirectories, finds each evaluation results file,
    analyzes it, and saves a summary in the SAME directory.
    """
    # 1. Load the single ground-truth answers file once
    # try:
    #     with open(answers_filename, 'r') as f:
    #         ground_truth_list = json.load(f)
    # except FileNotFoundError:
    #     print(f"FATAL Error: Ground truth file not found at '{answers_filename}'")
    #     return
    # answers_map = {item['prompt_id']: item['expected_answer'].lower().replace(' ', '-') for item in ground_truth_list}

    # 2. Walk through the results directory to find and process each result file
    found_results = False
    print(f"Scanning for results in directory: '{root_results_dir}'...")
    for subdir, dirs, files in os.walk(root_results_dir):
        if 'evaluation_results_2000_10.json' in files:
            found_results = True
            results_filepath = os.path.join(subdir, 'evaluation_results_2000_10.json')

            if "low" in results_filepath:
                answers_map = read_expected_answer_file("expected_answer_file_level_1_2000_10.json")
            elif "medium" in results_filepath:
                answers_map = read_expected_answer_file("expected_answer_file_level_2_2000_10.json")
            else:
                answers_map = read_expected_answer_file("expected_answer_file_level_3_2000_10.json")
            
            print(f"\n{'='*25}\nAnalyzing file: {results_filepath}\n{'='*25}")
            
            with open(results_filepath, 'r') as f:
                llm_results = json.load(f)

            if not llm_results:
                print("  This results file is empty. Skipping.")
                continue

            # Process this specific file
            analysis_data = []
            for result in llm_results:
                prompt_id = result.get('prompt_id')
                ground_truth = answers_map.get(prompt_id, 'not_found')
                parsed_answer = parse_llm_response(result.get('raw_response', ''))
                
                analysis_data.append({
                    'prompt_id': prompt_id,
                    'model': result.get('model'),
                    'expected_answer': ground_truth,
                    'predicted_answer': parsed_answer,
                    'is_correct': 1 if parsed_answer == ground_truth else 0,
                    'complexity_level': result.get('complexity_level'),
                    'time_taken': result.get('time_taken'),
                    'tokens_used':result.get('tokens_used'),
                    'temperature':result.get('temperature_setting'),
                    'seed':result.get('seed_setting'),
                    'grid_size': 10
                })

            # Create and print the report for this specific file
            df = pd.DataFrame(analysis_data)
            print(f"Overall Accuracy for this run: {df['is_correct'].mean():.2%}")
            print("Confusion Matrix for this run:")
            all_answers = sorted(list(set(df['expected_answer']) | set(df['predicted_answer'])))
            confusion_matrix = pd.crosstab(
                pd.Categorical(df['expected_answer'], categories=all_answers, ordered=True),
                pd.Categorical(df['predicted_answer'], categories=all_answers, ordered=True),
                rownames=['Actual Answer'], colnames=['Predicted Answer'], dropna=False
            )
            print(confusion_matrix)

            # NEW: Save the analysis summary CSV in the SAME directory
            analysis_output_filepath = os.path.join(subdir, 'analysis_summary_new.csv')
            try:
                df.to_csv(analysis_output_filepath, index=False)
                print(f"  --> Detailed analysis summary saved to '{analysis_output_filepath}'")
            except Exception as e:
                print(f"  Error saving analysis file: {e}")

    if not found_results:
        print("No 'evaluation_results.json' files were found in any subdirectories.")

if __name__ == '__main__':
    # This script now expects the root results directory as a command-line argument.
    analyze_all_results("results")
    