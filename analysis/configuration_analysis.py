import json
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path


CONFIG_FILES = {
    "C1": "results/dataset_261/SCOPE_results_C1.csv",
    "C2": "results/dataset_261/SCOPE_results_C2.csv",
    "C3": "results/dataset_261/SCOPE_results_C3.csv",
    "C4": "results/dataset_261/SCOPE_results_C4.csv",
    "C5": "results/dataset_261/SCOPE_results_C5.csv",
    "C6": "results/dataset_261/SCOPE_results_C6.csv",
    "C7": "results/dataset_261/SCOPE_results_C7.csv",
    "C8": "results/dataset_261/SCOPE_results_C8.csv",
}


def load_results(value):
    if pd.isna(value):
        return []
    return json.loads(value)


def get_guideline_ids(iteration):
    return {
        guideline["guideline_id"]
        for guideline in iteration.get("violated_guidelines", [])
    }


def analyze_configuration(config_name, file_path):
    df = pd.read_csv(file_path)
    df["parsed_results"] = df["results_guidelines"].apply(load_results)

    df["num_iterations_guidelines"] = pd.to_numeric(
        df["num_iterations_guidelines"],
        errors="coerce"
    )

    df["total_num_violations"] = df["parsed_results"].apply(
        lambda results: sum(
            iteration["num_violated_guidelines"]
            for iteration in results
        )
    )

    df["final_status"] = df["parsed_results"].apply(
        lambda x: x[-1]["status"] if len(x) > 0 else None
    )

    guideline_counter = Counter()
    guideline_by_bias = defaultdict(Counter)
    guideline_by_intent = defaultdict(Counter)
    disappearance_rows = []

    for _, row in df.iterrows():
        results = row["parsed_results"]

        if len(results) == 0:
            continue

        # Count guideline violations across ALL iterations
        for iteration in results:
            for guideline in iteration.get("violated_guidelines", []):
                gid = guideline["guideline_id"]
                guideline_counter[gid] += 1
                guideline_by_bias[row["bias_type"]][gid] += 1
                guideline_by_intent[row["intent"]][gid] += 1

        # Hardest guidelines to eliminate:
        # starts from guidelines violated in the initial response
        initial_guidelines = get_guideline_ids(results[0])

        for gid in initial_guidelines:
            disappearance_iteration = None

            for iteration in results[1:]:
                current_guidelines = get_guideline_ids(iteration)

                if gid not in current_guidelines:
                    disappearance_iteration = iteration["iteration"]
                    break

            if disappearance_iteration is None:
                if results[-1]["status"] == "SAFE":
                    disappearance_iteration = results[-1]["iteration"]

            disappearance_rows.append(
                {
                    "configuration": config_name,
                    "guideline_id": gid,
                    "disappearance_iteration": disappearance_iteration
                }
            )

    summary = {
        "configuration": config_name,
        "num_prompts": len(df),
        "avg_total_violations": df["total_num_violations"].mean(),
        "sum_total_violations": df["total_num_violations"].sum(),
        "median_total_violations": df["total_num_violations"].median(),
        "avg_iterations": df["num_iterations_guidelines"].mean(),
        "median_iterations": df["num_iterations_guidelines"].median(),
        "max_iterations": df["num_iterations_guidelines"].max(),
        "final_safe_rate": (df["final_status"] == "SAFE").mean() * 100,
    }

    guideline_freq = pd.DataFrame(
        guideline_counter.items(),
        columns=["guideline_id", "count"]
    )
    guideline_freq["configuration"] = config_name
    guideline_freq = guideline_freq[
        ["configuration", "guideline_id", "count"]
    ].sort_values(["configuration", "count"], ascending=[True, False])

    iteration_distribution = (
        df["num_iterations_guidelines"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    iteration_distribution.columns = ["num_iterations", "num_prompts"]
    iteration_distribution["configuration"] = config_name
    iteration_distribution = iteration_distribution[
        ["configuration", "num_iterations", "num_prompts"]
    ]

    violation_distribution = (
        df["total_num_violations"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    violation_distribution.columns = [
        "total_num_violations",
        "num_prompts"
    ]

    violation_distribution["configuration"] = config_name

    violation_distribution = violation_distribution[
        ["configuration", "total_num_violations", "num_prompts"]
    ]

    disappearance_df = pd.DataFrame(disappearance_rows)

    if not disappearance_df.empty:
        hardest_guidelines = (
            disappearance_df
            .groupby(["configuration", "guideline_id"])
            ["disappearance_iteration"]
            .mean()
            .reset_index()
            .rename(
                columns={
                    "disappearance_iteration": "avg_disappearance_iteration"
                }
            )
            .sort_values(
                ["configuration", "avg_disappearance_iteration"],
                ascending=[True, False]
            )
        )
    else:
        hardest_guidelines = pd.DataFrame(
            columns=[
                "configuration",
                "guideline_id",
                "avg_disappearance_iteration"
            ]
        )

    bias_rows = []
    for bias, counter in guideline_by_bias.items():
        for gid, count in counter.items():
            bias_rows.append(
                {
                    "configuration": config_name,
                    "bias_type": bias,
                    "guideline_id": gid,
                    "count": count,
                }
            )

    intent_rows = []
    for intent, counter in guideline_by_intent.items():
        for gid, count in counter.items():
            intent_rows.append(
                {
                    "configuration": config_name,
                    "intent": intent,
                    "guideline_id": gid,
                    "count": count,
                }
            )

    return (
        summary,
        guideline_freq,
        iteration_distribution,
        pd.DataFrame(bias_rows),
        pd.DataFrame(intent_rows),
        violation_distribution,
        hardest_guidelines,
    )


def main():
    output_dir = Path("analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    all_guidelines = []
    all_iterations = []
    all_bias = []
    all_intent = []
    all_violation_distributions = []
    all_hardest_guidelines = []

    for config_name, file_path in CONFIG_FILES.items():
        print(f"Analyzing {config_name}...")

        (
            summary,
            guideline_freq,
            iteration_dist,
            bias_df,
            intent_df,
            violation_distribution,
            hardest_guidelines,
        ) = analyze_configuration(config_name, file_path)

        summaries.append(summary)
        all_guidelines.append(guideline_freq)
        all_iterations.append(iteration_dist)
        all_bias.append(bias_df)
        all_intent.append(intent_df)
        all_violation_distributions.append(violation_distribution)
        all_hardest_guidelines.append(hardest_guidelines)

    pd.DataFrame(summaries).to_csv(
        output_dir / "summary_by_configuration.csv",
        index=False
    )

    pd.concat(all_guidelines).to_csv(
        output_dir / "guideline_frequency_by_configuration.csv",
        index=False
    )

    pd.concat(all_iterations).to_csv(
        output_dir / "iteration_distribution_by_configuration.csv",
        index=False
    )

    pd.concat(all_bias).to_csv(
        output_dir / "guideline_by_bias_type.csv",
        index=False
    )

    pd.concat(all_intent).to_csv(
        output_dir / "guideline_by_intent.csv",
        index=False
    )

    pd.concat(all_violation_distributions).to_csv(
        output_dir / "violation_distribution_by_configuration.csv",
        index=False
    )

    pd.concat(all_hardest_guidelines).to_csv(
        output_dir / "hardest_guidelines_to_eliminate.csv",
        index=False
    )

    print("\nSaved analysis files in analysis/")


if __name__ == "__main__":
    main()