import json
from typing import Any, Dict
import shopify

# general GraphQL navigation utilities
from arklex.env.tools.shopify.utils_nav import *
from arklex.env.tools.shopify.utils import authorify_admin
from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs

from arklex.env.tools.tools import register_tool

description = "Search collections by string query. If no collections are found, the function will return an error message."
slots = [
    ShopifySlots.SEARCH_COLLECTION_QUERY,
    *PAGEINFO_SLOTS
]
outputs = [
    ShopifyOutputs.COLLECTIONS_DETAILS,
    *PAGEINFO_OUTPUTS
]
COLLECTION_SEARCH_ERROR = "error: collection search failed"
NO_COLLECTIONS_FOUND_ERROR = "no collections found"

errors = [
    COLLECTION_SEARCH_ERROR,
    NO_COLLECTIONS_FOUND_ERROR,
    NAVIGATE_WITH_NO_CURSOR,
    NO_NEXT_PAGE,
    NO_PREV_PAGE
]

@register_tool(description, slots, outputs, lambda x: x[0] not in errors, True)
def search_collections(collection_query: str, **kwargs) -> str:
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
                    collections ({nav[0]}, query: "{collection_query}") {{
                        nodes {{
                            title
                            description
                            productsCount {{
                                count
                            }}
                            products (first: 5) {{
                                nodes {{
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
            answer = "Here are some recommended products:\n"
            data = json.loads(response)['data']['collections']
            nodes = data['nodes']
            product_list = []
            for node in nodes:
                products = node.get('products').get('nodes')
                for product in products:
                    product_dict = {
                        "title": product.get('title'),
                        "description": product.get('description'),
                        "product_url": product.get('onlineStoreUrl'),
                        "image_url": product.get('images', {}).get('edges', [{}])[0].get('node', {}).get('src', ""),
                    }
                    product_list.append(product_dict)
            if product_list:
                return json.dumps({
                    "answer": answer,
                    "product_list": product_list
                }) 
            else:
                return json.dumps({
                    "answer": NO_COLLECTIONS_FOUND_ERROR,
                    "product_list": []
                })
    
    except Exception as e:
        return json.dumps({
            "answer": COLLECTION_SEARCH_ERROR,
            "product_list": []
        })