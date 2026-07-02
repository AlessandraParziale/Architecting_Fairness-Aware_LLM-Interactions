""" - Claude
"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def LLMJudge(judge_prompt: str) -> str:

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": judge_prompt
            }
        ]
    )

    return response.content[0].text


""" - GPT


import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def LLMJudge(judge_prompt: str) -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": judge_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
"""