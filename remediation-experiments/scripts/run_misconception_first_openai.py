"""Run misconception-first diagnosis prompt batches with OpenAI chat models.

Example smoke test:

    OPENAI_API_KEY=... python remediation-experiments/scripts/run_misconception_first_openai.py --limit 2

Example full run:

    OPENAI_API_KEY=... python remediation-experiments/scripts/run_misconception_first_openai.py --model gpt-4-turbo
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "paper_repeated_random_100"
DEFAULT_OUTPUT_ROOT = EXPERIMENT_ROOT / "outputs" / "misconception_first"
OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_completed_keys(path: Path, model_name: str) -> set[tuple[str, str, int, str]]:
    if not path.exists():
        return set()

    completed = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("model_name") == model_name and not row.get("error"):
                completed.add(
                    (
                        row["condition"],
                        row["prompt_batch_id"],
                        int(row["trial"]),
                        row["topic"],
                    )
                )
    return completed


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def call_openai(
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a math expert specialized in diagnosing student misconceptions.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "frequency_penalty": 0.0,
    }
    request = urllib.request.Request(
        OPENAI_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc

    return data["choices"][0]["message"]["content"].strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--model", default="gpt-4-turbo")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=2000)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Set it in your shell or add it to a local .env file."
        )

    output_dir = Path(args.output_root) / args.run_id
    input_path = output_dir / "inputs" / "prompt_batches.jsonl"
    response_dir = output_dir / "raw_model_responses"
    response_dir.mkdir(parents=True, exist_ok=True)
    response_path = response_dir / "model_responses.jsonl"

    prompt_batches = load_jsonl(input_path)
    completed = set() if args.no_resume else load_completed_keys(response_path, args.model)

    pending = []
    for batch in prompt_batches:
        key = (
            batch["condition"],
            batch["prompt_batch_id"],
            int(batch["trial"]),
            batch["topic"],
        )
        if key not in completed:
            pending.append(batch)

    if args.limit:
        pending = pending[: args.limit]

    print(f"Loaded {len(prompt_batches)} prompt batches.")
    print(f"Pending for {args.model}: {len(pending)}")
    print(f"Writing responses to: {response_path}")

    for index, batch in enumerate(pending, start=1):
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            raw_response = call_openai(
                model=args.model,
                prompt=batch["prompt"],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            row = {
                "run_id": batch["run_id"],
                "condition": batch["condition"],
                "trial": batch["trial"],
                "prompt_batch_id": batch["prompt_batch_id"],
                "topic": batch["topic"],
                "diagnoses_expected": batch["diagnoses_expected"],
                "test_items": batch["test_items"],
                "model_provider": args.provider,
                "model_name": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "prompt": batch["prompt"],
                "raw_response": raw_response,
                "created_at": started_at,
                "error": "",
            }
        except Exception as exc:
            row = {
                "run_id": batch["run_id"],
                "condition": batch["condition"],
                "trial": batch["trial"],
                "prompt_batch_id": batch["prompt_batch_id"],
                "topic": batch["topic"],
                "diagnoses_expected": batch["diagnoses_expected"],
                "test_items": batch["test_items"],
                "model_provider": args.provider,
                "model_name": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "prompt": batch["prompt"],
                "raw_response": "",
                "created_at": started_at,
                "error": repr(exc),
            }

        append_jsonl(response_path, row)
        print(
            f"[{index}/{len(pending)}] {batch['condition']} "
            f"trial={batch['trial']} topic={batch['topic']} error={bool(row['error'])}"
        )

        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()
