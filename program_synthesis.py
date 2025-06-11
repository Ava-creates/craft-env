from typing import List
from collections import deque
from cfg_parser import CFGParser
import itertools
from program_evaluator import ProgramEvaluator 
import heapq
import concurrent.futures
import time
import multiprocessing
final =[]
def run_evaluation(queue, evaluator, program_str):
    try:
        result = evaluator.evaluate_program(program_str)
        print("result", result)
        queue.put(result)
    except Exception as e:
        queue.put(e)

def run_with_timeout(evaluator, program_str, timeout=360):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_evaluation, args=(queue, evaluator, program_str))
    p.start()
    print("program", program_str)
    p.join(timeout)
    if p.is_alive():
        print("Evaluation timed out.", program_str)
        p.terminate()   # Force kill
        p.join()        # Wait for process cleanup (fast now)
        return 0.0
    exitcode = p.exitcode
    print(f"Child exit code: {exitcode}")
    if not queue.empty():
        result = queue.get()
        if isinstance(result, Exception):
            print("Error evaluating:", program_str, result)
            return 0.0
        if(result['success']):
            final.append(program_str)
        return float(result['total_reward'])
    else:
        print("No result returned.")
        return float('-inf')

final = []
def is_terminal(symbol: str, cfg: CFGParser) -> bool:
    return symbol not in cfg.non_terminals

def evaluate_program_with_evaluator(program_str: str) -> int:
    """
    Evaluate a program using your ProgramEvaluator.
    """
    try:
        evaluator = ProgramEvaluator()
        result = evaluator.evaluate_program(program_str)
        # print("result", result)
        if(result['success'] and all(is_terminal(sym, cfg) for sym in program_str)):
            final.append(program_str)
        return result['total_reward']
    except Exception as e:
        print("Error evaluating:", program_str, e)
        return float('-inf')

# def run_with_timeout(evaluator, program_str, timeout=200):
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future = executor.submit(evaluator.evaluate_program, program_str)
#         print("program", program_str)
#         try:
#             # print("program", program_str)
#             result = float(future.result(timeout=timeout)['total_reward'])
#         except concurrent.futures.TimeoutError:
#             print("Evaluation timed out.")
#             return float('-inf')
#         except Exception as e:
#             print("Error evaluating:", program_str, e)
#             return float('-inf')
#         return result

# def run_with_timeout(evaluator, program_str, timeout=5):
#     with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
#         future = executor.submit(evaluator.evaluate_program, program_str)
#         print("program", program_str)
#         try:
#             result = float(future.result(timeout=timeout)['total_reward'])
#         except concurrent.futures.TimeoutError:
#             print("Evaluation timed out.")
#             return float('-inf')
#         except Exception as e:
#             print("Error evaluating:", program_str, e)
#             return float('-inf')
#         return result

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

def synthesize_priority(cfg: CFGParser, start_symbol: str, max_depth: int):
    """
    Priority-queue-based program synthesis using environment rewards.
    """
    counter = itertools.count()  # Tie-breaker for equal priorities
    queue: List[Tuple[int, int, int, List[str]]] = []  # (neg_reward, depth, count, derivation)

    heapq.heappush(queue, (0, 0, next(counter), [start_symbol]))

    while queue:
        neg_reward, depth, _, current = heapq.heappop(queue)

        if all(is_terminal(sym, cfg) for sym in current):
            program_str = format_program(current)
            yield program_str
            continue

        if depth >= max_depth:
            continue
        evaluator = ProgramEvaluator()
        # Expand first non-terminal
        for idx, sym in enumerate(current):
            if not is_terminal(sym, cfg):
                for production in cfg.rules[sym]:
                    for alt in tokenize_rhs(production):
                        new_derivation = current[:idx] + alt + current[idx+1:]
                        program_str = format_program(new_derivation)
                        reward = run_with_timeout(evaluator, program_str)
                        heapq.heappush(queue, (-reward, depth + 1, next(counter), new_derivation))
                break

        if(len(final) > 5):
            with open("final.txt", "w") as f:
                for program in final:
                    f.write(program + "\n")
            break

if __name__ == "__main__":
    cfg_parser = CFGParser("cfg.txt")
    start_symbol = "s"
    print(f"Start symbol: {start_symbol}")
    print("\nGenerating programs (worklist)...")
    for i, program in enumerate(synthesize_priority(cfg_parser, start_symbol, max_depth=15), 1):
        print(f"\n=== Program {i} ===")
        print(program)
