import json
import logging

import shopify

# general GraphQL navigation utilities
from arklex.env.tools.shopify.utils_nav import *
from arklex.env.tools.shopify.utils import authorify

# ADMIN
from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs
from arklex.env.tools.tools import register_tool

logger = logging.getLogger(__name__)

description = "Get the product image url of a product."
slots = [
    ShopifySlots.PRODUCT_IDS,
    *PAGEINFO_SLOTS
]
outputs = [
    ShopifyOutputs.PRODUCTS_DETAILS,
    *PAGEINFO_OUTPUTS
]
PRODUCTS_NOT_FOUND = "error: product not found"
errors = [PRODUCTS_NOT_FOUND]

@register_tool(description, slots, outputs, lambda x: x not in errors)
def get_product_images(product_ids: list, **kwargs) -> str:
    nav = cursorify(kwargs)
    if not nav[1]:
        return nav[0]
    auth = authorify(kwargs)
    if auth["error"]:
        return auth["error"]

    try:
        ids = ' OR '.join(f'id:{pid.split("/")[-1]}' for pid in product_ids)
        with shopify.Session.temp(**auth["value"]):
            response = shopify.GraphQL().execute(f"""
                {{
                    products ({nav[0]}, query:"{ids}") {{
                        nodes {{
                            title
                            images(first: 3) {{
                                edges {{
                                    node {{
                                        src
                                        altText
                                    }}
                                }}
                            }}
                        }}
                        pageInfo {{
                            endCursor
                            hasNextPage
                            hasPreviousPage
                            startCursor
                        }}
                    }}
                }}
            """)
            result = json.loads(response)['data']['products']
            response = result["nodes"]
            response_text = ""
            for i, product in enumerate(response):
                response_text += f"Product {i+1}:\n"
                response_text += f"Product Title: {product.get('title')}\n"
                response_text += f"Online Store URL: {product.get('onlineStoreUrl')}\n"
                images = product.get('images', {}).get('edges', [])
                for img in images:
                    response_text += f"Product Image URL: {img['node']['src']}\n"
                response_text += "\n"
            return response_text
    except Exception as e:
        return PRODUCTS_NOT_FOUND
