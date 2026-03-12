import ollama

def planner(goal: str, model: str = "llama3.2") -> list[str]:
    prompt = f"""You are a planner. Break the following goal into a numbered list of clear, simple steps.
Goal: {goal}
Respond with only the numbered steps, nothing else."""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    text = response["message"]["content"]
    steps = [line.strip() for line in text.strip().split("\n") if line.strip()]
    return steps
