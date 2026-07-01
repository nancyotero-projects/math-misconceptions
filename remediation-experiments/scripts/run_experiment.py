"""Skeleton runner for remediation experiments.

This file intentionally starts small. The next step is to wire in model providers
after deciding which LLM APIs to compare.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]


def load_cases(split_path: Path) -> list[str]:
    data = json.loads(split_path.read_text(encoding="utf-8"))
    return data["case_ids"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default=str(EXPERIMENT_ROOT / "data" / "splits" / "pilot_20.json"))
    parser.add_argument("--prompt", default=str(EXPERIMENT_ROOT / "prompts" / "diagnosis_first.md"))
    args = parser.parse_args()

    case_ids = load_cases(Path(args.split))
    prompt_template = Path(args.prompt).read_text(encoding="utf-8")

    print(f"Loaded {len(case_ids)} cases.")
    print(f"Loaded prompt template: {args.prompt}")
    print("Model-provider calls will be added after the model list is finalized.")
    print(prompt_template[:300])


if __name__ == "__main__":
    main()
