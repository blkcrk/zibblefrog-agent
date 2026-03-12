import os
import pandas as pd
from io import StringIO
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SUBCATEGORIES = [
    "Ball Bearings", "Sealed Bearings", "Roller Bearings", "Thrust Bearings",
    "Drive Belts", "V-Belts", "Timing Belts", "Flat Belts", "Other"
]

def process_csv_stream(csv_content: str, model: str = "gpt-4o-mini"):
    df = pd.read_csv(StringIO(csv_content))
    results = []
    for i, row in df.iterrows():
        name = str(row.get('Name', ''))

        # Taxonomy
        tax_prompt = f"You are a product taxonomy expert. Assign to one subcategory.\nSubcategories: {', '.join(SUBCATEGORIES)}\nProduct: {name}\nRespond with only the subcategory name."
        tax_resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": tax_prompt}])
        subcategory = tax_resp.choices[0].message.content.strip()
        yield {"type": "dialogue", "product": name, "agent": "taxonomy", "input": tax_prompt, "output": subcategory}

        # SEO
        seo_prompt = f"Rewrite this product name for SEO. Be concise and include key search terms.\nOriginal: {name}\nRespond with only the improved name."
        seo_resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": seo_prompt}])
        seo_name = seo_resp.choices[0].message.content.strip()
        yield {"type": "dialogue", "product": name, "agent": "seo", "input": seo_prompt, "output": seo_name}

        # KPI
        kpi_prompt = f"Estimate KPI improvements in one sentence.\nOriginal: {name}\nSEO Name: {seo_name}\nSubcategory: {subcategory}"
        kpi_resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": kpi_prompt}])
        kpi = kpi_resp.choices[0].message.content.strip()
        yield {"type": "dialogue", "product": name, "agent": "kpi", "input": kpi_prompt, "output": kpi}

        results.append({**row.to_dict(), 'Suggested_Category': subcategory, 'SEO_Name': seo_name, 'Expected_KPI': kpi})
        yield {"type": "progress", "current": i + 1, "total": len(df)}

    yield {"type": "complete", "csv": pd.DataFrame(results).to_csv(index=False)}
