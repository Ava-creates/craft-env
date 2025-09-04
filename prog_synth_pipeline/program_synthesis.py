from typing import List
from collections import deque
from cfg_parser import CFGParser
import itertools
from program_evaluator import ProgramEvaluator 
import heapq
import concurrent.futures
import time
from multiprocessing import Pool, cpu_count
import env_factory
import json
import sys
from google import genai
import requests
from funsearch.implementation.funsearch import FunSearch
from funsearch.implementation import config as config_lib
        
final =[]
evaluator = ProgramEvaluator()
recipes_path = "resources/recipes_for_synth.yaml"
hints_path = "resources/hints.yaml"
env_sampler = env_factory.EnvironmentFactory(
            recipes_path, hints_path, 6, max_steps=100, 
            reuse_environments=False, visualise=False)
    # Read tasks and time from JSON 

with open("prog_synth_pipeline/task_config.json", "r") as f:
        config = json.load(f)
        tasks = config["tasks"]
        time_limits = config["time"]
def is_terminal(symbol: str, cfg: CFGParser) -> bool:
    return symbol not in cfg.non_terminals

def evaluate_program_with_evaluator(evaluator, program_str: str, env, time) -> int:
    """
    Evaluate a program using your ProgramEvaluator.
    """

    # try:
    result = evaluator.evaluate_program(program_str, env, time)
    if(result['success']):
            final.append(program_str)
            with open("final2.txt", "a") as f:
                for program in final:
                    f.write(program + "\n")
    return result["actions"], result["success"], result['total_reward'], result['evaluation_time'] , result["func"]
    # except Exception as e:
    #     print(E)
    #     return False, float('-inf'), 0.0


def format_program(tokens: List[str]) -> str:
    result = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "MOVE_FUNC":
            result.append(f"MOVE_FUNC({tokens[i+2]})")
            i += 4
        elif tokens[i] == "CRAFT_FUNC":
            result.append(f"CRAFT_FUNC({tokens[i+2]})")
            i += 4
        elif tokens[i] == "COLLECT_FUNC":
            result.append(f"COLLECT_FUNC({tokens[i+2]})")
            i += 4
        elif tokens[i] == "if":
            # Skip LPAR and RPAR, use the actual item
            item = tokens[i+2]
            if item == "LPAR":
                item = tokens[i+3]
            if tokens[i+4] == "RPAR":
                i += 1  # Skip RPAR
            result.append(f"if has({item})")
            i += 4
        elif tokens[i] == "then":
            result.append("then")
            i += 1
        elif tokens[i] == "SEMI":
            result.append(";")
            i += 1
        else:
            result.append(tokens[i])
            i += 1
    return " ".join(result)

def tokenize_rhs(rhs: str) -> List[List[str]]:
    alternatives = [alt.strip().split() for alt in rhs.split('|')]
    return alternatives

def evaluate(program_str):
    envs = []
    # for task in tasks:
    envs.append(env_sampler.sample_environment(task_name='make[arrow]'))
    results = set()
    # for ind in range(len(envs)):
    a, s, r, eval_time, funcs = evaluate_program_with_evaluator(evaluator, program_str, envs[0], 60)
    results.add(1 if s else 0)
   
    
    return a, program_str, results, s, r, eval_time, "make[arrow]",funcs

def eval_pll(programs, num_workers=None):
    if num_workers is None:
        num_workers = cpu_count()  # use all available cores
        print(num_workers)

    results = {}
    with Pool(processes=num_workers) as pool:
        for prog, res, s, r, eval_time, task_name, func in pool.map(evaluate, programs):
            results[prog] = res
            print(func)
            with open("solutions.txt", "a") as f:              
                    f.write(f"{task_name}: {prog}, solution: {s}, reward: {r}, evaluation_time: {eval_time:.4f}s\n")
    return results

