"""
Ticket 19 — Automated catalog audit job.
Fetches live products and reports weak SEO and missing attributes.
Run manually or schedule with cron / APScheduler.
"""
import asyncio, os
from datetime import datetime, timezone
from tools.bigcommerce_connector import fetch_products
from evaluation.seo_eval import score_seo_title

SEO_THRESHOLD = 0.5

async def audit_catalog(limit: int = 250) -> dict:
    """Identify products with weak SEO titles or missing metadata."""
    products = await fetch_products(limit=limit)
    weak_seo, missing_attrs = [], []

    for p in products:
        name = p.get("name", "")
        page_title = p.get("page_title", "") or name
        seo = score_seo_title(name, page_title)
        if seo["score"] < SEO_THRESHOLD:
            weak_seo.append({"id": p.get("id"), "name": name, "seo_score": seo["score"]})
        missing = [f for f in ["description", "meta_description"] if not p.get(f, "").strip()]
        if missing:
            missing_attrs.append({"id": p.get("id"), "name": name, "missing": missing})

    n = max(len(products), 1)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "total_products": len(products),
        "weak_seo_count": len(weak_seo),
        "missing_attrs_count": len(missing_attrs),
        "health_score": round(1.0 - (len(weak_seo) + len(missing_attrs)) / (n * 2), 3),
        "weak_seo": weak_seo[:20],
        "missing_attrs": missing_attrs[:20],
    }

if __name__ == "__main__":
    r = asyncio.run(audit_catalog())
    print(f"Health: {r['health_score']}  total={r['total_products']}  "
          f"weak_seo={r['weak_seo_count']}  missing_attrs={r['missing_attrs_count']}")