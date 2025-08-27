import json
import requests
import random
import os
import csv
from typing import Collection
import sys
import os
from program_evaluator import ProgramEvaluator
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import env_factory

initial = '["COLLECT_FUNC(WORKSHOP1)","COLLECT_FUNC(WORKSHOP1)", "COLLECT_FUNC(WORKSHOP1)"]'
# Configuration paths
recipes_path = "../resources/recipes_for_synth.yaml"
hints_path = "../resources/hints.yaml"
json_file = "task_config.json"

# Read tasks and time from JSON file
with open(json_file, "r") as f:
    config = json.load(f)
    tasks = config["tasks"]
    time_limits = config["time"]

# Read configuration file
with open("../cfg/cfg.txt", "r") as f:
    cfg = f.read()

prompt = """
You are a program synthesizer for the following domain specific language->
{cfg}

Give me the programs for the following tasks->
{tasks}

Previous version of programs is 
{initial}

Please return the next version as a list that I can parse through below return the actual progam list after and separate from the reasoning ->
"""

# Initialize evaluator
evaluator = ProgramEvaluator()


def get_updated_prompt(function_str):
    """Generate updated prompt with current function."""
    return prompt.format(cfg=cfg, tasks=tasks, initial=function_str)

class LLM:
    """Language model that predicts continuation of provided source code."""

    def __init__(self, samples_per_prompt: int) -> None:
        self._samples_per_prompt = samples_per_prompt

    def _draw_sample(self, prompt: str) -> str:
        """Returns a predicted continuation of `prompt`."""
        api_url = "http://129.128.243.184:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "deepseek-r1:70b", 
            "prompt": prompt, 
            "stream": False, 
            "template": "{{ .Prompt }}", 
            "options": {
                "num_ctx": 3000, 
            }
        }
        res = requests.post(api_url, headers=headers, json=payload, timeout=300)
        res = res.json()
        return res["response"]

    def draw_samples(self, prompt: str) -> Collection[str]:
        """Returns multiple predicted continuations of `prompt`."""
        return [self._draw_sample(prompt) for _ in range(self._samples_per_prompt)]

def pick_top_k_from_sampled_island(islands: list[list], scores: list[list[float]], k: int):
    # Step 1: Pick a random island index
    idx = random.randrange(len(islands))

    sampled_island = islands[idx]       # List of candidates
    sampled_scores = scores[idx]        # Corresponding scores

    # Step 2: Zip candidates with their scores
    paired = list(zip(sampled_island, sampled_scores))  # List of (candidate, score)

    # Step 3: Sort by score descending
    paired.sort(key=lambda x: x[1], reverse=True)

    # Step 4: Extract top-k candidates
    top_k_candidates = [cand for cand, _ in paired[:k]]

    return idx, top_k_candidates

def log_to_csv(island_id, iteration_num, best_funct, best_score, csv_filename='evolution_log.csv'):
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['island_id', 'iteration_num', 'function', 'score'])
        writer.writerow([island_id, iteration_num, repr(best_funct), best_score])

def sampler():
    llm = LLM(2)
    islands = [[initial] for _ in range(4)]
    scores = [[0.0] for _ in range(4)]
    
    # Set up multiprocessing
    max_workers = min(mp.cpu_count(), 8)  # Limit to 8 processes or CPU count
    
    for i in range(100):
        island_id, version = pick_top_k_from_sampled_island(islands, scores, 1)
        prompt = get_updated_prompt(version[0])
        list_of_functions = llm.draw_samples(prompt)
        print(f"Iteration {i}: Generated {len(list_of_functions)} functions")
        
        # Parallel evaluation of all functions
        best_funct, best_score = parallel_evaluate_functions(list_of_functions, max_workers)
        
        islands[island_id].append(best_funct)
        scores[island_id].append(best_score)
        log_to_csv(island_id, i, best_funct, best_score)
        print(f"Iteration {i}: Best score = {best_score}")

def parallel_evaluate_functions(functions, max_workers):
    """Evaluate multiple functions in parallel and return the best one."""
    if not functions:
        return "", 0.0
    
    # Prepare evaluation tasks
    eval_tasks = [(func, i) for i, func in enumerate(functions)]
    
    results = []
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all evaluation tasks
        future_to_func = {
            executor.submit(eval_func_worker, func): (func, idx) 
            for func, idx in eval_tasks
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_func):
            func, idx = future_to_func[future]
            try:
                reward, success_count = future.result()
                results.append((func, reward, success_count, idx))
                print(f"Function {idx}: reward={reward}, success_count={success_count}")
            except Exception as e:
                print(f"Function {idx} evaluation failed: {e}")
                results.append((func, 0.0, 0, idx))
    
    end_time = time.time()
    print(f"Parallel evaluation completed in {end_time - start_time:.2f} seconds")
    
    # Find the best function based on reward
    best_result = max(results, key=lambda x: x[1])  # Sort by reward
    return best_result[0], best_result[1]

def eval_func_worker(func):
    """Worker function for parallel evaluation."""
    try:
        return eval_func(func)
    except Exception as e:
        print(f"Error evaluating function: {e}")
        return 0.0, 0

def evaluate_program_with_evaluator(evaluator, program_str: str, env, time) -> tuple:
    """
    Evaluate a program using your ProgramEvaluator.
    """
    try:
        result = evaluator.evaluate_program(program_str, env, time)
        return result["success"], result['total_reward'], result['evaluation_time']
    except Exception as e:
        return False, float('-inf'), 0.0

def eval_func(program_str):
    """Evaluate a function string across multiple environments."""
    try:
        env_sampler = env_factory.EnvironmentFactory(
                recipes_path, hints_path, 6, max_steps=100, 
                reuse_environments=False, visualise=False)
        envs = []
        for task in tasks:
            envs.append(env_sampler.sample_environment(task_name=task))

        reward = 0
        success_count = 0
        for ind in range(len(envs)):
            s_, r, eval_time = evaluate_program_with_evaluator(
                        evaluator, program_str, envs[ind], time_limits[ind]
                     )
            if s_:
                success_count += 1
            if r > 0:
                reward += r
                print(f"Reward found for {tasks[ind]}: {r}")
                with open("solutions_from_prog_synth.txt", "a") as f:
                    f.write(
                                f"{tasks[ind]}: {program_str}, solution: {s_}, reward: {r}, evaluation_time: {eval_time:.4f}s\n"
                    )

        return reward, success_count
    except Exception as e:
        print(f"Error in eval_func: {e}")
        return 0.0, 0

if __name__ == "__main__":
    # Set multiprocessing start method for compatibility
    mp.set_start_method('spawn', force=True)
    sampler()