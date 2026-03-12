"""Full async catalog optimization pipeline.
Covers: normalization (T6), diff engine (T10), preview mode (T11), async concurrency (T14).
"""
import asyncio, uuid
from typing import AsyncGenerator
from orchestrator.event_models import AgentEvent

MAX_CONCURRENCY = 5

# ── Ticket 6: Normalization ───────────────────────────────────────────────
FIELD_MAP = {
    "name":        ["Name", "name", "product_name", "title", "Title"],
    "sku":         ["SKU", "sku", "item_number", "ItemNumber"],
    "description": ["Description", "description", "body_html"],
    "price":       ["Price", "price", "base_price"],
}

def normalize_product(row: dict) -> dict:
    """Map supplier/CSV field names to internal product schema."""
    out = {}
    for key, candidates in FIELD_MAP.items():
        for c in candidates:
            if c in row:
                out[key] = str(row[c]).strip()
                break
        out.setdefault(key, "")
    out["original_name"] = out["name"]
    out["original_description"] = out["description"]
    return out

# ── Ticket 10: Diff engine ────────────────────────────────────────────────
DIFF_FIELDS = [
    ("original_name",        "seo_name",    "SEO Title"),
    ("original_name",        "name",        "Product Title"),
    ("original_description", "description", "Description"),
]

def compute_diff(product: dict) -> list[dict]:
    """Return human-readable diffs between original and optimised fields."""
    diffs = []
    for orig_key, new_key, label in DIFF_FIELDS:
        orig = product.get(orig_key, "").strip()
        new  = product.get(new_key,  "").strip()
        if orig and new and orig != new:
            diffs.append({"field": label, "old": orig, "new": new})
    return diffs

# ── Ticket 14: Per-product async processing ───────────────────────────────
async def _process_product(product: dict, model: str, semaphore: asyncio.Semaphore) -> dict:
    """Run one product through all optimization stages with error isolation."""
    async with semaphore:
        from tools.registry import get
        from tools.taxonomy_tool import TaxonomyInput
        from tools.seo_tool import SEOInput
        from tools.enrichment_tool import EnrichmentInput
        from tools.kpi_tool import KPIInput
        from tools.description_tool import DescriptionInput

        result = dict(product)
        name = product["name"]
        sku  = product.get("sku", "")

        for label, coro_fn in [
            ("taxonomy",  lambda: get("taxonomy").execute(TaxonomyInput(product_name=name, model=model))),
            ("seo",       lambda: get("seo").execute(SEOInput(product_name=name, model=model))),
        ]:
            try:
                out = await coro_fn()
                result.update(out.model_dump())
            except Exception as e:
                result[f"{label}_error"] = str(e)

        try:
            out = await get("enrichment").execute(EnrichmentInput(
                product_name=name, subcategory=result.get("subcategory",""), sku=sku, model=model
            ))
            result["attributes"] = out.model_dump()
            result["completeness_score"] = out.completeness_score
        except Exception as e:
            result["enrichment_error"] = str(e)

        try:
            out = await get("kpi").execute(KPIInput(product_name=name, model=model))
            result["kpi"] = out.model_dump()
        except Exception as e:
            result["kpi_error"] = str(e)

        try:
            out = await get("description").execute(DescriptionInput(product_name=name, model=model))
            result["description"] = getattr(out, "description", str(out))
        except Exception as e:
            result["description_error"] = str(e)

        result["diffs"] = compute_diff(result)
        return result

# ── Ticket 11: Preview-aware pipeline entry point ─────────────────────────
async def stream_catalog_pipeline(
    products: list[dict],
    model: str = "gpt-4o-mini",
    run_id: str | None = None,
    mode: str = "preview",
) -> AsyncGenerator[str, None]:
    """
    Stream SSE events for a full catalog optimization run.
    mode='preview'  — diffs returned, nothing pushed to BigCommerce.
    mode='publish'  — caller reads final event results and pushes via bigcommerce_tool.
    """
    run_id = run_id or str(uuid.uuid4())
    normalized = [normalize_product(p) for p in products]
    total = len(normalized)

    yield AgentEvent(type="pipeline_started", run_id=run_id, content={"total": total, "mode": mode}).to_sse()

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [asyncio.create_task(_process_product(p, model, semaphore)) for p in normalized]
    results, done = [], 0

    for fut in asyncio.as_completed(tasks):
        try:
            res = await fut
        except Exception as e:
            res = {"error": str(e)}
        results.append(res)
        done += 1
        yield AgentEvent(type="pipeline_progress", run_id=run_id,
                         content={"completed": done, "total": total}).to_sse()

    yield AgentEvent(type="pipeline_completed", run_id=run_id,
                     content={"mode": mode, "results": results}).to_sse()