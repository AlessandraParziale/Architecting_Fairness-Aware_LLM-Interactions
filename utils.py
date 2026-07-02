import json
from string import Template

from pypdf import PdfReader


def load_text(path: str) -> str:
    """
    Reads a text file and returns its content.
    Used to load prompts and ethical guidelines.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def fill_template(template: str, values: dict) -> str:
    """
    Replaces placeholders inside a prompt template.
    """
    return Template(template).safe_substitute(values)




import json
import re

def parse_output(raw_output: str) -> dict:
    cleaned_output = raw_output.strip()

    cleaned_output = (
        cleaned_output
        .replace("“", "\"")
        .replace("”", "\"")
        .replace("‘", "'")
        .replace("’", "'")
    )

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output.removeprefix("```json").strip()

    if cleaned_output.startswith("```"):
        cleaned_output = cleaned_output.removeprefix("```").strip()

    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output.removesuffix("```").strip()

    try:
        return json.loads(cleaned_output)

    except json.JSONDecodeError:

        # Repair common LLM JSON mistakes
        repaired_output = cleaned_output

        # Fix: "evidence": "A" and "B"
        repaired_output = re.sub(
            r'"\s+and\s+"',
            '; ',
            repaired_output
        )

        try:
            print("WARNING: repaired malformed JSON")
            return json.loads(repaired_output)

        except json.JSONDecodeError:
            raise ValueError(
                f"Judge did not return valid JSON:\n{raw_output}"
            )
    
    
def load_pdf(path: str) -> str:
    """
    Reads a PDF file and returns its extracted text.
    """

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text