from tools.taxonomy_tool import TaxonomyInput
from tools.registry import get

async def classify(product_name: str, model: str = "gpt-4o-mini") -> dict:
    """Classify a product name into the store taxonomy."""
    result = await get("taxonomy").execute(TaxonomyInput(product_name=product_name, model=model))
    return result.model_dump()