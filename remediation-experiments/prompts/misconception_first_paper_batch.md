# Misconception-First Paper-Style Batch Prompt

This prompt mirrors the diagnosis prompt used in the MaE benchmark paper.

It is generated programmatically because each trial has a randomized training set and test set.

Prompt structure:

```text
You are an expert tutor on middle school math with years of experience understanding students' most common math mistakes.
You have identified a set of common mistakes called Misconceptions, and you use them to diagnose student's answers to math questions.
You have also developed a labeled dataset of question items, and diagnosed them with the appropriate misconception ID.

Using the set of misconceptions and the labeled dataset, your task today is to take some items of unlabeled data and provide a diagnosis for each unlabeled item.

Here is the list of misconceptions together with a brief description:

Train Example 1
Question:
...
Answer:
...
Diagnosis: MaE##
Misconception Description:
...
Topic of Misconception:
...

Below are the unlabeled Test Examples. For each Test Example, provide only the most likely Misconception ID for the Test Answer from the provided list.
Do not write anything else but a sequence of lines of the format $Test_Example_Number, $Misconception_ID

Test Example 1:
Question:
...
Test Answer:
...
```

The generated prompt batches are saved to:

```text
remediation-experiments/outputs/misconception_first/<run_id>/inputs/prompt_batches.jsonl
```

