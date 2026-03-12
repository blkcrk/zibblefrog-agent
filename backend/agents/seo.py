import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def seo_agent(product_name: str, model: str = "gpt-4o-mini") -> str:
    prompt = f"You are an SEO expert for an e-commerce store selling replacement parts. Rewrite this product name to be more search-engine friendly. Keep it concise, clear, and include key search terms.\nOriginal: {product_name}\nRespond with only the improved name, nothing else."
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
