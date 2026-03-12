import httpx

class BigCommerceClient:
    def __init__(self, store_hash: str, access_token: str):
        self.base_url = f"https://api.bigcommerce.com/stores/{store_hash}/v3"
        self.headers = {
            "X-Auth-Token": access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_product(self, product_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/catalog/products/{product_id}",
                headers=self.headers
            )
            resp.raise_for_status()
            return resp.json().get("data", {})

    async def update_product(self, product_id: int, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/catalog/products/{product_id}",
                headers=self.headers,
                json=payload
            )
            resp.raise_for_status()
            return resp.json().get("data", {})

    async def bulk_update_products(self, updates: list[dict]) -> list[dict]:
        results = []
        for update in updates:
            product_id = update.pop("id")
            result = await self.update_product(product_id, update)
            results.append(result)
        return results
