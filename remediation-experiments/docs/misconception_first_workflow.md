# Misconception-First Workflow

This workflow runs the first experimental stage: ask each model to diagnose the likely misconception from a pattern of consistent student mistakes.

The output of this stage becomes an input to later remediation experiments. It lets us separate two questions:

1. Can the model diagnose the misconception?
2. If the misconception is known or model-diagnosed, can the model recommend a research-aligned intervention?

## Workflow Summary

```text
Raw recommendation workbook
        |
        v
prepare_dataset.py
        |
        v
data/processed/remediation_cases.jsonl
        |
        v
build_misconception_first_inputs.py
        |
        v
outputs/misconception_first/<run_id>/inputs/prompt_inputs.jsonl
        |
        v
model provider calls
        |
        v
outputs/misconception_first/<run_id>/raw_model_responses/model_responses.jsonl
        |
        v
parse + score diagnosis
        |
        v
outputs/misconception_first/<run_id>/parsed_diagnoses/diagnoses.csv
outputs/misconception_first/<run_id>/scored/diagnosis_scores.csv
```

## Step 1: Prepare the Shared Dataset

Run from the repository root:

```bash
python remediation-experiments/scripts/prepare_dataset.py
```

This creates:

- `remediation-experiments/data/processed/recommendations_long.csv`
- `remediation-experiments/data/processed/remediation_cases.jsonl`
- `remediation-experiments/data/splits/pilot_20.json`
- `remediation-experiments/data/splits/full_55.json`

## Step 2: Build Misconception-First Prompt Inputs

Run:

```bash
python remediation-experiments/scripts/build_misconception_first_inputs.py
```

Default output folder:

```text
remediation-experiments/outputs/misconception_first/pilot_20/
```

The script creates:

- `inputs/prompt_inputs.jsonl`
- `run_config.json`
- empty folders for raw responses, parsed diagnoses, scores, and logs

## Step 3: Model Computation

Each line in `inputs/prompt_inputs.jsonl` is one model-ready request.

Required input fields:

- `run_id`
- `condition`
- `case_id`
- `topic`
- `gold_misconception_id`
- `gold_misconception`
- `student_work_pattern_text`
- `prompt`

For each model, save one JSONL record per case to:

```text
outputs/misconception_first/<run_id>/raw_model_responses/model_responses.jsonl
```

Recommended output fields:

- `run_id`
- `condition`
- `model_provider`
- `model_name`
- `case_id`
- `topic`
- `gold_misconception_id`
- `prompt`
- `raw_response`
- `created_at`
- `temperature`

## Step 4: Parse Diagnoses

Parse each model response into a structured diagnosis record.

Save to:

```text
outputs/misconception_first/<run_id>/parsed_diagnoses/diagnoses.csv
```

Recommended parsed fields:

- `run_id`
- `model_provider`
- `model_name`
- `case_id`
- `topic`
- `gold_misconception_id`
- `predicted_misconception_id`
- `predicted_misconception_label`
- `diagnosis_rationale`
- `confidence`
- `parse_error`

## Step 5: Score Diagnosis

Score whether the predicted misconception matches the gold misconception.

Save to:

```text
outputs/misconception_first/<run_id>/scored/diagnosis_scores.csv
```

Recommended score fields:

- `exact_id_match`
- `topic_match`
- `human_accepts_alternative`
- `notes`

This preserves room for expert validation, since a model may name a broader or related misconception that is instructionally plausible.

## Prompt Condition

The first condition is:

```text
misconception_first_diagnosis
```

Prompt file:

```text
remediation-experiments/prompts/misconception_first_diagnosis.md
```

## Pilot

Start with:

- Split: `pilot_20`
- Cases: 20
- Models: 3
- Temperature: 0.0 or 0.2

Expected model responses:

```text
20 cases x 3 models = 60 diagnosis responses
```

After diagnosis quality is understood, use the model-predicted misconception as an input to the remediation workflow.

