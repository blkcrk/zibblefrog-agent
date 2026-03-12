import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def planner(goal: str, model: str = "llama-3.3-70b-versatile") -> list[str]:
    prompt = f"""You are a planner. Break the following goal into a numbered list of clear, simple steps.
Goal: {goal}
Respond with only the numbered steps, nothing else."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    steps = [line.strip() for line in text.strip().split("\n") if line.strip()]
    return steps
