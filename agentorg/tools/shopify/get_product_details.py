import json
from typing import Any, Dict

import shopify

from agentorg.tools.tools import register_tool

description = "Get the inventory information and description details of a product."
slots = [
    {
        "name": "product_ids",
        "type": "array",
        "items": {"type": "string"},
        "description": "The product id, such as 'gid://shopify/Product/2938501948327'. If there is only 1 product, return in list with single item. If there are multiple product ids, please return all of them in a list.",
        "prompt": "In order to proceed, please provide the product id.",
        "required": True,
    }
]
outputs = [
    {
        "name": "product_details",
        "type": "dict",
        "description": "The product details of the product. such as '{\"id\": \"gid://shopify/Product/2938501948327\", \"title\": \"Product 1\", \"description\": \"This is a product description.\"}'.",
    }
]

@register_tool(description, slots, outputs)
def get_product_details(product_ids: list) -> str:
    try:
        results = []
        for product_id in product_ids:
            response = shopify.GraphQL().execute(f"""
            {{
                product (id: "{product_id}") {{
                    id
                    title
                    description
                    totalInventory
                }}
            }}
            """)
            parsed_response = json.loads(response)["data"]["product"]
            results.append(json.dumps(parsed_response))
        return results
    except Exception as e:
        return "error: product not found"
