from tools.seo_tool import SEOInput
from tools.registry import get

async def optimize(product_name: str, model: str = "gpt-4o-mini") -> dict:
    """Generate SEO-optimized title for a product."""
    result = await get("seo").execute(SEOInput(product_name=product_name, model=model))
    return result.model_dump()