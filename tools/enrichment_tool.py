import os, json
from openai import AsyncOpenAI
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from prompts.loader import load_prompt

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

class EnrichmentInput(ToolInput):
    product_name: str
    subcategory: str = ""
    sku: str = ""
    model: str = "gpt-4o-mini"

class EnrichmentOutput(ToolOutput):
    material: str = ""
    compatibility: str = ""
    condition: str = ""
    specifications: str = ""
    completeness_score: float = 0.0

class EnrichmentTool(BaseTool):
    name = "enrichment"
    description = "Generates structured product attributes from name, category, and SKU"
    input_model = EnrichmentInput
    output_model = EnrichmentOutput

    async def execute(self, input: EnrichmentInput) -> EnrichmentOutput:
        prompt = load_prompt("enrichment").format(
            product_name=input.product_name,
            subcategory=input.subcategory,
            sku=input.sku,
        )
        resp = await client.chat.completions.create(
            model=input.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        filled = sum(1 for v in data.values() if v and str(v).strip())
        score = round(filled / max(len(data), 1), 2)
        return EnrichmentOutput(
            material=data.get("material", ""),
            compatibility=data.get("compatibility", ""),
            condition=data.get("condition", ""),
            specifications=str(data.get("specifications", "")),
            completeness_score=score,
        )

enrichment_tool = EnrichmentTool()
register(enrichment_tool)