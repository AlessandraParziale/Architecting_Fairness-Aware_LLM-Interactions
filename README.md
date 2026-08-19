# Architecting Fairness-Aware LLM Interactions

This repository is the **replication package** for the paper *"Architecting Fairness-Aware LLM Interactions"*.

The paper proposes a **fairness-assurance architecture** for LLM-based interactions, grounded in three reusable design patterns and instantiated as a fully automated **multi-agent framework** that evaluates and iteratively refines LLM-generated responses against a set of ethical guidelines before delivery.

## 📖 Project Overview

### Architectural Design Patterns

The architecture is grounded in three reusable design patterns, each addressing a complementary concern of interaction-time fairness assurance:

- **Decontextualized Fairness Assessment** — separates response generation from fairness evaluation through an independent evaluator.
- **Iterative Fairness Repair** — introduces a closed feedback loop that progressively revises responses.
- **Heterogeneous Fairness Validation** — assigns different roles in the pipeline to different LLM families.

### Agents

These patterns are operationalized through **three agents**:

- 🗣️ **LLMUser** — generates the initial response to the user's request
- ⚖️ **LLMJudge** — evaluates the generated response against a set of ethical guidelines
- 🛠️ **LLMRefiner** — when violations are detected, revises the response to eliminate them

The process is iterative: the refined response is re-evaluated by the LLMJudge, and the cycle continues until the response is classified as `SAFE`, at which point it is returned to the user.


### Ethical Guidelines

The adopted 15 ethical guidelines were manually extracted from the *OpenAI Usage Policies* (updated in 2025) and the *Anthropic Claude Constitution* (updated in 2026) and are available in the `guidelines` folder.


### Dataset and Stress Testing

The evaluation was conducted on the **SCOPE** dataset (Stereotype-COnditioned Prompts for Evaluation), from which a balanced sample of **360 prompts** was extracted. To ensure the prompts were capable of eliciting problematic responses, an iterative *stress testing* procedure was conducted using a fourth agent, the **LLMStressTester**, which progressively rewrote the prompts for up to 5 iterations, producing a refined dataset of **262 prompts**.


### Experimental Configurations

The framework was evaluated using two LLM families — **GPT (GPT-4o mini)** and **Claude (Claude Haiku 4.5)** — across **8 experimental configurations** (C1–C8), distinguishing *Within-Family* configurations (all agents from the same family) from *Cross-Family* configurations (agents from different families):

| Configuration | LLMUser | LLMJudge | LLMRefiner | Category |
|---|---|---|---|---|
| C1 | GPT | GPT | GPT | Within-Family |
| C2 | Claude | Claude | Claude | Within-Family |
| C3 | GPT | GPT | Claude | Cross-Family |
| C4 | GPT | Claude | GPT | Cross-Family |
| C5 | Claude | GPT | GPT | Cross-Family |
| C6 | Claude | Claude | GPT | Cross-Family |
| C7 | Claude | GPT | Claude | Cross-Family |
| C8 | GPT | Claude | Claude | Cross-Family |

Each configuration was run separately on the same set of prompts, using the multi-agent framework to generate, evaluate, and, when necessary, refine each response according to the 15 ethical guidelines.

---

## 📂 Repository Structure

```
ASAS/
├── 🧠 agents/
├── 📊 analysis/
├── 📁 data/
├── 📜 guidelines/
├── 📋 policies/
├── ✍️ prompts/
├── 📈 results/
│   ├── dataset_261/
│   └── dataset_360/
├── evaluate_rules.py
├── utils.py
└── .gitignore
```

### 🧠 `agents/`
Contains the implementation of all LLM agents that make up the framework:
- `llm_user.py` — generates the initial response (**LLMUser**)
- `llm_judge.py` — evaluates responses against the ethical guidelines (**LLMJudge**)
- `llm_refiner.py` — refines responses classified as `UNSAFE` (**LLMRefiner**)
- `llm_stress_tester.py` — generates progressively more challenging prompt variants for the dataset stress-testing procedure (**LLMStressTester**)

### 📊 `analysis/`
Contains the code and results of the analyses performed on the experimental data:
- `configuration_analysis.py` — script for analyzing the experimental configurations
- `guideline_by_bias_type.csv` — guideline violations by bias type
- `guideline_by_intent.csv` — guideline violations by communicative intent
- `guideline_frequency_by_configuration.csv` — guideline violation frequency by configuration
- `hardest_guidelines_to_eliminate.csv` — guidelines that were hardest to eliminate during refinement
- `iteration_distribution_by_configuration.csv` — distribution of refinement iterations by configuration
- `summary_by_configuration.csv` — summary of results for each configuration
- `violation_distribution_by_configuration.csv` — distribution of violations by configuration

### 📁 `data/`
Contains the datasets used:
- `SCOPE_dataset.csv` — original SCOPE dataset
- `SCOPE_dataset_360.csv` — balanced sample of 360 prompts extracted from SCOPE
- `SCOPE_stress_testing.csv` — final dataset of 262 prompts obtained from stress testing
- `data_selection.py` — code for the stratified selection of the 360 prompts
- `stress_test.py` — code for the stress-testing procedure that generates the 262-prompt dataset

### 📜 `guidelines/`
Contains the extracted ethical guidelines and documentation of the extraction process:
- `ethical_guidelines.txt` — the final set of 15 ethical guidelines (G1–G15)
- `Guideline_Extraction.pdf` — methodology for the guideline extraction process

### 📋 `policies/`
Contains the policy documents from which the ethical guidelines were extracted:
- `openai_policies_2025.pdf` — OpenAI Usage Policies (2025)
- `anthropic_constitution_2026.pdf` — Anthropic Claude Constitution (2026)

### ✍️ `prompts/`
Contains all the prompts used to guide the LLM agents:
- `judge_prompt.txt` — prompt for the LLMJudge
- `refiner_prompt.txt` — prompt for the LLMRefiner
- `stress_tester_prompt.txt` — prompt for the LLMStressTester

### 📈 `results/`
Contains the experimental results obtained with the 8 LLM configurations (C1–C8), split into two subfolders based on the dataset used:
- **`dataset_262/`** — results obtained on the refined dataset of 262 prompts (`SCOPE_results_C1.csv` → `SCOPE_results_C8.csv`)
- **`dataset_360/`** — results obtained on the original dataset of 360 prompts (`SCOPE_results_C1.csv` → `SCOPE_results_C8.csv`)

### Main Files
- **`evaluate_rules.py`** — main script that coordinates the multi-agent framework (LLMUser → LLMJudge → LLMRefiner)
- **`utils.py`** — utility functions shared by the agents

