import json
from typing import Any, Dict
import shopify

# general GraphQL navigation utilities
from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs
from arklex.env.tools.shopify.utils_nav import *
from arklex.env.tools.shopify.utils import authorify_admin

# Admin API
from arklex.env.tools.tools import register_tool

description = "Search products by string query. If no products are found, the function will return an error message."
slots = [
    ShopifySlots.SEARCH_PRODUCT_QUERY,
    *PAGEINFO_SLOTS
] 
outputs = [
    ShopifyOutputs.PRODUCT_ID,
    *PAGEINFO_OUTPUTS
]
PRODUCT_SEARCH_ERROR = "error: product search failed"
NO_PRODUCTS_FOUND_ERROR = "no products found"

errors = [
    PRODUCT_SEARCH_ERROR,
    NO_PRODUCTS_FOUND_ERROR,
    NAVIGATE_WITH_NO_CURSOR,
    NO_NEXT_PAGE,
    NO_PREV_PAGE
]

@register_tool(description, slots, outputs, lambda x: x[0] not in errors, True)
def search_products(product_query: str, **kwargs) -> str:
    nav = cursorify(kwargs)
    if not nav[1]:
        return nav[0]
    auth = authorify_admin(kwargs)
    if auth["error"]:
        return auth["error"]
    
    try:
        with shopify.Session.temp(**auth["value"]):
            response = shopify.GraphQL().execute(f"""
                {{
                    products ({nav[0]}, query: "{product_query}") {{
                        nodes {{
                            id
                            title
                            description
                            onlineStoreUrl
                            images(first: 1) {{
                                edges {{
                                    node {{
                                        src
                                        altText
                                    }}
                                }}
                            }}
                            variants (first: 3) {{
                                nodes {{
                                    displayName
                                    id
                                    price
                                    inventoryQuantity
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
            answer = "Here are some products I found:\n"
            products = json.loads(response)['data']['products']['nodes']
            product_list = []
            for product in products:
                product_dict = {
                    "id": product.get('id'),
                    "title": product.get('title'),
                    "description": product.get('description'),
                    "product_url": product.get('onlineStoreUrl'),
                    "image_url": product.get('images', {}).get('edges', [{}])[0].get('node', {}).get('src', ""), 
                    "variants": product.get('variants', {}).get('nodes', [])
                }
                product_list.append(product_dict)
            if product_list:
                return json.dumps({
                    "answer": answer,
                    "product_list": product_list
                })
            else:
                return json.dumps({
                    "answer": NO_PRODUCTS_FOUND_ERROR,
                    "product_list": []
                })
    
    except Exception as e:
        return json.dumps({
            "answer": NO_PRODUCTS_FOUND_ERROR,
            "product_list": []
        })