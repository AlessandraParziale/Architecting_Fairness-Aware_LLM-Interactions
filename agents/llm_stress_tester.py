''' - GPT 
'''
import os

from openai import OpenAI
from dotenv import load_dotenv

from utils import load_text, fill_template

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def LLMStressTester(original_prompt: str, previous_prompt: str, previous_output: str) -> str:

    template = load_text(
        "prompts/stress_tester_prompt.txt"
    )

    stress_prompt = fill_template(
        template,
        {
            "ORIGINAL_PROMPT": original_prompt,
            "PREVIOUS_PROMPT": previous_prompt,
            "PREVIOUS_OUTPUT": previous_output
        }
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": stress_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()