from typing import Any, Dict
import json

from arklex.env.tools.tools import register_tool

from arklex.env.tools.shopify.utils_slots import ShopifySlots, ShopifyOutputs
from arklex.env.tools.shopify.utils_nav import *
from arklex.env.tools.shopify.utils import authorify

# Admin API
import shopify

description = "Get the details of a user with Admin API."
slots = [
    ShopifySlots.USER_ID,
    *PAGEINFO_SLOTS
]
outputs = [
    ShopifyOutputs.USER_DETAILS,
    *PAGEINFO_OUTPUTS
]

USER_NOT_FOUND_ERROR = "error: user not found"
errors = [USER_NOT_FOUND_ERROR]


@register_tool(description, slots, outputs, lambda x: x not in errors)
def get_user_details_admin(user_id: str, **kwargs) -> str:
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
                    customer(id: "{user_id}")  {{ 
                        firstName
                        lastName
                        email
                        phone
                        numberOfOrders
                        amountSpent {{
                            amount
                            currencyCode
                        }}
                        createdAt
                        updatedAt
                        note
                        verifiedEmail
                        validEmailAddress
                        tags
                        lifetimeDuration
                        defaultAddress {{
                            formattedArea
                            address1
                        }}
                        addresses {{
                            address1
                        }}
                        orders ({nav[0]}) {{
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
                }}
            """)
            data = json.loads(response)['data']['customer']
            response_text = f"User: {data.get('firstName')} {data.get('lastName')}\n"
            response_text += f"Email: {data.get('email')}\n"
            response_text += f"Phone: {data.get('phone')}\n"
            response_text += f"Number of Orders: {data.get('numberOfOrders')}\n"
            response_text += f"Amount Spent: {data['amountSpent']['amount']} {data['amountSpent']['currencyCode']}\n"
            response_text += f"Created At: {data.get('createdAt')}\n"
            response_text += f"Updated At: {data.get('updatedAt')}\n"
            for order in data.get('orders').get('nodes'):
                response_text += f"Order ID: {order.get('id')}\n"
            return response_text

    except Exception:
        return USER_NOT_FOUND_ERROR