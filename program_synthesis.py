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
final =[]

def is_terminal(symbol: str, cfg: CFGParser) -> bool:
    return symbol not in cfg.non_terminals

def evaluate_program_with_evaluator(evaluator, program_str: str, env) -> int:
    """
    Evaluate a program using your ProgramEvaluator.
    """
    try:
        # evaluator = ProgramEvaluator()
        result = evaluator.evaluate_program(program_str, env)
        # print("result", result)

        if(result['success'] and all(is_terminal(sym, cfg) for sym in program_str)):
            final.append(program_str)
        print("result", result)
        return result['total_reward']
    except Exception as e:
        print("Error evaluating:", program_str, e)
        return float('-inf')


def format_program(tokens: List[str]) -> str:
    # (Same formatting logic as before)
    result = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "MOVE_FUNC":
            result.append(f"MOVE_FUNC({tokens[i+2]})")
            i += 4
        elif tokens[i] == "CRAFT_FUNC":
            result.append(f"CRAFT_FUNC({tokens[i+2]})")
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

def synthesize_priority(cfg: CFGParser, start_symbol: str, max_depth: int, env):
    """
    Priority-queue-based program synthesis up to a given depth.
    Evaluates only fully terminal (complete) programs.
    """
    counter = itertools.count()
    queue: List[Tuple[int, int, List[str]]] = []  # (depth, count, derivation)

    heapq.heappush(queue, (0, next(counter), [start_symbol]))

    evaluator = ProgramEvaluator()
    final_programs = []

    while queue:
        depth, _, current = heapq.heappop(queue)

        if all(is_terminal(sym, cfg) for sym in current):
            program_str = format_program(current)
            print("program_str", program_str)
            result = evaluate_program_with_evaluator(evaluator, program_str, env )  # Optional timeout

            final_programs.append(program_str)
            continue

        if depth >= max_depth:
            continue
        if(len(final) > 0):
            break
        for idx, sym in enumerate(current):
            if not is_terminal(sym, cfg):
                for production in cfg.rules[sym]:
                    for alt in tokenize_rhs(production):
                        new_derivation = current[:idx] + alt + current[idx+1:]
                        heapq.heappush(queue, (depth + 1, next(counter), new_derivation))
                break  # Only expand the first non-terminal

    with open("final.txt", "w") as f:
        for program in final:
            f.write(program + "\n")

    # Optionally write final programs to file


    return final_programs

if __name__ == "__main__":
    cfg_parser = CFGParser("cfg.txt")
    start_symbol = "s"
    recipes_path = "resources/recipes.yaml"
    hints_path = "resources/hints.yaml"
    env_sampler = env_factory.EnvironmentFactory(
            recipes_path, hints_path, max_steps=100, 
            reuse_environments=False, visualise=False)
    tasks =["make[arrow]", "make[flag]", "make[bench]", "get[gold]"]
    envs =[]
    for task in tasks:
        envs.append(env_sampler.sample_environment(task_name=task))
    print(f"Start symbol: {start_symbol}")
    print("\nGenerating programs (worklist)...")
    for env in envs:
        for i, program in enumerate(synthesize_priority(cfg_parser, start_symbol, max_depth=15, env=env), 1):
            print(f"\n=== Program {i} ===")
            print(program)
