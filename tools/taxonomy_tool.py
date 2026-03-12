import os
from openai import AsyncOpenAI
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from prompts.loader import load_prompt

SUBCATEGORIES = [
    "Ball Bearings", "Sealed Bearings", "Roller Bearings", "Thrust Bearings",
    "Drive Belts", "V-Belts", "Timing Belts", "Flat Belts", "Other"
]

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

class TaxonomyInput(ToolInput):
    product_name: str
    model: str = "gpt-4o-mini"

class TaxonomyOutput(ToolOutput):
    subcategory: str

class TaxonomyTool(BaseTool):
    name = "taxonomy"
    description = "Assigns a product to a subcategory"
    input_model = TaxonomyInput
    output_model = TaxonomyOutput

    async def execute(self, input: TaxonomyInput) -> TaxonomyOutput:
        prompt = load_prompt("taxonomy").format(
            subcategories=", ".join(SUBCATEGORIES),
            product_name=input.product_name
        )
        resp = await client.chat.completions.create(
            model=input.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return TaxonomyOutput(subcategory=resp.choices[0].message.content.strip())

register(TaxonomyTool())
