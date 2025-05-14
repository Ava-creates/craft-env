import subprocess
import requests

def run_and_capture(script_path):
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode

def read_script_content(script_path):
    with open(script_path, 'r') as file:
        return file.read()

def send_to_llm(script_content, error_message):
    api_url = "http://129.128.243.184:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    prompt = f"""Here is a Python script that has an error:
{script_content}

Error message:
{error_message}

Please provide the corrected version of the script that fixes this error. Return only the corrected Python code without any explanations."""

    payload = { 
        "model": "qwen2.5-coder:32b", 
        "prompt": prompt, 
        "stream": False,
        "options": {
            "num_ctx": 4096,
        }
    }
    res = requests.post(api_url, headers=headers, json=payload, timeout=3000)
    return res.json()

if __name__ == "__main__":
    script = "evaluator.py"
    script_content = read_script_content(script)
    stdout, stderr, code = run_and_capture(script)
    print("STDOUT:\n", stdout)
    if code != 0:
        print("STDERR:\n", stderr)
        corrected_script = send_to_llm(script_content, stderr)
        print("CORRECTED SCRIPT:\n", corrected_script)
        
        # Optionally save the corrected script
        with open("corrected_" + script, 'w') as file:
            file.write(corrected_script)
    else:
        print("Script ran successfully.")