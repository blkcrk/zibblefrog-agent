import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def planner(goal: str, model: str = "gpt-4o-mini") -> list[str]:
    prompt = (
        "You are a planner. Break the following goal into a numbered list of clear, simple steps.\n"
        f"Goal: {goal}\n"
        "Respond with only the numbered steps, nothing else."
    )
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    return [line.strip() for line in text.strip().split("\n") if line.strip()]
