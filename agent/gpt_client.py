import re
from openai import OpenAI
from openai.types.chat import ChatCompletion

from config import settings


DEBUG_MODE = True

client = OpenAI(api_key=settings.openai_api_key)


def clean_gpt_response(text_response: str) -> str:
    text_response = re.sub(r"^```(json)?\n?", "", text_response)
    text_response = re.sub(r"\n?```$", "", text_response)
    return text_response


def ask_gpt(messages: list, model="gpt-4o", temperature=0.3) -> str:
    response: ChatCompletion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return clean_gpt_response(response.choices[0].message.content.strip())




