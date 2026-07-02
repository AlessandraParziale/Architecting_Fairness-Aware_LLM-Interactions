""" - Claude
"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def LLMUser(user_prompt: str) -> str:

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=(
            "Provide a concise response. "
            "Do not ask follow-up questions. "
            "Use at most 3-4 sentences."
        ),
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.content[0].text.strip()


""" - GPT

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def LLMUser(user_prompt: str) -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Provide a concise response. "
                    "Do not ask follow-up questions. "
                    "Use at most 3-4 sentences."
                )
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content
"""