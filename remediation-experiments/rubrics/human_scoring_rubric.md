# Human Scoring Rubric

Score each model response from 1 to 5 on each dimension.

Use `1` for absent or harmful, `3` for partially useful, and `5` for strong, accurate, and instructionally useful.

## Dimensions

### 1. Misconception Targeting

Does the response address the actual misconception rather than only the surface error?

- 1: Misses or misidentifies the misconception.
- 3: Partially addresses the misconception but remains broad or vague.
- 5: Clearly targets the underlying misconception.

### 2. Research Alignment

Does the recommendation align with the gold research-based recommendation?

- 1: Contradicts or ignores the research-based recommendation.
- 3: Some overlap, but important elements are missing.
- 5: Strongly matches the research-based recommendation.

### 3. Conceptual Remediation

Does the response build conceptual understanding instead of only giving a rule or procedure?

- 1: Only gives a rule, shortcut, or answer.
- 3: Includes some conceptual explanation but mostly procedural.
- 5: Designs a conceptual path for revising the student's thinking.

### 4. Mathematical Correctness

Is the mathematics accurate?

- 1: Contains incorrect mathematics.
- 3: Mostly correct but imprecise or potentially confusing.
- 5: Fully correct and clear.

### 5. Specificity and Actionability

Could a teacher or tutor use the recommendation directly?

- 1: Generic advice only.
- 3: Gives a plausible direction but lacks a concrete task.
- 5: Provides a concrete instructional move, activity, or next problem.

### 6. Use of Representations

Does the response use appropriate representations when useful?

- 1: No representation when one is needed.
- 3: Mentions a representation but does not use it meaningfully.
- 5: Uses an appropriate representation such as number lines, fraction strips, area models, ratio tables, graphs, manipulatives, or diagrams.

### 7. Attention to Student Reasoning

Does the response engage with why the student likely made the error?

- 1: Treats the student answer as simply wrong.
- 3: Gives a possible reason but does not use it instructionally.
- 5: Uses the student's reasoning as the starting point for remediation.

### 8. Pedagogical Usefulness

Would this recommendation be useful in a real classroom or tutoring setting?

- 1: Not useful, misleading, or impractical.
- 3: Somewhat useful but needs teacher repair.
- 5: Clear, usable, and instructionally appropriate.

## Tags

Apply all that fit:

- `procedural_rule_only`
- `conceptual_explanation`
- `concrete_activity`
- `uses_visual_representation`
- `uses_counterexample`
- `uses_multiple_representations`
- `asks_diagnostic_question`
- `gives_answer_too_quickly`
- `misidentifies_misconception`
- `generic_advice`
- `research_aligned`
- `student_centered`
- `teacher_facing`

