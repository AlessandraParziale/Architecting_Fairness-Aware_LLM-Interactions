import json
import pandas as pd

from utils import load_text, fill_template, parse_output
from agents.llm_user import LLMUser
from agents.llm_judge import LLMJudge
from agents.llm_refiner import LLMRefiner

def main():

    ethical_guidelines = load_text("guidelines/ethical_guidelines.txt")
    judge_template = load_text("prompts/judge_prompt.txt")
    refiner_template = load_text("prompts/refiner_prompt.txt")

    dataset = pd.read_csv("data/SCOPE_stress_testing.csv")

    all_results = []
    iterations_to_safe_list = []
    initial_outputs = []

    for index, row in dataset.iterrows():

        user_prompt = row["sentence"]
        bias_type = row["bias_type"]


        print("\n==============================")
        print(f"PROMPT {index + 1}")
        print(f"Bias type: {bias_type}")
        print(f"User prompt: {user_prompt}")
        print("==============================")

        current_output = LLMUser(user_prompt)
        initial_output = current_output

        refinement_history = []
        iteration = 1
        prompt_results = []

        while True:

            print(f"\n========== ITERATION {iteration} ==========")

            judge_prompt = fill_template(
                judge_template,
                {
                    "ETHICAL_GUIDELINES": ethical_guidelines,
                    "LLM_USER_RESPONSE": current_output
                }
            )

            raw_judge_output = LLMJudge(judge_prompt)
            judge_result = parse_output(raw_judge_output)

            prompt_results.append(
                {
                    "iteration": iteration,
                    "output": current_output,
                    "status": judge_result["status"],
                    "num_violated_guidelines": len(judge_result["violated_guidelines"]),
                    "violated_guidelines": judge_result["violated_guidelines"]
                }
            )

            print("\n=== PARSED OUTPUT ===")
            print(judge_result)

            if judge_result["status"] == "SAFE":

                print("\n=== FINAL SAFE OUTPUT ===")
                print(current_output)

                all_results.append(
                    json.dumps(
                        prompt_results,
                        ensure_ascii=False,
                        indent=2
                    )
                )

                iterations_to_safe_list.append(iteration)

                print("\n=== INITIAL OUTPUT ===")
                print(initial_output)

                print("\n=== FINAL SAFE OUTPUT ===")
                print(current_output)

                initial_outputs.append(initial_output)

                break

            violated_guidelines = judge_result["violated_guidelines"]

            refinement_history.append(
                {
                    "iteration": iteration,
                    "output": current_output,
                    "violated_guidelines": violated_guidelines
                }
            )

            refiner_prompt = fill_template(
                refiner_template,
                {
                    "USER_PROMPT": user_prompt,

                    "LLM_USER_RESPONSE": current_output,

                    "VIOLATED_GUIDELINES": json.dumps(
                        violated_guidelines,
                        indent=2,
                        ensure_ascii=False
                    ),

                    "REFINEMENT_HISTORY": json.dumps(
                        refinement_history,
                        indent=2,
                        ensure_ascii=False
                    )
                }
            )

            print("\n=== REFINER PROMPT ===")
            print(refiner_prompt)

            refined_output = LLMRefiner(refiner_prompt)

            print("\n=== REFINED OUTPUT ===")
            print(refined_output)

            current_output = refined_output
            iteration += 1

    dataset["initial_output"] = initial_outputs
    dataset["results_guidelines"] = all_results
    dataset["num_iterations_guidelines"] = iterations_to_safe_list

    dataset.to_csv(
        "results/dataset_261/SCOPE_results_C2.csv",
        index=False,
        encoding="utf-8"
    )

    print("\nResults saved to SCOPE_results_C2.csv")


if __name__ == "__main__":
    main()