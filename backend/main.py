import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
from backend.agents.orchestrator import run_pipeline
import json

app = FastAPI(title="Zibblefrog Agent Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.environ["GROQ_API_KEY"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Zibblefrog agent is running"}

@app.post("/chat")
def chat(prompt: str, model: str = "llama-3.3-70b-versatile"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}

@app.post("/run")
def run(goal: str, model: str = "llama-3.3-70b-versatile"):
    return run_pipeline(goal, model)

@app.get("/stream")
def stream(goal: str, model: str = "llama-3.3-70b-versatile"):
    def event_stream():
        # Step 1: Planner
        yield f"data: {json.dumps({'agent': 'planner', 'status': 'thinking', 'content': ''})}\n\n"
        planner_prompt = f"""You are a planner. Break the following goal into a numbered list of clear, simple steps.
Goal: {goal}
Respond with only the numbered steps, nothing else."""
        planner_stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": planner_prompt}],
            stream=True
        )
        plan_text = ""
        for chunk in planner_stream:
            delta = chunk.choices[0].delta.content or ""
            plan_text += delta
            yield f"data: {json.dumps({'agent': 'planner', 'status': 'streaming', 'content': delta})}\n\n"

        # Parse steps
        steps = [l.strip() for l in plan_text.strip().split("\n") if l.strip()]
        yield f"data: {json.dumps({'agent': 'planner', 'status': 'done', 'steps': steps})}\n\n"

        # Step 2: Executor for each step
        for step in steps:
            yield f"data: {json.dumps({'agent': 'executor', 'status': 'thinking', 'step': step})}\n\n"
            exec_stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Execute this step concisely: {step}"}],
                stream=True
            )
            for chunk in exec_stream:
                delta = chunk.choices[0].delta.content or ""
                yield f"data: {json.dumps({'agent': 'executor', 'status': 'streaming', 'step': step, 'content': delta})}\n\n"
            yield f"data: {json.dumps({'agent': 'executor', 'status': 'done', 'step': step})}\n\n"

        yield f"data: {json.dumps({'agent': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
