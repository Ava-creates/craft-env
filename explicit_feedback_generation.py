import requests
import json
import os
import subprocess
import time

def eval(res):
            # with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = os.getcwd()
            script_path = os.path.join(temp_dir, 'generated_code.py')
            
            full_program_collect=f'''
import numpy as np
import time
import collections
import env_factory
import craft
import env

import env_factory
def solve(env, primitive, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = collect(env, primitive)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break

  if total_reward>0.5:
    return 0.2

  return total_reward


def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"
  reward = 0 
  for i in range(10):
    if(i == 0):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
    
    elif(i==1):
      p = "iron"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      
    elif(i==2):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()

    elif(i==3): #grass not present onthe grid should return empty list
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()

    elif(i==4):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[plank]')
      env.reset()
      #env.step(1)
      #env.step(4)

    elif(i==5):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 3, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[cloth]')
      env.reset()
      #env.step(1)
      #env.step(4)


    elif(i==6):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 4, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[rope]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)

    elif(i==7):
      p = "grass"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)
      #env.step(0)
      #env.step(4)

    elif(i==8):
      p = "wood"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      #env.step(0)
      #env.step(0)
      #env.step(4)

    else:
      p = "gold"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 6, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
      env.reset()
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      
    r= solve(env, p, visualise=visualise)
    reward += r

  return reward
  
  
def collect(env, primitive):
{res}

print(evaluate())'''
# print(full_program_collect)
            # Create complete executable program
            full_program = f'''
import numpy as np
import time
import collections
import env_factory

def solve(env, item, visualise=False) -> float:
  """Runs the environment with a collect function that returns list of actions to take and returns total reward."""
  actions_to_take = craft(env, item)
  total_reward = 0.0

  for t in range(len(actions_to_take)):
    action = actions_to_take[t]
    reward, done, observations = env.step(action)
    total_reward += reward
    if done:
      break
#   print(item, total_reward, actions_to_take)
  return total_reward

def evaluate() -> float:
  """Evaluates a crafting policy on a sample task."""
  #max reward is 6 for this fucntion so any craft objet that can get when it is working properly
  visualise = False
  recipes_path = "resources/recipes.yaml"
  hints_path = "resources/hints.yaml"     
  reward = 0 
  for i in range(11):
    if(i == 0):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item,  visualise=visualise) #should give +1
    
    elif(i==1):
      item = "stick"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 0, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[stick]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise)  #should give 0 when it is working properly
      if temp_reward>0 :
        reward -= 0.3
      
    elif(i==2):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  # 0 when working properly

    elif(i==3):
      item = "bridge"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 1, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bridge]')
      env.reset()
      temp_reward = solve(env, item, visualise=visualise) # 0 when working properly 
      if temp_reward>0 :
        reward -= 0.3

    elif(i==4):
      item = "plank"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 2, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[plank]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise) # +1 this does nnot work need to collect more before crafting

    elif(i==5):
      item = "cloth"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 3, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[cloth]')
      env.reset()
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  #+1


    elif(i==6):
      item = "rope"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 4, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[rope]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise) #+1

    elif(i==7):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)
      env.step(0)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  #+1

    elif(i==8):
      item = "bundle"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 5, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[bundle]')
      env.reset()
      env.step(0)
      env.step(0)
      env.step(4)

      temp_reward = solve(env, item, visualise=visualise)
      if temp_reward>0 :
        reward -= 0.3

    elif(i==9):
      item = "goldarrow"
      env_sampler = env_factory.EnvironmentFactory(
      recipes_path, hints_path, 6, max_steps=100, reuse_environments=False,
            visualise=visualise)

      env = env_sampler.sample_environment(task_name= 'make[goldarrow]')
      env.reset()
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward += solve(env, item, visualise=visualise)  # +1

    else:
      recipes_path_2 = "resources/recipes_for_synth.yaml"
      item = "arrow"
      env_sampler = env_factory.EnvironmentFactory(
            recipes_path_2, hints_path, 6, max_steps=100, 
            reuse_environments=False, visualise=False)
      env=env_sampler.sample_environment(task_name='make[arrow]')
      env.reset()
      # Actions to execute:
      env.step(0)
      env.step(2)
      env.step(2)
      env.step(4)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(0)
      env.step(2)
      env.step(4)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(2)
      env.step(4)
      env.step(1)
      env.step(1)
      env.step(4)
      reward+=solve(env, item, visualise=visualise) 
      
  return reward

def craft(env, item):
{res}

print(evaluate())
                        '''
            # print(full_program)
            with open(script_path, 'w') as f:
                f.write(full_program_collect.strip())

            try:
                # Convert input to string representatio
                
                # Execute in subprocess with timeout
                result = subprocess.run(
                    ['python', script_path],
                    capture_output=True,
                    text=True,
                    timeout=300, #this is in seconds
                    check=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                # Try to parse numerical output
                output = result.stdout.strip()
                # print("output ", output)
                try:
                    return float(output), True
                except ValueError:
                    return -1, True
                
            except subprocess.TimeoutExpired:
                return -1, False
            except subprocess.CalledProcessError as e:
                print(f"Process Error: Command failed with exit code {e.returncode}")
                print(f"Command: {e.cmd}")
                print(f"Output: {e.stdout}")
                print(f"Error: {e.stderr}")
                return -1, False


with open("prompt_specifications/specification_with_updated_nld.txt", "r") as f:
    prompt1 = f.read()

with open("collect_perf.py", "r") as f:
    func = f.read()

prompt = prompt1 + "\n" + "def collect(env, primitive): \n" + func

prompt += "we have the function above analyse the function and give natural language feedback on it as it is not working properly in bullet points."



from google import genai
import requests

client = genai.Client()


response = client.models.generate_content(
                        model="gemini-2.5-pro", contents = prompt
                    )
b = response.text

print(b)

prompt = prompt1 + "feedback:\n"+b +  "def collect(env, primitive): \n" + func + "Return the corrected version of the function"


for i in range(10):
    response = client.models.generate_content(
                            model="gemini-2.5-pro", contents = prompt
                        )
    b = response.text

    # print("second generation\n", b)

    b = b[b.index("def collect(env, primitive):")+len("def collect(env, primitive):")+1:]
    b= b[:b.index("```")]
    
    # # Log the extracted function code
    # print(f"Iteration {i+1} - Extracted function code:")
    # print(b)
    # print("-" * 50)
    
    # Log the evaluation result
    eval_result = eval(b)
    
    # Create dictionary for structured logging
    log_entry = {
        "extracted_function_code": b,
        "evaluation_result": eval_result,
    }
    print(eval_result)
    # Write to log file in JSON format
    with open("feedback_sampling.json", 'a') as log_file:
        log_file.write(json.dumps(log_entry, indent=2) + "\n")
  

