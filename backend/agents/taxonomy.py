import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SUBCATEGORIES = [
    "Ball Bearings", "Sealed Bearings", "Roller Bearings", "Thrust Bearings",
    "Drive Belts", "V-Belts", "Timing Belts", "Flat Belts", "Other"
]

def taxonomy_agent(product_name: str, model: str = "gpt-4o-mini") -> str:
    prompt = f"You are a product taxonomy expert. Given this product name, assign it to exactly one subcategory.\nSubcategories: {', '.join(SUBCATEGORIES)}\nProduct: {product_name}\nRespond with only the subcategory name, nothing else."
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
