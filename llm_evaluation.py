import json
import os
import time,requests
import google.generativeai as genai
import ollama
REPRODUCIBILITY_CONFIG = {
                    "temperature": 0.0,
                    "seed": 42
                }
request_options = {
    "timeout": 60,
}
prompt_count = 0
key = 0
# --- NEW: API Calling Helper Function ---
def get_llm_response(model_name: str, messages: list):
    """
    Calls the appropriate LLM API based on the model name.
    
    Args:
        model_name (str): The name of the model to query (e.g., 'gemini-2.5-flash', 'llama3:8b-instruct').
        messages (list): The list of messages (system and user prompts) for the API call.

    Returns:
        str: The text content of the model's response.
    """
    print(f"  Querying {model_name}...")
    tokens_used = 0
    try:
        if 'gemini' in model_name:
            # # Assumes gemma models from Google are being called via the Gemini API
            # # The system prompt is passed during model initialization
            # GOOGLE_API_KEY = "AIzaSyD7GRx6uKwPxOfGivYrin8IZrrKDikH91U" #"AIzaSyBYh9j9jlp8KMQFDkT_-JY2XF7Okd342FA"
            # if not GOOGLE_API_KEY:
            #     # Reverted the hardcoded key to use the secure environment variable method
            #     raise ValueError("Error: GOOGLE_API_KEY environment variable not set.")
            # genai.configure(api_key=GOOGLE_API_KEY)
            
            system_prompt = ""
            user_prompt = ""
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    user_prompt = msg['content']
            
            model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
            # Pass the generation_config to the API call
            gemini_config = {"temperature": REPRODUCIBILITY_CONFIG["temperature"]}
            
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(**gemini_config),
                request_options=request_options
            )
            #response = model.generate_content(user_prompt)
            tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else 0
            return {"text": response.text, "tokens_used": tokens_used}
        
        elif model_name == 'o4-mini':
            # Extract details from your curl command
            url = 'https://scfli-m3m0wtql-swedencentral.cognitiveservices.azure.com/openai/deployments/o4-mini-2025-04-16/chat/completions?api-version=2025-01-01-preview'
            # IMPORTANT: For security, the bearer token should be an environment variable
            bearer_token = os.environ.get("AZURE_OAI_KEY", "8uQyLpwQ9") # Fallback to the one you provided

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer 8uQyLpwQ92pyvIL0MbvXCZaNK6WMh0abHXjbM3kMSmzlJkg8O7ptJQQJ99AKACfhMk5XJ3w3AAAAACOGNFmh"
            }
            
            data = {
                "messages": messages,
                "stream": False,
                #"temperature": REPRODUCIBILITY_CONFIG["temperature"],
                "seed": REPRODUCIBILITY_CONFIG["seed"]
            }
            #print(data)
            response = requests.post(url, headers=headers, json=data,timeout=60)
            #print(response.json())
            response.raise_for_status() # Will raise an exception for HTTP error codes
            
            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content']
            if 'usage' in response_json:
                tokens_used = response_json['usage']['total_tokens']
        
        elif model_name == 'gpt-4.1-mini':
            # Extract details from your curl command
            url = 'https://scfli-m3m0wtql-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4.1-mini-2025-04-14/chat/completions?api-version=2025-01-01-preview'
            # IMPORTANT: For security, the bearer token should be an environment variable
            bearer_token = os.environ.get("AZURE_OAI_KEY", "8uQyLpwQ9") # Fallback to the one you provided

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer 8uQyLpwQ92pyvIL0MbvXCZaNK6WMh0abHXjbM3kMSmzlJkg8O7ptJQQJ99AKACfhMk5XJ3w3AAAAACOGNFmh"
            }
            
            data = {
                "messages": messages,
                "stream": False,
                #"temperature": REPRODUCIBILITY_CONFIG["temperature"],
                "seed": REPRODUCIBILITY_CONFIG["seed"]
            }
            #print(data)
            response = requests.post(url, headers=headers, json=data,timeout=60)
            #print(response.json())
            response.raise_for_status() # Will raise an exception for HTTP error codes
            
            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content']
            if 'usage' in response_json:
                tokens_used = response_json['usage']['total_tokens']
        
        elif model_name == 'phi-4-reasoning-1': # very slow in giving response...removing it
            # Extract details from your curl command
            url = 'https://scfli-m3m0wtql-swedencentral.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview'
            # IMPORTANT: For security, the bearer token should be an environment variable
            bearer_token = os.environ.get("AZURE_OAI_KEY", "8uQyLpwQ9") # Fallback to the one you provided

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer 8uQyLpwQ92pyvIL0MbvXCZaNK6WMh0abHXjbM3kMSmzlJkg8O7ptJQQJ99AKACfhMk5XJ3w3AAAAACOGNFmh"
            }
            
            data = {
                "messages": messages,
                "stream": False,
                "model" : "Phi-4-reasoning-1",
                #"temperature": REPRODUCIBILITY_CONFIG["temperature"],
                "seed": REPRODUCIBILITY_CONFIG["seed"]
            }
            #print(data)
            response = requests.post(url, headers=headers, json=data,timeout=60)
            #print(response.json())
            response.raise_for_status() # Will raise an exception for HTTP error codes
            
            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content']
            if 'usage' in response_json:
                tokens_used = response_json['usage']['total_tokens']
        
        elif model_name == 'deepSeek-v3':
            # Extract details from your curl command
            url = 'https://scfli-m3m0wtql-swedencentral.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview'
            # IMPORTANT: For security, the bearer token should be an environment variable
            bearer_token = os.environ.get("AZURE_OAI_KEY", "8uQyLpwQ9") # Fallback to the one you provided

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer 8uQyLpwQ92pyvIL0MbvXCZaNK6WMh0abHXjbM3kMSmzlJkg8O7ptJQQJ99AKACfhMk5XJ3w3AAAAACOGNFmh"
            }
            
            data = {
                "messages": messages,
                "stream": False,
                "model": "DeepSeek-V3-0324",
                #"temperature": REPRODUCIBILITY_CONFIG["temperature"],
                "seed": REPRODUCIBILITY_CONFIG["seed"]
            }
            #print(data)
            response = requests.post(url, headers=headers, json=data,timeout=60)
            #print(response.json())
            response.raise_for_status() # Will raise an exception for HTTP error codes
            
            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content']
            if 'usage' in response_json:
                tokens_used = response_json['usage']['total_tokens']
        
        elif model_name == 'gpt-4.1':
            # Extract details from your curl command
            url = 'https://scfli-m3m0wtql-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4.1-2025-04-14/chat/completions?api-version=2025-01-01-preview'
            # IMPORTANT: For security, the bearer token should be an environment variable
            bearer_token = os.environ.get("AZURE_OAI_KEY", "8uQyLpwQ9") # Fallback to the one you provided

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer 8uQyLpwQ92pyvIL0MbvXCZaNK6WMh0abHXjbM3kMSmzlJkg8O7ptJQQJ99AKACfhMk5XJ3w3AAAAACOGNFmh"
            }
            
            data = {
                "messages": messages,
                "stream": False,
                "model": "DeepSeek-V3-0324",
                #"temperature": REPRODUCIBILITY_CONFIG["temperature"],
                "seed": REPRODUCIBILITY_CONFIG["seed"]
            }
            #print(data)
            response = requests.post(url, headers=headers, json=data,timeout=60)
            #print(response.json())
            response.raise_for_status() # Will raise an exception for HTTP error codes
            
            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content']
            if 'usage' in response_json:
                tokens_used = response_json['usage']['total_tokens']
        elif any(name in model_name for name in ['llama3', 'phi3','gemma']): # For local Ollama models
            # Ollama takes the full message list directly
            client = ollama.Client(timeout=60)
            response = client.chat(model=model_name, messages=messages)
            response_text = response['message']['content']
            prompt_tokens = response.get('prompt_eval_count', 0)
            completion_tokens = response.get('eval_count', 0)
            tokens_used = prompt_tokens + completion_tokens

            #return response['message']['content']

        # elif 'gpt' in model_name: # For OpenAI models
        #     # OpenAI client will use the OPENAI_API_KEY environment variable
        #     client = openai.OpenAI()
        #     response = client.chat.completions.create(
        #         model=model_name,
        #         messages=messages
        #     )
        #     return response.choices[0].message.content
            
        else:
            response_text =  f"Error: No API logic defined for model '{model_name}'."
            
    except Exception as e:
        print(f"    An error occurred while querying {model_name}: {e}")
        response_text = f"Error: {e}"
    return {"text": response_text, "tokens_used": tokens_used}