def synthesis_llm():
    with open("cfg/cfg.txt") as f:
        cfg = f.read()
    with open("resources/recipes_for_synth.yaml") as f:
        recipes = f.read()
    prompt = f"""
    You are a Domain Specific Language (DSL) program generator for the Craft domain. 

    ## Context Free Grammar (CFG)
    Here is the context-free grammar (CFG) that defines the DSL. Strictly follow this CFG when synthesising programs :

    {cfg}

    ## Example Programs
    Here are examples of programs written in this DSL:

    COLLECT_FUNC(WOOD) ; MOVE_FUNC(RIGHT) ; CRAFT_FUNC(STICK)
    COLLECT_FUNC(GRASS) ; MOVE_FUNC(RIGHT)

    ## Domain Context
    This DSL is used to solve tasks in the Craft domain. Tasks typically look like:
    - get(wood)
    - make(stick)

    The goal is to write programs in the context free grammar (CFG) provided that can complete these tasks using the available functions and recipes.

    ## Available Recipes
    Here are the recipes for the domain:

    {recipes}

    ## Task
    Generate a program that solves the following task :

    **make(goldarrow)**

    ## Output Format Instructions
    Return ONLY the program string delimited by $ signs. Do not include any explanations, comments, or additional text outside the $ delimiters.

    Example output format:
    $CRAFT_FUNC(ARROW) ; COLLECT_FUNC(WOOD) ; MOVE_FUNC(RIGHT)$
    """
    # client = genai.Client()
    first_failing_funcs = []
    programs = []
    for i in range(1):
        # response = client.models.generate_content(
        #                 model="gemini-2.5-pro", contents = prompt
        #             )
        # b = response.text.strip('$')
        b= "COLLECT_FUNC(WOOD) ; COLLECT_FUNC(IRON) ; COLLECT_FUNC(ROCK) ; CRAFT_FUNC(KNIFE) ; CRAFT_FUNC(ARROW)"
        programs.append(b)
        a, program_str, results, s, r, eval_time, task, funcs = evaluate(b)
        print("fuuncs", funcs)
        if funcs:
            actions_up_to_failure = []
            for i, (func_name, reward, func_actions) in enumerate(funcs):
                if reward <= 0:
                    # Collect actions from all functions up to this failing one
                    for j in range(i):
                        actions_up_to_failure.append(funcs[j][2])  
                    first_failing_funcs.append((func_name, reward, actions_up_to_failure, task))
                    break  
        # print(first_failing_funcs)
    # Run FunSearch for each failing function
    if first_failing_funcs:
        # print("\nRunning FunSearch for failing functions...")
        actions =[]
        for func_name, reward, actions_up_to_failure, task in first_failing_funcs:
            base_func_name = func_name.replace("_FUNC", "").lower()+"_base"
            # print(base_func_name)
            action_string = ""
            if actions_up_to_failure:
                print(actions_up_to_failure)
                for actions in actions_up_to_failure:
                    for a in actions:
                        action_string+="env.step("+str(a)+")"+"\n  "
            # print(action_string)
            try:
                with open("craft_base.txt", "r") as f:
                    content = f.read()

                # print(content )
                
                # Replace placeholders with actual values
                content = content.replace("{env}", "env=env_sampler.sample_environment(task_name='make[arrow]')")
                content = content.replace("{actions}", action_string)
        
                with open("craft_base.txt", "w") as f:
                    f.write(content)
                
                
            except Exception as e:
                print(f"Failed to update craft_base.txt: {e}")
            
            with open("prompt_specifications/specification_jocelyn.txt", 'r') as f:
                 specification = f.read()
            funsearch = FunSearch(model_type='ollama')
            config = config_lib.Config()
            
            try:
                funsearch.run(specification, [""], config, base_func_name, "craft_func.py")
                print(f"FunSearch completed for {func_name}")
            except Exception as e:
                print(f"FunSearch failed for {func_name}: {e}")
    return programs


if __name__ == "__main__":
    
    # Check if JSON file path is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python program_synthesis.py <json_file_path>")
        print("Example: python program_synthesis.py task_config.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    cfg_parser = CFGParser("cfg/cfg.txt")
    start_symbol = "s"
    print(f"Start symbol: {start_symbol}")
    print(f"Using JSON config file: {json_file}")
    print("\nGenerating programs (worklist)...")
    synthesis_llm()