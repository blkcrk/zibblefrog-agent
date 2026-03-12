"""Ticket 17 — Taxonomy accuracy evaluation against labelled fixture data."""
from typing import Callable, Awaitable

FIXTURES = [
    ("6203-2RS Deep Groove Ball Bearing 17x40x12mm", "Ball Bearings"),
    ("608-ZZ Sealed Miniature Ball Bearing 8x22x7mm", "Sealed Bearings"),
    ("NU205 Cylindrical Roller Bearing", "Roller Bearings"),
    ("51104 Thrust Ball Bearing 20x35x10mm", "Thrust Bearings"),
    ("A-B Section V-Belt 36 inch", "V-Belts"),
    ("HTD 5M Synchronous Timing Belt 25mm wide", "Timing Belts"),
    ("Industrial Flat Drive Belt Neoprene 50mm", "Flat Belts"),
]

async def evaluate(classify_fn: Callable[[str], Awaitable[dict]]) -> dict:
    """Score taxonomy accuracy. classify_fn: async (name) -> dict with 'subcategory'."""
    correct, failures = 0, []
    for product_name, expected in FIXTURES:
        result = await classify_fn(product_name)
        predicted = result.get("subcategory", "")
        if predicted.strip().lower() == expected.strip().lower():
            correct += 1
        else:
            failures.append({"product": product_name, "expected": expected, "predicted": predicted})
    total = len(FIXTURES)
    return {"total": total, "correct": correct, "accuracy": round(correct / total, 3), "failures": failures}

if __name__ == "__main__":
    import asyncio
    from agents.taxonomy_agent import classify
    r = asyncio.run(evaluate(classify))
    print(f"Accuracy: {r['accuracy']*100:.1f}%  ({r['correct']}/{r['total']})")
    for f in r["failures"]:
        print(f"  FAIL  {f['product']!r}  expected={f['expected']!r}  got={f['predicted']!r}")