from litellm import completion
from openai import OpenAI
from agentorg.utils.model_config import MODEL
import json
SAFETY_RESPONSE = "I'm unable to respond to that. Please ask me another question."
PROMPT = f"""
        Carefully analyze the following text for hate speech, sexually suggestive content, harassment, and dangerous content.  Return a JSON object with a "safe" boolean (true if the text is completely safe, false otherwise) 

        JSON Response:
        {{
        "safe": true/false,
        "reason": "Explanation of why unsafe (if applicable)"  
        }}
        """

def model_safety_check(inputs):
    is_flagged = False
    if MODEL['llm_provider'] == 'openai':
        client = OpenAI()
        text = inputs["text"]
        moderation_response = client.moderations.create(input=text).model_dump()
        if moderation_response["results"][0]["flagged"]:
            return True, SAFETY_RESPONSE
    elif MODEL['llm_provider'] == 'gemini':
        response = completion(
            model=MODEL["model_type_or_path"],
            custom_llm_provider=MODEL["llm_provider"],
            messages=[
                    {"role": "system", "content": PROMPT}, {"role": "user", "content": inputs['text']}
                ],
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
            ],
             response_format={"type": "json_object"}
        )
  
        res = json.loads(response.choices[0].message.content)
        if not res['safe']:
            return True, SAFETY_RESPONSE
  
    return is_flagged, ""