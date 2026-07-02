"""Build paper-style misconception diagnosis prompt batches.

This reproduces the MaE paper's repeated random subsampling setup:

1. For each trial, randomly select one training example per misconception.
2. Select a different test example per misconception.
3. Build cross-topic and/or topic-constrained batch prompts.

Default output:

    remediation-experiments/outputs/misconception_first/paper_repeated_random_100/
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = REPO_ROOT / "data" / "data.json"
DEFAULT_OUTPUT_ROOT = EXPERIMENT_ROOT / "outputs" / "misconception_first"
DEFAULT_RUN_ID = "paper_repeated_random_100"
DEFAULT_SEED = 20240701
TOPIC_ORDER = [
    "Ratios and proportional reasoning",
    "Number Operations",
    "Patterns, relationships, and functions",
    "Number sense",
    "Algebraic representations",
    "Variables, expressions, and operations",
    "Equations and inequalities",
    "Properties of number and operations",
]


def load_data(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_row(row: dict) -> dict:
    return {
        "misconception": row["Misconception"],
        "misconception_id": row["Misconception ID"],
        "topic": row["Topic"],
        "example_number": int(row["Example Number"]),
        "question": row["Question"],
        "incorrect_answer": row["Incorrect Answer"],
        "correct_answer": row.get("Correct Answer", ""),
        "source": row.get("Source", ""),
    }


def group_by_misconception(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["misconception_id"]].append(row)
    return {
        misconception_id: sorted(items, key=lambda item: item["example_number"])
        for misconception_id, items in sorted(grouped.items())
    }


def sample_trial_examples(
    grouped: dict[str, list[dict]],
    rng: random.Random,
) -> tuple[list[dict], list[dict], list[dict]]:
    train_examples = []
    test_examples = []
    assignments = []

    for misconception_id, examples in grouped.items():
        if len(examples) < 2:
            raise ValueError(f"{misconception_id} has fewer than two examples.")

        selected = rng.sample(examples, 2)
        train_example, test_example = selected[0], selected[1]
        train_examples.append(train_example)
        test_examples.append(test_example)
        assignments.append(
            {
                "misconception_id": misconception_id,
                "topic": train_example["topic"],
                "train_example_number": train_example["example_number"],
                "test_example_number": test_example["example_number"],
            }
        )

    return train_examples, test_examples, assignments


def generate_prompt(train_examples: list[dict], test_examples: list[dict]) -> str:
    prompt = (
        "You are an expert tutor on middle school math with years of experience understanding students' most common math mistakes. "
        "You have identified a set of common mistakes called Misconceptions, and you use them to diagnose student's answers to math questions. "
        "You have also developed a labeled dataset of question items, and diagnosed them with the appropriate misconception ID.\n"
        "Using the set of misconceptions and the labeled dataset, your task today is to take some items of unlabeled data and provide a diagnosis for each unlabeled item.\n\n"
        "Here is the list of misconceptions together with a brief description:\n"
    )

    for index, example in enumerate(train_examples, start=1):
        prompt += f"""
Train Example {index}
Question:
{example["question"]}
Answer:
{example["incorrect_answer"]}
Diagnosis: {example["misconception_id"]}
Misconception Description: {example["misconception"]}
Topic of Misconception: {example["topic"]}

"""

    prompt += """
Below are the unlabeled Test Examples. For each Test Example, provide only the most likely Misconception ID for the Test Answer from the provided list.
Don't write anything else but a sequence of lines of the format $Test_Example_Number, $Misconception_ID

"""

    for index, example in enumerate(test_examples, start=1):
        prompt += f"""
Test Example {index}:
Question:
{example["question"]}
Test Answer:
{example["incorrect_answer"]}

