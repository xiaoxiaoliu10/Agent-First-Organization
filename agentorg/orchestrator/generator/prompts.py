generate_tasks_sys_prompt = """Given the type of the assistant the owner need, the introduction and the detailed documentation from owner (if available), your task is to figure out the tasks that this assistant need to handle in terms of user's intent. Return the answer in JSON format.

For Example:

Assistant Type: Customer Service Assistant
Owner's Information: Amazon.com is a large e-commerce platform that sells a wide variety of products, ranging from electronics to groceries.
Documentations: 
https://www.amazon.com/
Holiday Deals
Disability Customer Support
Same-Day Delivery
Medical Care
Customer Service
Amazon Basics
Groceries
Prime
Buy Again
New Releases
Pharmacy
Shop By Interest
Amazon Home
Amazon Business
Subscribe & Save
Livestreams
luwanamazon's Amazon.com
Best Sellers
Household, Health & Baby Care
Sell
Gift Cards

https://www.amazon.com/bestsellers
Any Department
Amazon Devices & Accessories
Amazon Renewed
Appliances
Apps & Games
Arts, Crafts & Sewing
Audible Books & Originals
Automotive
Baby
Beauty & Personal Care
Books
Camera & Photo Products
CDs & Vinyl
Cell Phones & Accessories
Clothing, Shoes & Jewelry
Collectible Coins
Computers & Accessories
Digital Educational Resources
Digital Music
Electronics
Entertainment Collectibles
Gift Cards
Grocery & Gourmet Food
Handmade Products
Health & Household
Home & Kitchen
Industrial & Scientific
Kindle Store
Kitchen & Dining
Movies & TV
Musical Instruments
Office Products
Patio, Lawn & Garden
Pet Supplies
Software
Sports & Outdoors
Sports Collectibles
Tools & Home Improvement
Toys & Games
Unique Finds
Video Games

Reasoning Process:
Thought 1: Understand the general responsibilities of the assistant type.
Observation 1: A customer service assistant typically handles tasks such as answering customer inquiries, addressing complaints, making product recommendations, assisting with orders, processing returns and exchanges, supporting billing and payments, and managing customer accounts.

Thought 2: Based on these general tasks, identify the specific tasks relevant to this assistant, taking into account the customer's decision-making journey. Consider the typical activities customers engage in on this platform and the potential questions they might ask.
Observation 2: The customer decision-making journey includes stages like need recognition, information search, evaluating alternatives, making a purchase decision, and post-purchase behavior. On Amazon, customers log in, browse and compare products, add items to their cart, and check out. They also track orders, manage returns, and leave reviews. Therefore, the assistant would handle tasks such as product search and discovery, product inquiries, product comparison, billing and payment support, order management, and returns and exchanges.

Thought 3: Summarize the identified tasks in terms of user intent and format them into JSON.
Observation 3: Structure the output as a list of dictionaries, where each dictionary represents an intent and its corresponding task.

Answer:
```json
[
    {{
        "intent": "product_search_and_discovery",
        "task": "Provide help in Product Search and Discovery"
    }},
    {{
        "intent": "product_inquiry",
        "task": "Provide help in product inquiry"
    }},
    {{
        "intent": "product_comparison",
        "task": "Provide help in product comparison"
    }},
    {{
        "intent": "billing_and_payment_support",
        "task": "Provide help in billing and payment support"
    }},
    {{
        "intent": "order_management",
        "task": "Provide help in order management"
    }},
    {{
        "intent": "returns_and_exchanges",
        "task": "Provide help in Returns and Exchanges"
    }}
]
```

Assistant Type: {role}
Owner's information: {intro}
Documentations: 
{docs}
Reasoning Process:
"""


generate_best_practice_sys_prompt = """Given the task that the assistant needs to handle, your task is to generate a step-by-step best practice for addressing this task. Each step should represent a clear interaction with the user. Return the answer in JSON format.

For example:
Task: Provide help in Product Search and Discovery
Thought: To help users find products effectively, the assistant should first get context information about the customer from CRM, such as purchase history, demographic information, preference metadata, inquire about specific preferences or requirements (e.g., brand, features, price range) specific for the request. Second, based on the user's input, the assistant should provide personalized product recommendations. Third, the assistant should ask if there is anything not meet their goals. Finally, the assistant should confirm the user's selection, provide additional information if needed, and assist with adding the product to the cart or wish list.
Answer:
```json
[
    {{
      "step": 1,
      "task": "Retrieve the information about the customer and Inquire about specific preferences or requirements (e.g., brand, features, price range)."
    }},
    {{
      "step": 2,
      "task": "Provide a curated list of products that match the user's criteria."
    }},
    {{
      "step": 3,
      "task": "Ask if the user would like to see more options or has any specific preferences."
    }},
    {{
      "step": 4,
      "task": "Confirm if the user is ready to proceed with a purchase or needs more help."
    }},
    {{
      "step": 5,
      "task": "Provide instructions for completing the purchase or next steps."
    }}
]
```

Task: {task}
"""


finetune_best_practice_sys_prompt = """Given the best practice for addressing a specific task, the available resources and other objectives of the task, your task is to fine-tune the steps to make them only make use of the available resources and embed the objectives. The return answer need to include the resources used for each step and the example response if needed. Return the answer in JSON format.

For example:
Best Practice: 
[
    {{
        "step": 1,
        "task": "Retrieve the information about the customer and Inquire about specific preferences or requirements (e.g., brand, features, price range)."
    }},
    {{
        "step": 2,
        "task": "Provide a curated list of products that match the user's criteria."
    }},
    {{
        "step": 3,
        "task": "Ask if the user would like to see more options or has any specific preferences."
    }},
    {{
        "step": 4,
        "task": "Confirm if the user is ready to proceed with a purchase or needs more help."
    }},
    {{
        "step": 5,
        "task": "Provide instructions for completing the purchase or next steps."
    }}
]
Resources:
{{
    "MessageAgent": "The agent responsible for interacting with the user with predefined responses",
    "RAGAgent": "Answer the user's questions based on the company's internal documentations, such as the policies, FAQs, and product information",
    "ProductAgent": "Access the company's database to retrieve information about products, such as availability, pricing, and specifications",
    "UserProfileAgent": "Access the company's database to retrieve information about the user's preferences and history"
}}
Objectives:
[
    "Sign up the Prime membership"
]
Answer:
```json
[
    {{
        "step": 1,
        "task": "Retrieve the information about the customer from CRM and Inquire about specific preferences or requirements (e.g., brand, features, price range)."
        "resource": "UserProfileAgent",
        "example_response": "Do you have some specific preferences or requirements for the product you are looking for?"
    }},
    {{
        "step": 2,
        "task": "Provide a curated list of products that match the user's criteria."
        "resource": "ProductAgent",
        "example_response": "Here are some products that match your preferences."
    }},
    {{
        "step": 3,
        "task": "Ask if the user would like to see more options or has any specific preferences."
        "resource": "MessageAgent",
        "example_response": "Would you like to see more options or do you have any specific preferences?"
    }},
    {{
        "step": 4,
        "task": "Confirm if the user is ready to proceed with a purchase or needs more help."
        "resource": "MessageAgent",
        "example_response": "Are you ready to proceed with the purchase or do you need more help?"
    }},
    {{
        "step": 5,
        "task": "Persuade the user to sign up for the Prime membership."
        "resource": "MessageAgent",
        "example_response": "I noticed that you are a frequent shopper. Have you considered signing up for our Prime membership to enjoy exclusive benefits and discounts?"
    }}
]
```

Best Practice: {best_practice}
Resources: {resources}
Objectives: {objectives}
Answer:
"""