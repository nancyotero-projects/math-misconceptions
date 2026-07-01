# Experiment Plan: LLM Recommendations for Overcoming Mathematical Misconceptions

## Study Goal

Evaluate how different LLMs recommend instructional responses for overcoming mathematical misconceptions, given evidence of a consistent student error pattern, and compare those recommendations with research-based recommendations.

## Core Research Question

How well do LLM-generated instructional recommendations align with mathematics education research when a student demonstrates a persistent misconception?

## Subquestions

1. Do LLMs address the underlying misconception or only the surface error?
2. Do LLMs recommend conceptual remediation or procedural correction?
3. Do diagnosis-first prompts improve recommendation quality?
4. Do research-aligned prompts increase use of representations, counterexamples, and student reasoning?
5. Are LLMs weaker for some misconception families, especially ratios and proportional reasoning?
6. How much do models differ in research alignment, specificity, and pedagogical usefulness?

## Experimental Unit

Each case should include:

- Misconception ID
- Misconception description
- Several examples of consistent student mistakes
- Research-based recommendation
- Gold student-facing activity or task
- Correct and incorrect reference responses
- Topic, when available

## Prompt Conditions

1. Baseline: help the student overcome the mistake.
2. Diagnosis-first: infer the misconception before recommending an intervention.
3. Research-aligned: recommend a response consistent with math education research.

Optional later conditions:

- Teacher-facing guidance
- Student-facing feedback
- No-giveaway tutor
- Few-shot research-grounded prompt
- Topic-constrained prompt

## Model Conditions

Start with 3-4 models:

- One strong frontier model
- One cheaper or faster model
- One open-weight model, if relevant
- One education-specialized or fine-tuned model, if available

Use deterministic or low-temperature settings for the first pass.

## Pilot

Use 20 misconception cases.

Suggested coverage:

- Number sense
- Number operations
- Fractions
- Ratios and proportional reasoning
- Patterns/functions
- Algebraic representations
- Variables/expressions/equations

For 20 cases, 3 prompt conditions, and 4 models, the pilot produces 240 responses.

## Full Study

Use all 55 misconceptions once the pilot rubric and scripts are stable.

## Main Hypotheses

1. LLMs will often generate mathematically plausible but pedagogically shallow recommendations.
2. Diagnosis-first prompts will improve alignment with the target misconception.
3. Research-aligned prompts will increase the use of representations and conceptual tasks.
4. LLMs will over-recommend procedural rules, especially for proportional reasoning.
5. Larger models will not always be the most research-aligned.
6. Recommendation quality will vary substantially by misconception family.

## Primary Outcomes

- Mean rubric score by model and prompt condition
- Research-alignment score by model and prompt condition
- Rate of procedural-only recommendations
- Rate of concrete activity/task generation
- Rate of representation use
- Topic-level variation

## Analysis Plan

1. Score all outputs with the human rubric.
2. Compute per-dimension means by model, prompt, and topic.
3. Compare baseline vs diagnosis-first vs research-aligned conditions.
4. Tag common failure modes.
5. Select qualitative examples showing strong, weak, and misleading recommendations.

