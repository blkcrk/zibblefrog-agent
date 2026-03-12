import os
from openai import AsyncOpenAI
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from prompts.loader import load_prompt

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

class DescriptionInput(ToolInput):
    product_name: str
    subcategory: str
    sku: str = ""
    model: str = "gpt-4o-mini"

class DescriptionOutput(ToolOutput):
    description: str

class DescriptionTool(BaseTool):
    name = "description"
    description = "Generates an AI-friendly product description"
    input_model = DescriptionInput
    output_model = DescriptionOutput

    async def execute(self, input: DescriptionInput) -> DescriptionOutput:
        prompt = load_prompt("description").format(
            product_name=input.product_name,
            subcategory=input.subcategory,
            sku=input.sku
        )
        resp = await client.chat.completions.create(
            model=input.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return DescriptionOutput(description=resp.choices[0].message.content.strip())

register(DescriptionTool())
