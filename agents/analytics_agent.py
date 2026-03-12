from tools.registry import get

async def analyze(product_name: str, model: str = "gpt-4o-mini") -> dict:
    """Generate KPI analytics for a product."""
    from tools.kpi_tool import KPIInput
    result = await get("kpi").execute(KPIInput(product_name=product_name, model=model))
    return result.model_dump()