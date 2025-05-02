"""import os
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
    return clean_gpt_response(response.choices[0].message.content.strip())"""

import os
import re
from openai import OpenAI
from openai.types.chat import ChatCompletion
import requests
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


def ask_huggingface(messages: list) -> str:
    prompt = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
    headers = {"Authorization": f"Bearer {settings.huggingface_token}"}
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers=headers,
        json={"inputs": prompt}
    )
    result = response.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return "מצטער, לא הצלחתי להבין."



