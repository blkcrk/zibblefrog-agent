from .planner import planner
from .executor import executor

def run_pipeline(goal: str, model: str = "llama3.2") -> dict:
    steps = planner(goal, model)
    results = [{"step": step, "result": executor(step, model)} for step in steps]
    return {"goal": goal, "steps": results}
