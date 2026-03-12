from tools.enrichment_tool import EnrichmentInput
from tools.registry import get

async def enrich(
    product_name: str,
    subcategory: str = "",
    sku: str = "",
    model: str = "gpt-4o-mini",
) -> dict:
    """Generate structured attribute data for a product."""
    result = await get("enrichment").execute(
        EnrichmentInput(product_name=product_name, subcategory=subcategory, sku=sku, model=model)
    )
    return result.model_dump()