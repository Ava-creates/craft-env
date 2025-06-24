import requests

from funsearch.implementation.funsearch import FunSearch


api_url = "http://129.128.243.184:11434/api/generate"
headers = {"Content-Type": "application/json"}
a = FunSearch()
with open("specification.txt", 'r') as f:
        specification = f.read()
stop_tokens = ["\ndef", "\nclass", "\n#", "\nimport"]
prompt = a._replace_function_in_specification(specification,  "craft")
# print(prompt)
payload = {
          "model": "qwen2.5-coder:32b", 
          "prompt": prompt, 
          "stream": False, 
          "template": "{{ .Prompt }}", 
          "options": {
            "num_ctx": 4096, 
            "stop": stop_tokens
          }
        }
res = requests.post(api_url, headers=headers, json=payload, timeout=300)

print(res.json()["response"])