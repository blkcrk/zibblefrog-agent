import os
import pandas as pd
from io import StringIO
from .taxonomy import taxonomy_agent
from .seo import seo_agent
from .kpi import kpi_agent

def process_csv(csv_content: str, model: str = "llama-3.3-70b-versatile") -> str:
    df = pd.read_csv(StringIO(csv_content))
    results = []
    for _, row in df.iterrows():
        name = str(row.get('Name', ''))
        subcategory = taxonomy_agent(name, model)
        seo_name = seo_agent(name, model)
        kpi = kpi_agent(name, seo_name, subcategory, model)
        results.append({**row.to_dict(), 'Suggested_Category': subcategory, 'SEO_Name': seo_name, 'Expected_KPI': kpi})
    return pd.DataFrame(results).to_csv(index=False)
