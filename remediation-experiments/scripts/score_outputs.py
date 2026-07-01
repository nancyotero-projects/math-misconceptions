"""Skeleton for scoring model outputs with the human rubric schema."""

from __future__ import annotations

import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = EXPERIMENT_ROOT / "rubrics" / "scoring_schema.json"


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    print("Scoring dimensions:")
    for dimension in schema["dimensions"]:
        print(f"- {dimension}")


if __name__ == "__main__":
    main()
