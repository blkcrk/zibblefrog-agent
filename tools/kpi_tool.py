import os
from openai import AsyncOpenAI
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from prompts.loader import load_prompt

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

class KPIInput(ToolInput):
    original_name: str
    seo_name: str
    subcategory: str
    model: str = "gpt-4o-mini"

class KPIOutput(ToolOutput):
    kpi_summary: str

class KPITool(BaseTool):
    name = "kpi"
    description = "Estimates KPI improvements for a product rename"
    input_model = KPIInput
    output_model = KPIOutput

    async def execute(self, input: KPIInput) -> KPIOutput:
        prompt = load_prompt("kpi").format(
            original_name=input.original_name,
            seo_name=input.seo_name,
            subcategory=input.subcategory
        )
        resp = await client.chat.completions.create(
            model=input.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return KPIOutput(kpi_summary=resp.choices[0].message.content.strip())

register(KPITool())
