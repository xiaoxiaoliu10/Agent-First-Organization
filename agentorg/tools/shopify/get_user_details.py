import json
from typing import Any, Dict
import shopify

from agentorg.tools.tools import register_tool

description = "Get the details of a user."
slots = [
    {
        "name": "user_id",
        "type": "string",
        "description": "The user id, such as 'gid://shopify/Customer/13573257450893'.",
        "prompt": "In order to proceed, Could you please provide the user id?",
        "required": True,
    }
]
outputs = [
    {
        "name": "user_details",
        "type": "dict",
        "description": "The user details of the user. such as '{\"firstName\": \"John\", \"lastName\": \"Doe\", \"email\": \"example@gmail.com\"}'."
    }
]

@register_tool(description, slots, outputs)
def get_user_details(user_id: str) -> str:
    try:
        response = shopify.GraphQL().execute(f"""
        {{
            customer(id: "{user_id}") {{
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
                orders (first: 10) {{
                    edges {{
                        node {{
                            id         
                        }}
                    }}
                }}
            }}
        }}
        """)
        parsed_response = json.loads(response)["data"]["customer"]
        return json.dumps(parsed_response)
    except Exception as e:
        print("error: user not found")
        print(e)
        return "error: user not found"
