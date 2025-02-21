import json
from typing import Any, Dict
import shopify

# general GraphQL navigation utilities
from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs
from arklex.env.tools.shopify.utils_nav import *
from arklex.env.tools.shopify.utils import authorify

# Admin API
from arklex.env.tools.tools import register_tool

description = "Search products by string query. If no products are found, the function will return an error message."
slots = [
    ShopifySlots.SEARCH_PRODUCT_QUERY,
    *PAGEINFO_SLOTS
] 
outputs = [
    ShopifyOutputs.PRODUCTS_LIST,
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

@register_tool(description, slots, outputs, lambda x: x[0] not in errors)
def search_products(product_query: str, **kwargs) -> str:
    nav = cursorify(kwargs)
    if not nav[1]:
        return nav[0]
    auth = authorify(kwargs)
    if auth["error"]:
        return auth["error"]
    
    try:
        with shopify.Session.temp(**auth["value"]):
            response = shopify.GraphQL().execute(f"""
                {{
                    products ({nav[0]}, query: "{product_query}") {{
                        nodes {{
                            id
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
            response_text = ""
            data = json.loads(response)['data']['products']
            nodes = data['nodes']
            for node in nodes:
                response_text += f"Product ID: {node['id']}\n"
            if response_text:
                return response_text
            else:
                return NO_PRODUCTS_FOUND_ERROR
    
    except Exception as e:
        return PRODUCT_SEARCH_ERROR