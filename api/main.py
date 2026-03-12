import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from memory.run_store import init_db, get_run, get_run_events
from orchestrator.run_manager import stream_run
from pipelines.csv_pipeline import stream_csv

# Ensure tools are registered
import tools.taxonomy_tool
import tools.seo_tool
import tools.kpi_tool
import tools.description_tool

app = FastAPI(title="Zibblefrog Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/stream")
def stream(goal: str, model: str = "gpt-4o-mini"):
    return StreamingResponse(stream_run(goal, model), media_type="text/event-stream")

@app.post("/analyze-csv-stream")
async def analyze_csv_stream(file: UploadFile = File(...), model: str = "gpt-4o-mini"):
    content = (await file.read()).decode()
    return StreamingResponse(stream_csv(content, model), media_type="text/event-stream")

@app.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    run = get_run(run_id)
    if not run:
        return {"error": "not found"}
    return {"run": run, "events": get_run_events(run_id)}
