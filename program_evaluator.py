from typing import List, Dict, Any
import env_factory
import time
import re
import json
import os
import io
import contextlib
from craft_func import craft
from has_func import has
from move_func import move
import multiprocessing
def run_funcs(queue, func_name, args_1, env):
    try:
        w = args_1[0]
        if func_name == "move":
            result = move(env, w)
        elif func_name == "craft":
            result = craft(env, w)
        elif func_name == "has":
            result = has(env, w) 
        queue.put(result)
    except Exception as e:
        queue.put(e)

def run_with_timeout(func_name, args_1, env, timeout=20):
        queue_obj = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_funcs, args=(queue_obj, func_name, args_1, env))
        p.start()
        p.join(timeout)
        if p.is_alive():
            # print("Evaluation timed out.")
            p.terminate()
            p.join()
            return -1
        if not queue_obj.empty():
            result = queue_obj.get()
            if isinstance(result, Exception):
                print("Error evaluating:", result)
                return -1
            return result
        else:
            print("No result returned.")
            return -1
class ProgramEvaluator:
    def __init__(self, recipes_path: str = "resources/recipes.yaml", 
                 hints_path: str = "resources/hints.yaml",
                 visualise: bool = True):
        # self.env_sampler = env_factory.EnvironmentFactory(
        #     recipes_path, hints_path, max_steps=100, 
        #     reuse_environments=False, visualise=visualise)
        # self.visualise = visualise
        self.item_map =item_id_map = {
                                "PLANK": 13,
                                "STICK": 14,
                                "CLOTH": 15,
                                "ROPE": 16,
                                "BRIDGE": 17,
                                "BUNDLE": 18,
                                "HAMMER": 19,
                                "KNIFE": 20,
                                "BED": 21,
                                "AXE": 22,
                                "SHEARS": 23,
                                "LADDER": 24,
                                "SLINGSHOT": 25,
                                "ARROW": 26,
                                "BOW": 27,
                                "BENCH": 28,
                                "FLAG": 29,
                                "GOLDARROW": 30
                            }


    def parse_program(self, program: str, env: Any = None) -> List[int]:
        """Convert a program string into a list of actions."""
        actions = []
        tokens = program.split()
        # print("tokens", tokens)
        i = 0
        reward = 0
    
        d = False
        while i < len(tokens):
            if len(tokens[i]) > 10 and tokens[i][:9] == "MOVE_FUNC":
                dir_str = tokens[i].split('(')[1].strip(')')

                result = run_with_timeout( "move", [dir_str], env)
                if(result == -1):
                    print("Evaluation timed out in move")
                    return [], reward, False
                r, done, observations = env.step(result)
                if done:
                    d = True
                reward += r
                i += 1
                
            if len(tokens[i]) > 11 and tokens[i][:10] == "CRAFT_FUNC":
                dir_str = tokens[i].split('(')[1].strip(')')
                item = self.item_map[dir_str]
                result = run_with_timeout( "craft", [item], env)
                if(result == -1):
                    print("Evaluation timed out in craft")
                    return [], reward, False
                for j in result:
                    r, done, observations = env.step(j)
                    if done:
                        d = True
                    reward += r 
                i += 1
        
            elif tokens[i] == "if" and i + 4 < len(tokens):
                # print(i)
                condition = tokens[i + 1]
                then_token = tokens[i + 2]
                then_action = tokens[i + 3]

                if condition.startswith("has(") and condition.endswith(")"):
                    item = condition[4:-1]  # Extract "GOLDARROW"    
                    # print("item", item)
                    item = int(self.item_map[item])
                    result = run_with_timeout("has", [item], env)
                    if(result == -1):
                        print("Evaluation timed out in has")
                        return [], reward, False
                    # print("Captured print:", printed_output.strip())
                    if(result == False):
                        i+=3
                    else:
                        i+=3
                        
                else:
                    raise ValueError(f"Unsupported if condition: {condition}")

            elif tokens[i] == ";":
                i += 1

            elif tokens[i] == "":
                i += 1  

            else:
                # print("Unknown token", tokens[i])
                return [], reward, False

        return actions, reward, d

    def evaluate_program(self, program: str, env) -> Dict[str, Any]:
        """Evaluate a program in the craft environment."""
        # Create environment
        # env = self.env_sampler.sample_environment(task_name=task_name)
        # print(f"Environment: task {env.task_name}: {env.task}")
        env.reset()
        # Parse program into actions using the actual environment
        actions, reward, d = self.parse_program(program, env)
        # print("actions", actions)
        # Reset environment
        observations = env.reset()
        total_reward = 0 + reward
        done = False
        return {
            "total_reward": total_reward,
            "success": d and total_reward > 0,
        }

def main():
    # Example usage
    evaluator = ProgramEvaluator(visualise=True)
    
    # Example program
    # program = "MOVE_FUNC(UP) ; CRAFT_FUNC(KNIFE) ; if has(KNIFE) then CRAFT_FUNC(ARROW) ; MOVE_FUNC(UP) ;"
    program = "if has(BED) then if has(SLINGSHOT) then if has(BRIDGE) then task ;"
    # Evaluate program
    result = evaluator.evaluate_program(program)
    print("\nEvaluation Results:")
    print(f"Total Reward: {result['total_reward']}")
    print(f"Success: {result['success']}")

if __name__ == "__main__":
    main() 