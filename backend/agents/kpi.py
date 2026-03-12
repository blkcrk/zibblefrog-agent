import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def kpi_agent(original_name: str, seo_name: str, subcategory: str, model: str = "llama-3.3-70b-versatile") -> str:
    prompt = f"""You are an e-commerce KPI analyst. Given an original product name, an improved SEO name, and a subcategory,
estimate the expected KPI improvements in a single concise sentence covering CTR, search ranking, and conversion potential.
Original: {original_name}
SEO Name: {seo_name}
Subcategory: {subcategory}
Respond with one sentence only."""
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
