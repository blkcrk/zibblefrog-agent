import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def kpi_agent(original_name: str, seo_name: str, subcategory: str, model: str = "gpt-4o-mini") -> str:
    prompt = f"You are an e-commerce KPI analyst. Given an original product name, an improved SEO name, and a subcategory, estimate the expected KPI improvements in a single concise sentence covering CTR, search ranking, and conversion potential.\nOriginal: {original_name}\nSEO Name: {seo_name}\nSubcategory: {subcategory}\nRespond with one sentence only."
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
