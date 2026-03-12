import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def seo_agent(product_name: str, model: str = "llama-3.3-70b-versatile") -> str:
    prompt = f"""You are an SEO expert for an e-commerce store selling replacement parts.
Rewrite this product name to be more search-engine friendly. Keep it concise, clear, and include key search terms.
Original: {product_name}
Respond with only the improved name, nothing else."""
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
