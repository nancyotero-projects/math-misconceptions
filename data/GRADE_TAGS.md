# Grade-level tags

The existing `data/data.json` contains all 55 misconceptions and 220 original
diagnostic examples. Each record now has two additional fields; all original
questions, answers, descriptions, explanations, references and image identifiers
are preserved.

## Fields

`grade_tags` contains arrays of grade strings:

- `misconception`: union of the grades assigned to this misconception's four
  diagnostic examples. This summarizes its actual example coverage; it is not
  a claim that the whole misconception is first taught in each listed grade.
- `example`: best-fit Common Core grade for the supplied task as written.
- `question`: same tag as the example, explicitly available for question displays.
- `correct_answer`: same tag as the example.
- `incorrect_answer`: same tag as the example. An error does not change the
  grade of the task or imply anything about a student's enrolled grade.

Values are strings `"1"` through `"8"`, or `"HS"` for high school.
The validator also permits `"K"` for future entries.
Common Core does not assign high-school content to a universal grade 9, 10, 11
or 12, so no such precision is invented.

`grade_alignment` contains `framework`, `status: "inferred"`,
`standard_codes`, and an explanatory `note`.
Codes apply to the example. Misconception-level grades are derived from its
examples, including when a family has a broad or imperfect source label.

After the second review, `grade_alignment` also includes:
- `match_type`: `direct`, `closest_match`, `extension`, or `ambiguous`.
- `requires_grade_review`: true for unresolved ambiguous items.
- `reviewed_on` and `source_urls`: review date and official domain references.
- `source_quality_note` where a source defect was observed (original text is untouched).

A direct match means the cited standard supports the task's mathematical demand,
not that the entire standard is assessed or that the answer key is correct.
Closest matches and extensions are instructional judgments. Nine ambiguous
records retain provisional tags and require author review before those tags
are treated as definitive. The image files themselves were not visually
re-audited; this review used the text, image descriptions and source answers.
See [the review log](GRADE_TAG_REVIEW.json) for all 16 changed example grades,
26 revised standard mappings and unresolved cases. This log compares the
second review with the initial local draft; neither draft was uploaded.

These are analyst-added curriculum annotations, not grades supplied by the
original authors or an official Common Core endorsement. They identify a
best-fit instructional level, not every later grade where review is useful.
Some tasks are extensions or closest matches; notes identify these cases.
The grade tags are not a mathematical validation or correction of the source
answer keys.

## Example

```json
{
  "Misconception ID": "MaE05",
  "Example Number": 3,
  "grade_tags": {
    "misconception": ["4", "5"],
    "example": ["5"],
    "question": ["5"],
    "correct_answer": ["5"],
    "incorrect_answer": ["5"]
  }
}
```

For an app, filter questions with
`row.grade_tags.example.includes("5")`; use
`row.grade_tags.misconception` when filtering whole misconception families.
Do not substitute the family union for the individual question tag.

## Alignment basis

Reviewed against the official
[Common Core State Standards for Mathematics](https://www.thecorestandards.org/wp-content/uploads/Math_Standards.pdf)
on November 22, 2026. Each record supplies the specific code.
A domain page can be constructed from its first two code segments:
`5.NF.B.4.a` → [Grade 5 fractions](https://www.thecorestandards.org/Math/Content/5/NF/);
`HSF.LE.A.1` → [High-school linear/exponential models](https://www.thecorestandards.org/Math/Content/HSF/LE/).

Important distinctions include first-quadrant versus negative-coordinate
plotting, unit-fraction versus general fraction division, numerical versus
variable expressions, and linear versus quadratic/exponential functions.
Original image-dependent and mathematically inconsistent examples retain their
content and receive scope notes where identified.

## Validation

Run from the repository root:

```sh
python scripts/validate_grade_tags.py
```

To additionally verify that only annotation fields changed, provide an original
dataset copy:

```sh
python scripts/validate_grade_tags.py --baseline /path/to/original-data.json
```

The validator checks record uniqueness, tag values, answer inheritance,
standard-to-grade consistency, and consistent family unions. The optional
baseline comparison checks every original field and record order.

This change tags the canonical 220 diagnostic records in `data/data.json`.
The original recommendation workbook, processed remediation cases, experiment
outputs, and images remain in their existing repository locations; their
separate activities have not been given unreviewed inherited grade tags.

