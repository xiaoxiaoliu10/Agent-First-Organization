from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

PROVIDER_MAP = {
    "anthropic": ChatAnthropic,
    "gemini": ChatGoogleGenerativeAI,
    "openai": ChatOpenAI  
}