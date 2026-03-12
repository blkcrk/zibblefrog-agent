import os
import httpx
from typing import AsyncIterator

STORE_HASH = os.environ["BIGCOMMERCE_STORE_HASH"]
ACCESS_TOKEN = os.environ["BIGCOMMERCE_ACCESS_TOKEN"]
BASE_URL = f"https://api.bigcommerce.com/stores/{STORE_HASH}/v3"

HEADERS = {
    "X-Auth-Token": ACCESS_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

async def fetch_products(limit: int = 250, page: int = 1) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/catalog/products",
            headers=HEADERS,
            params={"limit": limit, "page": page, "include": "variants"}
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

def bc_to_csv_row(product: dict) -> dict:
    return {
        "Location ID": 1,
        "Item": "Product",
        "Product ID": product.get("id"),
        "Variant ID": None,
        "Type": product.get("type", ""),
        "Weight": product.get("weight", 0),
        "Name": product.get("name", ""),
        "SKU": product.get("sku", ""),
        "Current Stock": product.get("inventory_level", 0),
        "Low Stock": product.get("inventory_warning_level", 0),
        "Price": product.get("price", 0),
        "Availability": str(product.get("availability", "available") == "available")
    }
