import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SUBCATEGORIES = [
    "Ball Bearings", "Sealed Bearings", "Roller Bearings", "Thrust Bearings",
    "Drive Belts", "V-Belts", "Timing Belts", "Flat Belts", "Other"
]

def taxonomy_agent(product_name: str, model: str = "llama-3.3-70b-versatile") -> str:
    prompt = f"""You are a product taxonomy expert. Given this product name, assign it to exactly one subcategory.
Subcategories: {', '.join(SUBCATEGORIES)}
Product: {product_name}
Respond with only the subcategory name, nothing else."""
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
