import ollama

def executor(step: str, model: str = "llama3.2") -> str:
    prompt = f"""You are an executor agent. Carry out the following step and report the result concisely.
Step: {step}"""
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]
