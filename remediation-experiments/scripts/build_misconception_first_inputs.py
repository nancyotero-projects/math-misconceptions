"""Build prompt inputs for the misconception-first diagnosis workflow.

Run from the repository root:

    python remediation-experiments/scripts/build_misconception_first_inputs.py

Default output:

    remediation-experiments/outputs/misconception_first/pilot_20/
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = EXPERIMENT_ROOT / "data" / "processed" / "remediation_cases.jsonl"
DEFAULT_SPLIT_PATH = EXPERIMENT_ROOT / "data" / "splits" / "pilot_20.json"
DEFAULT_PROMPT_PATH = EXPERIMENT_ROOT / "prompts" / "misconception_first_diagnosis.md"
DEFAULT_OUTPUT_ROOT = EXPERIMENT_ROOT / "outputs" / "misconception_first"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_split(path: Path) -> tuple[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["split_name"], data["case_ids"]


def format_student_work_pattern(case: dict) -> str:
    parts = []
    for index, item in enumerate(case["student_work_pattern"], start=1):
        parts.append(
            "\n".join(
                [
                    f"Example {index}",
                    "Task:",
                    item["activity_or_question"],
                    "Student response:",
                    item["student_incorrect_response"],
                ]
            )
        )
    return "\n\n".join(parts)


def render_prompt(template: str, student_work_pattern: str) -> str:
    return template.replace("{{student_work_pattern}}", student_work_pattern)


def write_jsonl(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_prompt_inputs(
    cases: list[dict],
    case_ids: list[str],
    prompt_template: str,
    run_id: str,
) -> list[dict]:
    case_lookup = {case["case_id"]: case for case in cases}
    prompt_inputs = []

    for case_id in case_ids:
        case = case_lookup[case_id]
        student_work_pattern_text = format_student_work_pattern(case)
        prompt = render_prompt(prompt_template, student_work_pattern_text)

        prompt_inputs.append(
            {
                "run_id": run_id,
                "condition": "misconception_first_diagnosis",
                "case_id": case["case_id"],
                "topic": case["topic"],
                "gold_misconception_id": case["misconception_id"],
                "gold_misconception": case["misconception"],
                "student_work_pattern_text": student_work_pattern_text,
                "prompt": prompt,
            }
        )

    return prompt_inputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(CASES_PATH))
    parser.add_argument("--split", default=str(DEFAULT_SPLIT_PATH))
    parser.add_argument("--prompt", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    args = parser.parse_args()

    split_name, case_ids = load_split(Path(args.split))
    run_id = args.run_id or split_name
    output_dir = Path(args.output_root) / run_id

    input_dir = output_dir / "inputs"
    response_dir = output_dir / "raw_model_responses"
    parsed_dir = output_dir / "parsed_diagnoses"
    scored_dir = output_dir / "scored"
    log_dir = output_dir / "logs"

    for directory in [input_dir, response_dir, parsed_dir, scored_dir, log_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    cases = load_jsonl(Path(args.cases))
    prompt_template = Path(args.prompt).read_text(encoding="utf-8")
    prompt_inputs = build_prompt_inputs(cases, case_ids, prompt_template, run_id)

    write_jsonl(prompt_inputs, input_dir / "prompt_inputs.jsonl")

    run_config = {
        "run_id": run_id,
        "condition": "misconception_first_diagnosis",
        "split_name": split_name,
        "case_count": len(prompt_inputs),
        "cases_path": str(Path(args.cases)),
        "split_path": str(Path(args.split)),
        "prompt_path": str(Path(args.prompt)),
        "output_dir": str(output_dir),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(prompt_inputs)} prompt inputs.")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()

