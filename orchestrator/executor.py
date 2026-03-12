import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

async def execute_stream(step: str, model: str = "gpt-4o-mini"):
    stream = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"Execute this step concisely: {step}"}],
        stream=True
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""
