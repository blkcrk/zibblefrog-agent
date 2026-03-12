import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def executor(step: str, model: str = "llama-3.3-70b-versatile") -> str:
    prompt = f"""You are an executor agent. Carry out the following step and report the result concisely.
Step: {step}"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
