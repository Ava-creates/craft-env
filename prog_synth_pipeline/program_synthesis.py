from typing import List
from collections import deque
from cfg_parser import CFGParser
import itertools
from program_evaluator import ProgramEvaluator 
import heapq
import concurrent.futures
import time
import multiprocessing
import env_factory
import json
import sys

final =[]

def is_terminal(symbol: str, cfg: CFGParser) -> bool:
    return symbol not in cfg.non_terminals

def evaluate_program_with_evaluator(evaluator, program_str: str, env, time) -> int:
    """
    Evaluate a program using your ProgramEvaluator.
    """

    try:
        result = evaluator.evaluate_program(program_str, env, time)
        if(result['success']):
            final.append(program_str)
            with open("final2.txt", "a") as f:
                for program in final:
                    f.write(program + "\n")
        return result["success"] , result['total_reward'], result['evaluation_time']
    except Exception as e:
        return False, float('-inf'), 0.0


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

def synthesize_priority(cfg: CFGParser, start_symbol: str, max_depth: int, json_file :str):
    """
    Priority-queue-based program synthesis up to a given depth.
    Evaluates only fully terminal (complete) programs.
    """
    # counter = itertools.count()
    queue: List[Tuple[int, int, List[str]]] = []  # (depth, count, derivation)

    heapq.heappush(queue, (0, [start_symbol]))

    evaluator = ProgramEvaluator()
    final_programs = []
    recipes_path = "resources/recipes_for_synth.yaml"
    hints_path = "resources/hints.yaml"
    env_sampler = env_factory.EnvironmentFactory(
            recipes_path, hints_path, 6, max_steps=100, 
            reuse_environments=False, visualise=False)
    # Read tasks and time from JSON file
    with open(json_file, "r") as f:
        config = json.load(f)
        tasks = config["tasks"]
        time_limits = config["time"]
    envs = []
    for task in tasks:
        envs.append(env_sampler.sample_environment(task_name=task))

    current_depth = 0
    depth_start_time = time.time()

    while queue:
        depth, current = heapq.heappop(queue)

        # When we hit a new depth, log how long the last one took
        if depth != current_depth:
            elapsed = time.time() - depth_start_time
            print(f"Finished enumerating depth {current_depth} in {elapsed:.4f}s")
            current_depth = depth
            depth_start_time = time.time()

        # Terminal check
        if all(is_terminal(sym, cfg) for sym in current):
            results = set()
            program_str = format_program(current)
            for ind in range(len(envs)):
                s, r, eval_time = evaluate_program_with_evaluator(
                    evaluator, program_str, envs[ind], time_limits[ind]
                )
                results.add(1 if s else 0)
                if s:
                    print("sol found for", tasks[ind])
                    with open("solutions_from_prog_synth.txt", "a") as f:
                        f.write(
                            f"{tasks[ind]}: {program_str}, reward: {r}, evaluation_time: {eval_time:.4f}s\n"
                        )

            if results == {1}:
                return
            final_programs.append(program_str)
            continue

        if depth >= max_depth:
            continue

        # Expand one nonterminal
        for idx, sym in enumerate(current):
            if not is_terminal(sym, cfg):
                for production in cfg.rules[sym]:
                    for alt in tokenize_rhs(production):
                        new_derivation = current[:idx] + alt + current[idx+1:]
                        heapq.heappush(queue, (depth + 1, new_derivation))
                break

    # After the loop, log the last depth's time
    elapsed = time.time() - depth_start_time
    print(f"Finished enumerating depth {current_depth} in {elapsed:.4f}s")
 # Only expand the first non-terminal

    with open("final_all.txt", "a") as f:
        for program in final:
            f.write(program + "\n")

    return final_programs

if __name__ == "__main__":
    
    # Check if JSON file path is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python program_synthesis.py <json_file_path>")
        print("Example: python program_synthesis.py task_config.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    cfg_parser = CFGParser("cfg/cfg.txt")
    start_symbol = "s"
    # recipes_path = "resources/recipes.yaml"
    # hints_path = "resources/hints.yaml"
    # env_sampler = env_factory.EnvironmentFactory(
    #         recipes_path, hints_path, max_steps=100, 
    #         reuse_environments=False, visualise=False)
    # tasks =[ "make[shears]",  "make[ladder]", "make[arrow]"]
    # time =[20, 20 , 20]
    # envs =[]
    # for task in tasks:
    #     envs.append(env_sampler.sample_environment(task_name=task))
    print(f"Start symbol: {start_symbol}")
    print(f"Using JSON config file: {json_file}")
    print("\nGenerating programs (worklist)...")
    
    synthesize_priority(cfg_parser, start_symbol, max_depth=20, json_file=json_file)
