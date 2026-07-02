# Misconception-First Workflow

This workflow runs the first experimental stage: ask each model to diagnose the likely misconception before any remediation recommendation is generated.

The primary workflow reproduces the diagnosis method from the MaE benchmark paper: repeated random subsampling with one training example and one test example per misconception in each trial.

## Why Start With Diagnosis?

The remediation study needs to distinguish between two bottlenecks:

1. Can the model diagnose the misconception?
2. Once the misconception is known, can the model recommend a research-aligned intervention?

If diagnosis is unstable, then remediation quality may be poor because the model is solving the wrong instructional problem.

## Method From The Paper

The paper used:

- 55 misconceptions
- 4 diagnostic examples per misconception
- 100 repeated random subsampling iterations
- 1 randomly selected training example per misconception per iteration
- 1 different randomly selected test example per misconception per iteration
- in-context learning prompts
- two diagnosis settings:
  - cross-topic diagnosis
  - topic-constrained diagnosis

The published paper describes this as repeated random subsampling validation, where one of four examples per MaE is randomly selected for training and another is selected for testing in each iteration. The paper repeats this process 100 times and reports that topic-constrained diagnosis improves performance.

## Improvement Over The Original Implementation

We keep the paper's method, with one reproducibility improvement:

> The randomized train/test assignments are materialized and saved with a fixed random seed before any model is run.

This means every model receives exactly the same randomized batches. It also makes the experiment auditable: we can inspect which example was used for training and testing for every MaE in every trial.

This does not change the statistical design. It only makes the randomization reproducible.

## How Many Times Is Each Misconception Diagnosed?

For the full paper-style diagnosis workflow:

```text
100 trials x 1 test example per misconception per trial = 100 diagnoses per misconception per model per condition
```

With 55 misconceptions:

```text
55 misconceptions x 100 trials = 5,500 diagnosis decisions per model per condition
```

If both conditions are run:

```text
5,500 cross-topic diagnoses
+ 5,500 topic-constrained diagnoses
= 11,000 diagnosis decisions per model
```

For 3 models:

```text
11,000 x 3 = 33,000 diagnosis decisions
```

## How Are Misconceptions Randomized?

For each trial:

1. Group the 220 diagnostic examples by `Misconception ID`.
2. For each misconception group, randomly sample two different examples from the four available examples.
3. Use the first sampled example as the training example.
4. Use the second sampled example as the test example.
5. Repeat this for all 55 misconceptions.

The script uses a fixed random seed by default:

```text
20240701
```

This creates a reproducible version of repeated random subsampling.

## Workflow Summary

```text
data/data.json
        |
        v
build_misconception_first_paper_inputs.py
        |
        v
outputs/misconception_first/paper_repeated_random_100/
        |
        +-- inputs/prompt_batches.jsonl
        +-- inputs/trial_assignments.csv
        +-- run_config.json
        |
        v
model provider calls
        |
        v
raw_model_responses/model_responses.jsonl
        |
        v
parsed_diagnoses/diagnoses.csv
        |
        v
scored/diagnosis_scores.csv
```

## Step 1: Build Paper-Style Prompt Inputs

Run from the repository root:

```bash
python remediation-experiments/scripts/build_misconception_first_paper_inputs.py
```

Default output folder:

```text
remediation-experiments/outputs/misconception_first/paper_repeated_random_100/
```

The script creates:

- `inputs/prompt_batches.jsonl`
- `inputs/trial_assignments.csv`
- `run_config.json`
- empty folders for raw responses, parsed diagnoses, scores, and logs

## Step 2: Prompt Batch Inputs

Each line in `inputs/prompt_batches.jsonl` is one model-ready batch prompt.

Required fields:

- `run_id`
- `condition`
- `trial`
- `prompt_batch_id`
- `topic`
- `diagnoses_expected`
- `test_items`
- `prompt`

For cross-topic diagnosis:

```text
100 prompt batches per model
55 expected diagnoses per prompt
5,500 diagnosis decisions per model
```

For topic-constrained diagnosis:

```text
800 prompt batches per model
topic-sized diagnosis batches
5,500 diagnosis decisions per model
```

When both conditions are generated:

```text
900 prompt batches per model
11,000 diagnosis decisions per model
```

## Step 3: Trial Assignments

`inputs/trial_assignments.csv` records the exact randomized split.

Columns:

- `run_id`
- `condition`
- `trial`
- `prompt_batch_id`
- `topic`
- `misconception_id`
- `train_example_number`
- `test_example_number`

This file is the audit trail for randomization.

## Step 4: Model Computation Output

For each model, save one JSONL record per prompt batch to:

```text
outputs/misconception_first/<run_id>/raw_model_responses/model_responses.jsonl
```

Recommended fields:

- `run_id`
- `condition`
- `trial`
- `prompt_batch_id`
- `topic`
- `model_provider`
- `model_name`
- `prompt`
- `raw_response`
- `created_at`
- `temperature`

OpenAI runner:

```bash
python remediation-experiments/scripts/run_misconception_first_openai.py \
  --model gpt-4-turbo \
  --limit 2
```

Use `--limit 2` for a smoke test. Remove `--limit` for the full run.

Before running model calls, install dependencies and set the API key in your shell:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="..."
```

The runner resumes by default. If `model_responses.jsonl` already contains successful responses for a model, those prompt batches are skipped on the next run.

## Step 5: Parsed Diagnosis Output

Parse each batch response into one row per test example.

Save to:

```text
outputs/misconception_first/<run_id>/parsed_diagnoses/diagnoses.csv
```

Recommended fields:

- `run_id`
- `condition`
- `trial`
- `prompt_batch_id`
- `test_example_number`
- `topic`
- `gold_misconception_id`
- `predicted_misconception_id`
- `model_provider`
- `model_name`
- `parse_error`

## Step 6: Scored Diagnosis Output

Score exact matches and educator-accepted alternatives.

Save to:

```text
outputs/misconception_first/<run_id>/scored/diagnosis_scores.csv
```

Recommended fields:

- `exact_id_match`
- `topic_match`
- `human_accepts_alternative`
- `expert_review_category`
- `notes`

The expert review fields preserve the validation logic from the paper, where some model "errors" may be acceptable because multiple misconceptions match the same answer or one misconception is a subset of another.

## Optional Pilot

For a fast smoke test:

```bash
python remediation-experiments/scripts/build_misconception_first_paper_inputs.py \
  --run-id paper_smoke_test_2 \
  --iterations 2
```

This produces:

```text
2 trials x 55 misconceptions = 110 diagnoses per condition per model
```

Use the full 100-trial run for reportable results.
