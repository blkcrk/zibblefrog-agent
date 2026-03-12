import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def executor(step: str, model: str = "gpt-4o-mini") -> str:
    prompt = f"You are an executor agent. Carry out the following step and report the result concisely.\nStep: {step}"
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
