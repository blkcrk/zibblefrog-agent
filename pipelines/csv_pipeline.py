import asyncio
import pandas as pd
from io import StringIO
from typing import AsyncIterator
from tools.registry import get
from tools.taxonomy_tool import TaxonomyInput
from tools.seo_tool import SEOInput
from tools.kpi_tool import KPIInput
from orchestrator.event_models import AgentEvent
import uuid

MAX_CONCURRENCY = 5

async def process_row(row: dict, model: str, run_id: str) -> dict:
    name = str(row.get("Name", ""))
    tax_tool = get("taxonomy")
    seo_tool = get("seo")
    kpi_tool = get("kpi")

    tax_out = await tax_tool.execute(TaxonomyInput(product_name=name, model=model))
    seo_out = await seo_tool.execute(SEOInput(product_name=name, model=model))
    kpi_out = await kpi_tool.execute(KPIInput(
        original_name=name,
        seo_name=seo_out.seo_name,
        subcategory=tax_out.subcategory,
        model=model
    ))
    return {
        **row,
        "Suggested_Category": tax_out.subcategory,
        "SEO_Name": seo_out.seo_name,
        "Expected_KPI": kpi_out.kpi_summary,
        "_tax_input": f"Classify: {name}",
        "_tax_output": tax_out.subcategory,
        "_seo_input": f"Rewrite for SEO: {name}",
        "_seo_output": seo_out.seo_name,
        "_kpi_input": f"KPI for: {name} -> {seo_out.seo_name}",
        "_kpi_output": kpi_out.kpi_summary,
    }

async def stream_csv(csv_content: str, model: str = "gpt-4o-mini") -> AsyncIterator[str]:
    run_id = str(uuid.uuid4())
    df = pd.read_csv(StringIO(csv_content))
    rows = df.to_dict(orient="records")
    total = len(rows)
    results = []
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async def bounded(row, idx):
        async with sem:
            try:
                return await process_row(row, model, run_id)
            except Exception as e:
                return {**row, "error": str(e)}

    tasks = [asyncio.create_task(bounded(row, i)) for i, row in enumerate(rows)]

    completed = 0
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        completed += 1

        name = result.get("Name", "")

        for agent, inp, out in [
            ("taxonomy", result.get("_tax_input",""), result.get("_tax_output","")),
            ("seo",      result.get("_seo_input",""), result.get("_seo_output","")),
            ("kpi",      result.get("_kpi_input",""), result.get("_kpi_output","")),
        ]:
            ev = AgentEvent(type="dialogue", run_id=run_id, agent=agent,
                            content={"product": name, "agent": agent, "input": inp, "output": out})
            yield ev.to_sse()

        ev = AgentEvent(type="pipeline_progress", run_id=run_id,
                        content={"current": completed, "total": total})
        yield ev.to_sse()

    # Strip internal keys before export
    clean = [{k:v for k,v in r.items() if not k.startswith("_")} for r in results]
    csv_out = pd.DataFrame(clean).to_csv(index=False)
    ev = AgentEvent(type="run_completed", run_id=run_id, content={"csv": csv_out})
    yield ev.to_sse()
