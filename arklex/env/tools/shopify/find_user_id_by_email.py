from typing import Any, Dict
import json

import shopify

from arklex.env.tools.tools import register_tool
from arklex.env.tools.shopify.utils import SHOPIFY_AUTH_ERROR
from arklex.env.tools.shopify.utils_slots import ShopifySlots

description = "Find user id by email. If the user is not found, the function will return an error message."
slots = [
    ShopifySlots.USER_EMAIL
]
outputs = [
    ShopifySlots.USER_ID
]

USER_NOT_FOUND_ERROR = "error: user not found"
MULTIPLE_USERS_SAME_EMAIL_ERROR = "error: there are multiple users with the same email"
errors = [
    SHOPIFY_AUTH_ERROR,
    USER_NOT_FOUND_ERROR,
    MULTIPLE_USERS_SAME_EMAIL_ERROR
]

@register_tool(description, slots, outputs, lambda x: x not in errors)
def find_user_id_by_email(user_email: str, **kwargs) -> str:
    shop_url = kwargs.get("shop_url")
    api_version = kwargs.get("api_version")
    token = kwargs.get("token")
    
    if not shop_url or not api_version or not token:
        return SHOPIFY_AUTH_ERROR
    
    user_id = ""
    
    try:
        with shopify.Session.temp(shop_url, api_version, token):
            response = shopify.GraphQL().execute(f"""
                {{
                    customers (first: 10, query: "email:{user_email}") {{
                        edges {{
                            node {{
                                id
                            }}
                        }}
                    }}
                }}
                """)
        nodes = json.loads(response)["data"]["customers"]["edges"]
        if len(nodes) == 1:
            user_id = nodes[0]["node"]["id"]
            return user_id
        else:
            return MULTIPLE_USERS_SAME_EMAIL_ERROR
    except Exception as e:
        return USER_NOT_FOUND_ERROR