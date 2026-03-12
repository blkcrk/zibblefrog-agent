import os
from typing import Literal
from tools.base import BaseTool, ToolInput, ToolOutput
from tools.registry import register
from integrations.bigcommerce_client import BigCommerceClient

client = BigCommerceClient(
    store_hash=os.environ["BIGCOMMERCE_STORE_HASH"],
    access_token=os.environ["BIGCOMMERCE_ACCESS_TOKEN"]
)

class BCPublishInput(ToolInput):
    updates: list[dict]
    mode: Literal["preview", "publish"] = "preview"

class BCDiff(ToolOutput):
    product_id: int
    field: str
    old_value: str
    new_value: str

class BCPublishOutput(ToolOutput):
    mode: str
    diffs: list[dict]
    published: int = 0
    errors: list[str] = []

class BigCommerceTool(BaseTool):
    name = "bigcommerce"
    description = "Preview or publish catalog changes to BigCommerce"
    input_model = BCPublishInput
    output_model = BCPublishOutput

    async def execute(self, input: BCPublishInput) -> BCPublishOutput:
        diffs = []
        errors = []
        published = 0

        for update in input.updates:
            product_id = update.get("Product ID")
            if not product_id:
                continue
            try:
                current = await client.get_product(int(product_id))
                row_diffs = []

                field_map = {
                    "SEO_Name": "name",
                    "AI_Description": "description",
                    "Suggested_Category": "meta_keywords"
                }

                for csv_field, bc_field in field_map.items():
                    new_val = update.get(csv_field, "")
                    old_val = str(current.get(bc_field, ""))
                    if new_val and new_val != old_val:
                        row_diffs.append({
                            "product_id": product_id,
                            "field": bc_field,
                            "old_value": old_val,
                            "new_value": new_val
                        })

                diffs.extend(row_diffs)

                if input.mode == "publish" and row_diffs:
                    payload = {d["field"]: d["new_value"] for d in row_diffs}
                    await client.update_product(int(product_id), payload)
                    published += 1

            except Exception as e:
                errors.append(f"Product {product_id}: {str(e)}")

        return BCPublishOutput(
            mode=input.mode,
            diffs=diffs,
            published=published,
            errors=errors
        )

register(BigCommerceTool())
