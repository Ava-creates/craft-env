with open("prompt_specifications/specification_with_updated_nld.txt", "r") as f:
    prompt = f.read()

with open("craft_func.py", "r") as f:
    func = f.read()

prompt = prompt + "\n" + "def craft(env, item): \n" + func

prompt += "we have the function above analyse the function and give feedback on it as it is not working properly in bullet points and an updated function"



from google import genai
import requests

client = genai.Client()


response = client.models.generate_content(
                        model="gemini-2.5-pro", contents = prompt
                    )
b = response.text

print(b)