# --- Main Execution Function ---
def run_llm_evaluation(MODEL_TO_TEST,API_PROMPTS_FILE):
    """
    Loads API-ready prompts, calls the specified LLM API for each,
    and saves the raw responses into an organized folder structure.
    """
    # 1. Load the list of API-ready prompts to determine the output path
    try:
        with open(API_PROMPTS_FILE, 'r') as f:
            all_prompts = json.load(f)
    except FileNotFoundError:
        print(f"FATAL Error: The prompt file '{API_PROMPTS_FILE}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"FATAL Error: The file '{API_PROMPTS_FILE}' is not a valid JSON file.")
        return
        
    if not all_prompts:
        print("FATAL Error: The prompt file is empty. Nothing to process.")
        return

    # --- NEW: Logic to create organized output directory ---
    # Get complexity level from the first prompt in the file (assuming all are the same level)
    if "level_1" in API_PROMPTS_FILE:
        complexity_level = "low"
    elif "level_2" in API_PROMPTS_FILE:
        complexity_level = "medium"
    else:
        complexity_level = "high"
    
    # Define the output directory path
    output_dir = os.path.join('results', MODEL_TO_TEST, complexity_level)
    
    # Create the directory if it doesn't already exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Results will be saved in: {output_dir}")
    
    # Define the final path for the results file
    results_filepath = os.path.join(output_dir, 'evaluation_results.json')
    # --- END of new logic ---

    # 2. Configure the API Client
    # try:
        
    #     if 'gemini-2.5-flash' in MODEL_TO_TEST or 'gemma-3-27b-it' in MODEL_TO_TEST:
    #         # Load your API key from an environment variable for security
    #         GOOGLE_API_KEY = "AIzaSyBYh9j9jlp8KMQFDkT_-JY2XF7Okd342FA"
    #         if not GOOGLE_API_KEY:
    #             # Reverted the hardcoded key to use the secure environment variable method
    #             raise ValueError("Error: GOOGLE_API_KEY environment variable not set.")
    #         genai.configure(api_key=GOOGLE_API_KEY)
    # except Exception as e:
    #     print(f"Fatal Error: Could not configure Google API. {e}")
    #     return

    # 3. Loop through prompts and call the API
    all_results = []
    # BUG FIX: Calculate total_prompts after loading the file
    total_prompts = len(all_prompts) 
    
    print(f"Starting evaluation for {total_prompts} prompts with model: {MODEL_TO_TEST}")
    
    for i, prompt_object in enumerate(all_prompts):
        global prompt_count
        prompt_count = prompt_count + 1
        prompt_id = prompt_object.get("id")
        messages = prompt_object.get("messages")

        if not all([prompt_id, messages]):
            print(f"Warning: Skipping malformed prompt object at index {i}.")
            continue
            
        print(f"---[complexity_level: {complexity_level}] Processing Prompt ID: {prompt_id} ({i+1}/{total_prompts}) ---")
        if (i+1)%10==0:
            time.sleep(62)
        
        if prompt_count%240 == 0:
            global key
            key = key + 1
        system_prompt = ""
        user_prompt = ""
        # for message in messages:
        #     if message.get("role") == "system":
        #         system_prompt = message.get("content", "")
        #     elif message.get("role") == "user":
        #         user_prompt = message.get("content", "")
        
        # if not user_prompt or not system_prompt:
        #     print("  Warning: Prompt missing system or user content. Skipping.")
        #     continue

        #raw_response = f"Error: API call failed for {MODEL_TO_TEST}"
        time_taken = 0
        try:
            #model = genai.GenerativeModel(MODEL_TO_TEST, system_instruction=system_prompt)
            if 'gemini' in MODEL_TO_TEST:
            # Assumes gemma models from Google are being called via the Gemini API
            # The system prompt is passed during model initialization
                GOOGLE_API_KEY = ["AIzaSyC6V1zbzMS7O21xmElkKnzpDLvdlV176xM","AIzaSyBZbJLSiiPUMyN5hTui1tk_SetmJ-Zu53Q","AIzaSyBYqGw5eBSYWLDQRcVsTj36Vek_F9sJVC8","AIzaSyDzRiC3ovwjML0p5yDvATyUufyl4SZ823g","AIzaSyAC7_yEk9M1CfgTTxj9XWlxxOn03EYKiow","AIzaSyDfX1U49o2aIJegNd_RfaLIxUEEXGq5h0Q","AIzaSyCgSELw9g6NFJ9MN_bFNFAWC_wxfQbbBv8","AIzaSyDNjg0H-BkZ69U20ECZ2u04slxUxTWTgeU",
                "AIzaSyDKyDWPkOuk8mLhP2RxdFwG2ywyXTVjRxQ"]
                if not GOOGLE_API_KEY:
                # Reverted the hardcoded key to use the secure environment variable method
                    raise ValueError("Error: GOOGLE_API_KEY environment variable not set.")
                print("prompt no: ",prompt_count," ", GOOGLE_API_KEY[key])
                genai.configure(api_key=GOOGLE_API_KEY[key])
    
            start_time = time.monotonic()
            #response = model.generate_content(user_prompt)
            raw_response = get_llm_response(MODEL_TO_TEST, messages)
            end_time = time.monotonic()
            time_taken = end_time - start_time
            print(f"  Successfully received response from API: {MODEL_TO_TEST} in {time_taken:.2f} seconds")

            all_results.append({
                "prompt_id": prompt_id,
                "model": MODEL_TO_TEST,
                "raw_response": raw_response["text"].strip(),
                "tokens_used": raw_response["tokens_used"],
                "temperature_setting": REPRODUCIBILITY_CONFIG["temperature"],
                "seed_setting": REPRODUCIBILITY_CONFIG["seed"],
                "complexity_level": complexity_level,
                "time_taken": f'{time_taken:.2f}'
            })
        except Exception as e:
            print(f"    An error occurred while querying {MODEL_TO_TEST}: {e}")
            #raw_response = f"Error: {e}"
        
        
        #time.sleep(2)

    # 4. Save all collected results to the new, dynamic file path
    try:
        with open(results_filepath, 'w') as f:
            json.dump(all_results, f, indent=4)
        print(f"\nEvaluation complete. Raw results for {len(all_results)} queries saved to '{results_filepath}'.")
    except IOError as e:
        print(f"Error saving results to file: {e}")

# --- Run the Script ---
if __name__ == '__main__':
    # Input file containing the API-ready prompts
    API_PROMPTS_FILE = ['prompts_level_1_2000_10.json','prompts_level_2_2000_10.json','prompts_level_3_2000_10.json'] #

    # The model we are testing in this run
    MODEL_TO_TEST = ['gemini-2.5-flash','gpt-4.1-mini','o4-mini','deepSeek-v3','gpt-4.1']#['gemini-2.5-flash']#['o4-mini','gpt-4.1','gpt-4.1-mini','deepSeek-v3']#['gemini-2.5-flash-lite-preview-06-17']##['deepSeek-v3','phi-4-reasoning-1']#['gpt-4.1-mini','o4-mini']#['o4-mini']#['gemini-2.5-flash']#['phi4-reasoning:14b']#['gemini-2.5-flash','gemma3:4b'] 
    for llm_model in MODEL_TO_TEST:
        for prompt_file in API_PROMPTS_FILE:
            run_llm_evaluation(llm_model,prompt_file)