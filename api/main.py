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


@app.get("/fetch-bc-products")
async def fetch_bc_products():
    from tools.bigcommerce_connector import fetch_products, bc_to_csv_row
    import pandas as pd
    products = await fetch_products()
    rows = [bc_to_csv_row(p) for p in products]
    csv = pd.DataFrame(rows).to_csv(index=False)
    return {"count": len(rows), "csv": csv}

@app.get("/analyze-bc-stream")
async def analyze_bc_stream(model: str = "gpt-4o-mini"):
    from tools.bigcommerce_connector import fetch_products, bc_to_csv_row
    import pandas as pd
    products = await fetch_products()
    rows = [bc_to_csv_row(p) for p in products]
    csv_content = pd.DataFrame(rows).to_csv(index=False)
    return StreamingResponse(stream_csv(csv_content, model), media_type="text/event-stream")


@app.post("/preview-changes")
async def preview_changes(updates: list[dict]):
    import tools.bigcommerce_tool
    from tools.registry import get
    from tools.bigcommerce_tool import BCPublishInput
    tool = get("bigcommerce")
    result = await tool.execute(BCPublishInput(updates=updates, mode="preview"))
    return result.model_dump()

@app.post("/publish-changes")
async def publish_changes(updates: list[dict]):
    import tools.bigcommerce_tool
    from tools.registry import get
    from tools.bigcommerce_tool import BCPublishInput
    tool = get("bigcommerce")
    result = await tool.execute(BCPublishInput(updates=updates, mode="publish"))
    return result.model_dump()

@app.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    run = get_run(run_id)
    if not run:
        return {"error": "not found"}
    return {"run": run, "events": get_run_events(run_id)}
