"""Ticket 17 — SEO title quality evaluation."""

MIN_LEN, MAX_LEN = 30, 70

def score_seo_title(original: str, seo_title: str) -> dict:
    """Score a single SEO title on length, improvement, and capitalisation."""
    length   = len(seo_title.strip())
    length_ok = MIN_LEN <= length <= MAX_LEN
    is_improvement = (
        len(seo_title) > len(original)
        and seo_title.strip().lower() != original.strip().lower()
    )
    starts_upper = bool(seo_title) and seo_title[0].isupper()
    return {
        "length": length,
        "length_ok": length_ok,
        "is_improvement": is_improvement,
        "score": round(sum([length_ok, is_improvement, starts_upper]) / 3, 3),
    }

def evaluate_batch(pairs: list[dict]) -> dict:
    """Evaluate a list of {original, seo_name} dicts and return aggregate metrics."""
    scores = [score_seo_title(p["original"], p["seo_name"]) for p in pairs]
    n = max(len(scores), 1)
    return {
        "total": len(scores),
        "avg_score":        round(sum(s["score"]         for s in scores) / n, 3),
        "length_ok_rate":   round(sum(s["length_ok"]     for s in scores) / n, 3),
        "improvement_rate": round(sum(s["is_improvement"] for s in scores) / n, 3),
        "details": scores,
    }

if __name__ == "__main__":
    samples = [
        {"original": "Hex Bolt", "seo_name": "M8 Stainless Steel Hex Bolt Corrosion Resistant"},
        {"original": "V-Belt",   "seo_name": "A-Section V-Belt 36 Inch for Industrial Drives"},
        {"original": "Bearing",  "seo_name": "Deep Groove Ball Bearing 6203-2RS 17x40x12mm"},
    ]
    r = evaluate_batch(samples)
    print(f"Avg score: {r['avg_score']}  length OK: {r['length_ok_rate']}  improved: {r['improvement_rate']}")