import os
from openai import AsyncOpenAI
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from prompts.loader import load_prompt

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

class SEOInput(ToolInput):
    product_name: str
    model: str = "gpt-4o-mini"

class SEOOutput(ToolOutput):
    seo_name: str

class SEOTool(BaseTool):
    name = "seo"
    description = "Rewrites a product name for SEO"
    input_model = SEOInput
    output_model = SEOOutput

    async def execute(self, input: SEOInput) -> SEOOutput:
        prompt = load_prompt("seo").format(product_name=input.product_name)
        resp = await client.chat.completions.create(
            model=input.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return SEOOutput(seo_name=resp.choices[0].message.content.strip())

register(SEOTool())
