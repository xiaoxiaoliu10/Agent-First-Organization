import json
from typing import Any, Dict

import shopify

from arklex.env.tools.tools import register_tool
from arklex.env.tools.shopify.utils import SHOPIFY_AUTH_ERROR
from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs

description = "Get the status and details of an order."
slots = [
    ShopifySlots.ORDERS_ID,
    ShopifySlots.QUERY_LIMIT
]
outputs = [
    ShopifyOutputs.ORDERS_DETAILS
]
ORDERS_NOT_FOUND = "error: order not found"
errors = [
    SHOPIFY_AUTH_ERROR, 
    ORDERS_NOT_FOUND
]

@register_tool(description, slots, outputs, lambda x: x not in errors)
def get_order_details(order_ids: list, limit=10, **kwargs) -> str:
    limit = int(limit) if limit else 10
    shop_url = kwargs.get("shop_url")
    api_version = kwargs.get("api_version")
    token = kwargs.get("token")

    if not shop_url or not api_version or not token:
        return SHOPIFY_AUTH_ERROR
    
    try:
        with shopify.Session.temp(shop_url, api_version, token):
            results = []
            for order_id in order_ids:
                response = shopify.GraphQL().execute(f"""
                {{
                    order (id: "{order_id}") {{
                        id
                        name
                        totalPriceSet {{
                            presentmentMoney {{
                                amount
                            }}
                        }}
                        lineItems(first: 10) {{
                            edges {{
                                node {{
                                    id
                                    title
                                    quantity
                                    variant {{
                                        id
                                        product {{
                                            id
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                """)
                parsed_response = json.loads(response)["data"]["order"]
                results.append(json.dumps(parsed_response))
        return json.dumps(results)
    except Exception as e:
        print(e)
        return ORDERS_NOT_FOUND
