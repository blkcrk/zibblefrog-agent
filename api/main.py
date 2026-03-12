import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from memory.run_store import init_db, get_run, get_run_events
from orchestrator.run_manager import stream_run
from pipelines.csv_pipeline import stream_csv
from pipelines.catalog_pipeline import stream_catalog_pipeline
import pandas as pd
from io import StringIO

# Ensure tools are registered
import tools.taxonomy_tool
import tools.seo_tool
import tools.kpi_tool
import tools.description_tool
import tools.enrichment_tool
import tools.bigcommerce_tool
import tools.catalog_score_tool

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

@app.post("/catalog-pipeline-stream")
async def catalog_pipeline_stream(
    file: UploadFile = File(...),
    model: str = "gpt-4o-mini",
    mode: str = "preview",
):
    content = (await file.read()).decode()
    df = pd.read_csv(StringIO(content))
    products = df.to_dict(orient="records")
    return StreamingResponse(
        stream_catalog_pipeline(products, model=model, mode=mode),
        media_type="text/event-stream",
    )

@app.get("/fetch-bc-products")
async def fetch_bc_products():
    from tools.bigcommerce_connector import fetch_products, bc_to_csv_row
    products = await fetch_products()
    rows = [bc_to_csv_row(p) for p in products]
    csv = pd.DataFrame(rows).to_csv(index=False)
    return {"count": len(rows), "csv": csv}

@app.get("/analyze-bc-stream")
async def analyze_bc_stream(model: str = "gpt-4o-mini"):
    from tools.bigcommerce_connector import fetch_products, bc_to_csv_row
    products = await fetch_products()
    rows = [bc_to_csv_row(p) for p in products]
    csv_content = pd.DataFrame(rows).to_csv(index=False)
    return StreamingResponse(stream_csv(csv_content, model), media_type="text/event-stream")

@app.get("/analyze-bc-catalog-stream")
async def analyze_bc_catalog_stream(model: str = "gpt-4o-mini", mode: str = "preview"):
    from tools.bigcommerce_connector import fetch_products, bc_to_csv_row
    products = await fetch_products()
    rows = [bc_to_csv_row(p) for p in products]
    return StreamingResponse(
        stream_catalog_pipeline(rows, model=model, mode=mode),
        media_type="text/event-stream",
    )

@app.post("/preview-changes")
async def preview_changes(updates: list[dict]):
    from tools.registry import get
    from tools.bigcommerce_tool import BCPublishInput
    result = await get("bigcommerce").execute(BCPublishInput(updates=updates, mode="preview"))
    return result.model_dump()

@app.post("/publish-changes")
async def publish_changes(updates: list[dict]):
    from tools.registry import get
    from tools.bigcommerce_tool import BCPublishInput
    result = await get("bigcommerce").execute(BCPublishInput(updates=updates, mode="publish"))
    return result.model_dump()

@app.post("/score")
async def score_product(
    product_name: str,
    seo_name: str = "",
    taxonomy_confidence: float = 0.0,
    attribute_completeness: float = 0.0,
):
    from tools.registry import get
    from tools.catalog_score_tool import CatalogScoreInput
    result = await get("catalog_score").execute(CatalogScoreInput(
        product_name=product_name,
        seo_name=seo_name,
        taxonomy_confidence=taxonomy_confidence,
        attribute_completeness=attribute_completeness,
    ))
    return result.model_dump()

@app.get("/audit")
async def audit(limit: int = 250):
    from jobs.catalog_audit import audit_catalog
    return await audit_catalog(limit=limit)

@app.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    run = get_run(run_id)
    if not run:
        return {"error": "not found"}
    return {"run": run, "events": get_run_events(run_id)}