"""

    return prompt


def write_jsonl(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_assignments(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "run_id",
        "condition",
        "trial",
        "prompt_batch_id",
        "topic",
        "misconception_id",
        "train_example_number",
        "test_example_number",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_batches(
    rows: list[dict],
    run_id: str,
    iterations: int,
    seed: int,
    condition: str,
) -> tuple[list[dict], list[dict]]:
    grouped = group_by_misconception(rows)
    rng = random.Random(seed)
    prompt_batches = []
    assignment_rows = []

    for trial in range(iterations):
        train_examples, test_examples, assignments = sample_trial_examples(grouped, rng)

        if condition in {"cross_topic", "both"}:
            batch_id = f"cross_topic_trial_{trial:03d}"
            prompt_batches.append(
                {
                    "run_id": run_id,
                    "condition": "cross_topic",
                    "trial": trial,
                    "prompt_batch_id": batch_id,
                    "topic": "ALL",
                    "diagnoses_expected": len(test_examples),
                    "test_items": [
                        {
                            "test_example_number": index,
                            "misconception_id": example["misconception_id"],
                            "topic": example["topic"],
                            "example_number": example["example_number"],
                        }
                        for index, example in enumerate(test_examples, start=1)
                    ],
                    "prompt": generate_prompt(train_examples, test_examples),
                }
            )
            for assignment in assignments:
                assignment_rows.append(
                    {
                        "run_id": run_id,
                        "condition": "cross_topic",
                        "trial": trial,
                        "prompt_batch_id": batch_id,
                        "topic": assignment["topic"],
                        **assignment,
                    }
                )

        if condition in {"topic_constrained", "both"}:
            for topic in TOPIC_ORDER:
                topic_train = [example for example in train_examples if example["topic"] == topic]
                topic_test = [example for example in test_examples if example["topic"] == topic]
                if not topic_test:
                    continue

                topic_slug = topic.lower().replace(" ", "_").replace(",", "").replace("/", "_")
                batch_id = f"topic_constrained_{topic_slug}_trial_{trial:03d}"
                prompt_batches.append(
                    {
                        "run_id": run_id,
                        "condition": "topic_constrained",
                        "trial": trial,
                        "prompt_batch_id": batch_id,
                        "topic": topic,
                        "diagnoses_expected": len(topic_test),
                        "test_items": [
                            {
                                "test_example_number": index,
                                "misconception_id": example["misconception_id"],
                                "topic": example["topic"],
                                "example_number": example["example_number"],
                            }
                            for index, example in enumerate(topic_test, start=1)
                        ],
                        "prompt": generate_prompt(topic_train, topic_test),
                    }
                )
                for assignment in assignments:
                    if assignment["topic"] == topic:
                        assignment_rows.append(
                            {
                                "run_id": run_id,
                                "condition": "topic_constrained",
                                "trial": trial,
                                "prompt_batch_id": batch_id,
                                "topic": topic,
                                **assignment,
                            }
                        )

    return prompt_batches, assignment_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--condition",
        choices=["cross_topic", "topic_constrained", "both"],
        default="both",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.run_id
    input_dir = output_dir / "inputs"
    response_dir = output_dir / "raw_model_responses"
    parsed_dir = output_dir / "parsed_diagnoses"
    scored_dir = output_dir / "scored"
    log_dir = output_dir / "logs"

    for directory in [input_dir, response_dir, parsed_dir, scored_dir, log_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    rows = [normalize_row(row) for row in load_data(Path(args.data))]
    prompt_batches, assignments = build_batches(
        rows=rows,
        run_id=args.run_id,
        iterations=args.iterations,
        seed=args.seed,
        condition=args.condition,
    )

    write_jsonl(prompt_batches, input_dir / "prompt_batches.jsonl")
    write_assignments(assignments, input_dir / "trial_assignments.csv")

    run_config = {
        "run_id": args.run_id,
        "workflow": "misconception_first_paper_repeated_random_subsampling",
        "conditions": args.condition,
        "iterations": args.iterations,
        "seed": args.seed,
        "data_path": str(Path(args.data)),
        "output_dir": str(output_dir),
        "prompt_batches": len(prompt_batches),
        "diagnoses_per_model_cross_topic": 55 * args.iterations
        if args.condition in {"cross_topic", "both"}
        else 0,
        "diagnoses_per_model_topic_constrained": 55 * args.iterations
        if args.condition in {"topic_constrained", "both"}
        else 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(prompt_batches)} prompt batches.")
    print(f"Wrote {len(assignments)} trial assignment rows.")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()

