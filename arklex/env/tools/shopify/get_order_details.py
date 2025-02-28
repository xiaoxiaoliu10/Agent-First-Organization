import json
from typing import Any, Dict

import shopify

from arklex.env.tools.tools import register_tool
from arklex.env.tools.shopify.utils import authorify_admin
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
    ORDERS_NOT_FOUND
]

@register_tool(description, slots, outputs, lambda x: x not in errors)
def get_order_details(order_ids: list, limit=10, **kwargs) -> str:
    limit = int(limit) if limit else 10
    auth = authorify_admin(kwargs)
    if auth["error"]:
        return auth["error"]
    
    try:
        with shopify.Session.temp(**auth["value"]):
            response_text = ""
            for order_id in order_ids:
                response = shopify.GraphQL().execute(f"""
                {{
                    order (id: "{order_id}") {{
                        id
                        name
                        createdAt
                        cancelledAt
                        returnStatus
                        statusPageUrl
                        totalPriceSet {{
                            presentmentMoney {{
                                amount
                            }}
                        }}
                        fulfillments {{
                            displayStatus
                            trackingInfo {{
                                number
                                url
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
                response_text += f"Order ID: {parsed_response.get('id', 'None')}\n"
                response_text += f"Order Name: {parsed_response.get('name', 'None')}\n"
                response_text += f"Created At: {parsed_response.get('createdAt', 'None')}\n"
                response_text += f"Cancelled At: {parsed_response.get('cancelledAt', 'None')}\n"
                response_text += f"Return Status: {parsed_response.get('returnStatus', 'None')}\n"
                response_text += f"Status Page URL: {parsed_response.get('statusPageUrl', 'None')}\n"
                response_text += f"Total Price: {parsed_response.get('totalPriceSet', {}).get('presentmentMoney', {}).get('amount', 'None')}\n"
                response_text += f"Fulfillment Status: {parsed_response.get('fulfillments', 'None')}\n"
                response_text += "Line Items:\n"
                for item in parsed_response.get('lineItems', {}).get('edges', []):
                    response_text += f"    Title: {item.get('node', {}).get('title', 'None')}\n"
                    response_text += f"    Quantity: {item.get('node', {}).get('quantity', 'None')}\n"
                    response_text += f"    Variant ID: {item.get('node', {}).get('variant', {}).get('id', 'None')}\n"
                response_text += "\n"
        return response_text
    except Exception as e:
        return ORDERS_NOT_FOUND
