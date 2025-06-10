from typing import List, Dict, Any
import env_factory
import time
import re
import json
import os
import io
import contextlib

class ProgramEvaluator:
    def __init__(self, recipes_path: str = "resources/recipes.yaml", 
                 hints_path: str = "resources/hints.yaml",
                 visualise: bool = True):
        self.env_sampler = env_factory.EnvironmentFactory(
            recipes_path, hints_path, max_steps=100, 
            reuse_environments=False, visualise=visualise)
        self.visualise = visualise
        self.best_samples = self._load_all_best_samples()
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

        self.has = """
def has(env, item):
        count = env._current_state.inventory[item]
        print(count > 0)
        return count > 0 """

        self.craft = """
def craft(env, item):
            def bfs(start_state):
                queue = [(start_state, [])]
                visited_states = set()
                
                while queue:
                    current_state, path = queue.pop(0)
                    
                    # Convert the state to a hashable format for storing in visited set
                    state_hash = tuple(current_state.grid.flatten()) + tuple(current_state.inventory) + (current_state.pos, current_state.dir)

                    if state_hash in visited_states:
                        continue
                    
                    visited_states.add(state_hash)
                    
                    # Check if goal is satisfied
                    if current_state.satisfies(None, item):
                        return path

                    for action in range(env.world.n_actions):
                        _, new_state = current_state.step(action)
                        queue.append((new_state, path + [action]))
                
                return []

            start_state = env._current_state
            a = bfs(start_state)
            for r in a:
                print(r)
            return a
        """
        
    def _load_all_best_samples(self) -> Dict[str, List[Dict]]:
        """Load and parse all best samples from the log files."""
        samples = {}
        
        # Load move samples
        move_samples = self._load_best_samples("results/best_samples_2025-06-03_13-02-44_move.log")
        if move_samples:
            samples['move'] = move_samples
        

        return samples
        
    def _load_best_samples(self, log_file: str) -> List[Dict]:
        """Load and parse the best samples from a log file."""
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Split content into individual samples
            samples = content.split('Best Sample')
            samples = [s.strip() for s in samples if s.strip()]
            
            implementations = []
            for i, sample in enumerate(samples, 1):
                # Extract the function body (everything after the first line)
                lines = sample.split('\n')
                if len(lines) > 1:
                    implementation = '\n'.join(lines[1:]).strip()
                    implementation = '\n'.join(line for line in implementation.split('\n'))
                    implementations.append(
                     implementation
                    )
            
            return implementations
        except FileNotFoundError:
            # print(f"Warning: Best samples log file {log_file} not found")
            return []
            
    def get_best_samples(self, function_name: str = None) -> Dict[str, List[Dict]]:
        """Return the loaded best samples, optionally filtered by function name."""
        if function_name:
            return {function_name: self.best_samples.get(function_name, [])}
        return self.best_samples
        
        
    def parse_program(self, program: str, env: Any = None) -> List[int]:
        """Convert a program string into a list of actions."""
        actions = []
        tokens = program.split()
        # print("tokens", tokens)
        i = 0
        reward = 0
        move_samples = self.get_best_samples('move')["move"]
       
        if not move_samples:
            raise ValueError("No move function implementations found")
            
        move_impl = move_samples[1]
        exec_env = {}
        d = False
        while i < len(tokens):
            if len(tokens[i]) > 10 and tokens[i][:9] == "MOVE_FUNC":
                dir_str = tokens[i].split('(')[1].strip(')')
                exec_env = {}
                exec(move_impl,exec_env)
                output_buffer = io.StringIO()
                with contextlib.redirect_stdout(output_buffer):
                        result = exec_env['move'](env, dir_str)
                printed_output = output_buffer.getvalue()
                # print("Captured print:", printed_output.strip())
                # actions.append(result)
                
                r, done, observations = env.step(result)
                if done:
                    d = True
                reward += r
                i += 1
                
            if len(tokens[i]) > 11 and tokens[i][:10] == "CRAFT_FUNC":
                dir_str = tokens[i].split('(')[1].strip(')')
                exec_env = {}
                # print("item", dir_str)
                exec(self.craft,exec_env)
                output_buffer = io.StringIO()
                with contextlib.redirect_stdout(output_buffer):
                        result = exec_env['craft'](env, int(self.item_map[dir_str]))
                printed_output = output_buffer.getvalue()
                # print("Captured print:", printed_output.strip())
                # print("printed_output", printed_output.strip())
                for j in printed_output.strip().split('\n'):
                    r, done, observations = env.step(int(j))
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
                    exec_env = {}
                    exec(self.has,exec_env)
                    output_buffer = io.StringIO()
                    with contextlib.redirect_stdout(output_buffer):
                            result = exec_env['has'](env, int(self.item_map[item]))
                    printed_output = output_buffer.getvalue()
                    # print("Captured print:", printed_output.strip())
                    if(printed_output.strip() == "False"):
                        i+=3
                    else:
                        i+=3
                        
                else:
                    raise ValueError(f"Unsupported if condition: {condition}")

                # print("i", i)

            elif tokens[i] == ";":
                i += 1

            elif tokens[i] == "":
                i += 1  

            else:
                print("Unknown token", tokens[i])
                return [], reward, False

        return actions, reward, d

    def evaluate_program(self, program: str, task_name: str = 'make[arrow]') -> Dict[str, Any]:
        """Evaluate a program in the craft environment."""
        # Create environment
        env = self.env_sampler.sample_environment(task_name=task_name)
        # print(f"Environment: task {env.task_name}: {env.task}")
        
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