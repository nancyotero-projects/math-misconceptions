# Remediation Experiments

This folder extends the MaE misconception diagnosis benchmark into a remediation benchmark:

> Given evidence that a student is making a consistent mathematical mistake, how well do LLMs recommend instructional responses that align with mathematics education research?

The diagnosis benchmark asks whether a model can identify a misconception. These experiments ask whether a model can help a student overcome it.

## Folder Structure

```text
remediation-experiments/
  data/
    raw/          # Original recommendation workbook and untouched source files
    processed/    # Long-form CSV/JSONL files created by scripts
    splits/       # Pilot and full evaluation case lists
  docs/           # Experimental plan and paper notes
  prompts/        # Prompt templates used across models
  rubrics/        # Human scoring rubric and machine-readable schema
  scripts/        # Reproducible preparation, run, scoring, and analysis scripts
  notebooks/      # Colab notebooks that call scripts
  outputs/        # Model responses and scored results
```

## Recommended Workflow

1. Keep GitHub as the source of truth for data schemas, prompts, rubrics, scripts, and results.
2. Use Colab notebooks as the runnable interface for collaborators.
3. Store raw data unchanged in `data/raw/`.
4. Generate analysis-ready files in `data/processed/`.
5. Save model responses as JSONL and human scoring sheets as CSV.

## First Setup Step

From the repository root:

```bash
pip install -r requirements.txt
python remediation-experiments/scripts/prepare_dataset.py
```

This reads `data/raw/recommendation_dataset_original.xlsx` and creates:

- `data/processed/recommendations_long.csv`
- `data/processed/remediation_cases.jsonl`
- `data/splits/pilot_20.json`
- `data/splits/full_55.json`

## First Workflow: Misconception First

The first experiment stage diagnoses the misconception before any remediation recommendation is generated.

Workflow doc:

```text
docs/misconception_first_workflow.md
```

Build pilot prompt inputs:

```bash
python remediation-experiments/scripts/build_misconception_first_inputs.py
```

Default generated output folder:

```text
remediation-experiments/outputs/misconception_first/pilot_20/
```

This workflow creates model-ready prompt inputs in `inputs/prompt_inputs.jsonl`, then reserves separate folders for raw model responses, parsed diagnoses, scored diagnosis results, and logs.

## Initial Experimental Conditions

- Baseline prompt: ask the model to help the student.
- Diagnosis-first prompt: ask the model to identify the misconception before recommending help.
- Research-aligned prompt: ask the model to recommend an intervention consistent with mathematics education research.

## Initial Evaluation

Score each response with the rubric in `rubrics/human_scoring_rubric.md`.

Primary dimensions:

- Misconception targeting
- Research alignment
- Conceptual remediation
- Mathematical correctness
- Specificity and actionability
- Use of representations
- Attention to student reasoning
- Pedagogical usefulness
