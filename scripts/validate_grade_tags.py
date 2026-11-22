#!/usr/bin/env python3
"""Validate grade tags; optionally prove original fields were preserved."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

TAG_KEYS = {"misconception", "example", "question", "correct_answer", "incorrect_answer"}
ALLOWED = {str(n) for n in range(1, 9)} | {"K", "HS"}
ADDED = {"grade_tags", "grade_alignment"}

def validate(rows, baseline=None):
    seen = set()
    family_grades = defaultdict(set)
    family_tags = {}
    for row in rows:
        key = (row["Misconception ID"], row["Example Number"])
        if key in seen:
            raise ValueError(f"Duplicate example: {key}")
        seen.add(key)
        tags = row.get("grade_tags", {})
        if set(tags) != TAG_KEYS:
            raise ValueError(f"Missing/unexpected tag keys: {key}")
        for field, values in tags.items():
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or v not in ALLOWED for v in values):
                raise ValueError(f"Invalid {field} grades: {key}")
            if len(values) != len(set(values)):
                raise ValueError(f"Duplicate {field} grades: {key}")
        for field in ("question", "correct_answer", "incorrect_answer"):
            if tags[field] != tags["example"]:
                raise ValueError(f"Answer/question must inherit example grade: {key}")
        alignment = row.get("grade_alignment", {})
        codes = alignment.get("standard_codes", [])
        if not codes or not all(isinstance(c, str) and "." in c for c in codes):
            raise ValueError(f"Missing Common Core codes: {key}")
        inferred = {"HS" if c.startswith("HS") else c.split(".")[0] for c in codes}
        if set(tags["example"]) != inferred:
            raise ValueError(f"Standard/grade mismatch: {key}")
        if alignment.get("status") != "inferred":
            raise ValueError(f"Missing annotation status: {key}")
        match_type = alignment.get("match_type")
        if match_type not in {"direct", "closest_match", "extension", "ambiguous"}:
            raise ValueError(f"Missing alignment match type: {key}")
        if alignment.get("requires_grade_review") is not (match_type == "ambiguous"):
            raise ValueError(f"Ambiguity/review flag mismatch: {key}")
        urls = alignment.get("source_urls", [])
        if not urls or not all(u.startswith("https://www.thecorestandards.org/Math/Content/") for u in urls):
            raise ValueError(f"Missing official standard sources: {key}")
        family = key[0]
        family_grades[family].update(tags["example"])
        if family in family_tags and family_tags[family] != tags["misconception"]:
            raise ValueError(f"Inconsistent misconception grades: {family}")
        family_tags[family] = tags["misconception"]
    for family, grades in family_grades.items():
        if set(family_tags[family]) != grades:
            raise ValueError(f"Misconception grades must be the union of example grades: {family}")
    if baseline is not None:
        stripped = [{k: v for k, v in row.items() if k not in ADDED} for row in rows]
        original = [{k: v for k, v in row.items() if k not in ADDED} for row in baseline]
        if stripped != original:
            raise ValueError("Original record order, fields or values changed")
    return {"misconceptions": len(family_grades), "examples": len(rows),
            "tagged_answers": 2 * len(rows)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1] / "data/data.json")
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.dataset.read_text(encoding="utf-8"))
    baseline = json.loads(args.baseline.read_text(encoding="utf-8")) if args.baseline else None
    print(json.dumps(validate(rows, baseline), indent=2))
