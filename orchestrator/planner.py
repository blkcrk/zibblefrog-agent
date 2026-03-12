import os
from openai import AsyncOpenAI
from prompts.loader import load_prompt

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

async def plan(goal: str, model: str = "gpt-4o-mini") -> list[str]:
    prompt = load_prompt("planner").format(goal=goal)
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.choices[0].message.content
    return [l.strip() for l in text.strip().splitlines() if l.strip()]

async def plan_stream(goal: str, model: str = "gpt-4o-mini"):
    prompt = load_prompt("planner").format(goal=goal)
    stream = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""
