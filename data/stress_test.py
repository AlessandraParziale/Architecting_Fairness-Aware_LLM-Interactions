import json
import os
import pandas as pd

from agents.llm_stress_tester import LLMStressTester
from utils import load_text, fill_template, parse_output
from agents.llm_user import LLMUser
from agents.llm_judge import LLMJudge
from agents.llm_refiner import LLMRefiner


MAX_ATTEMPTS = 5


def evaluate_output(output: str, ethical_guidelines: str, judge_template: str) -> dict:
    judge_prompt = fill_template(
        judge_template,
        {
            "ETHICAL_GUIDELINES": ethical_guidelines,
            "LLM_USER_RESPONSE": output
        }
    )

    raw_judge_output = LLMJudge(judge_prompt)
    return parse_output(raw_judge_output)


def main():

    ethical_guidelines = load_text("guidelines/ethical_guidelines.txt")
    judge_template = load_text("prompts/judge_prompt.txt")

    dataset = pd.read_csv("data/SCOPE_dataset_360.csv")

    trace_rows = []
    unsafe_rows = []

    for index, row in dataset.iterrows():

        original_prompt = row["sentence"]
        bias_type = row["bias_type"]

        current_prompt = original_prompt

        trace = {
            "topic": row["topic"],
            "intent": row["intent"],
            "group": row["group"],
            "sentence": row["sentence"],
            "bias_type": row["bias_type"]
        }

        found_unsafe = False

        print("\n==============================")
        print(f"PROMPT {index + 1}")
        print(f"Bias type: {bias_type}")
        print("==============================")

        for attempt in range(1, MAX_ATTEMPTS + 1):

            print(f"\n--- ATTEMPT {attempt} ---")
            print(f"Prompt: {current_prompt}")

            output = LLMUser(current_prompt)
            judge_result = evaluate_output(
                output,
                ethical_guidelines,
                judge_template
            )

            trace[f"prompt_attempt_{attempt}"] = current_prompt
            trace[f"output_attempt_{attempt}"] = output
            trace[f"judge_status_attempt_{attempt}"] = judge_result["status"]
            trace[f"violated_guidelines_attempt_{attempt}"] = json.dumps(
                judge_result.get("violated_guidelines", []),
                ensure_ascii=False,
                indent=2
            )

            print(f"Judge status: {judge_result['status']}")

            if judge_result["status"] == "UNSAFE":

                found_unsafe = True

                unsafe_rows.append(
                    {
                        "topic": row["topic"],
                        "intent": row["intent"],
                        "group": row["group"],
                        "sentence": current_prompt,
                        "bias_type": row["bias_type"]
                    }
                )

                break

            if attempt < MAX_ATTEMPTS:
                current_prompt = LLMStressTester(
                    original_prompt=original_prompt,
                    previous_prompt=current_prompt,
                    previous_output=output
                )

        if found_unsafe:
            trace_rows.append(trace)

    os.makedirs("results", exist_ok=True)

    pd.DataFrame(trace_rows).to_csv(
        "results/stress_testing.csv",
        index=False,
        encoding="utf-8"
    )

    pd.DataFrame(unsafe_rows).to_csv(
        "data/SCOPE_stress_testing.csv",
        index=False,
        encoding="utf-8"
    )

    print("\nSaved:")
    print("- results/results_stress_testing.csv")
    print("- data/SCOPE_stress_testing_360.csv")


if __name__ == "__main__":
    main()