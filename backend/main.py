import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from openai import OpenAI
from backend.agents.orchestrator import run_pipeline
from backend.agents.csv_pipeline import process_csv_stream
import json

app = FastAPI(title="Zibblefrog Agent Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Zibblefrog agent is running"}

@app.post("/chat")
def chat(prompt: str, model: str = "gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}

@app.post("/run")
def run(goal: str, model: str = "gpt-4o-mini"):
    return run_pipeline(goal, model)

@app.get("/stream")
def stream(goal: str, model: str = "gpt-4o-mini"):
    def event_stream():
        yield f"data: {json.dumps({'agent': 'planner', 'status': 'thinking', 'content': ''})}\n\n"
        planner_prompt = (
            "You are a planner. Break the following goal into a numbered list of clear, simple steps.\n"
            f"Goal: {goal}\n"
            "Respond with only the numbered steps, nothing else."
        )
        planner_stream = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": planner_prompt}], stream=True
        )
        plan_text = ""
        for chunk in planner_stream:
            delta = chunk.choices[0].delta.content or ""
            plan_text += delta
            yield f"data: {json.dumps({'agent': 'planner', 'status': 'streaming', 'content': delta})}\n\n"
        steps = [l.strip() for l in plan_text.strip().split("\n") if l.strip()]
        yield f"data: {json.dumps({'agent': 'planner', 'status': 'done', 'steps': steps})}\n\n"
        for step in steps:
            yield f"data: {json.dumps({'agent': 'executor', 'status': 'thinking', 'step': step})}\n\n"
            exec_stream = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": f"Execute this step concisely: {step}"}], stream=True
            )
            for chunk in exec_stream:
                delta = chunk.choices[0].delta.content or ""
                yield f"data: {json.dumps({'agent': 'executor', 'status': 'streaming', 'step': step, 'content': delta})}\n\n"
            yield f"data: {json.dumps({'agent': 'executor', 'status': 'done', 'step': step})}\n\n"
        yield f"data: {json.dumps({'agent': 'done'})}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...), model: str = "gpt-4o-mini"):
    content = await file.read()
    result_csv = process_csv(content.decode(), model)
    return Response(content=result_csv, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=analyzed_inventory.csv"})

@app.post("/analyze-csv-stream")
async def analyze_csv_stream(file: UploadFile = File(...), model: str = "gpt-4o-mini"):
    content = await file.read()
    csv_content = content.decode()
    def event_stream():
        for event in process_csv_stream(csv_content, model):
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
