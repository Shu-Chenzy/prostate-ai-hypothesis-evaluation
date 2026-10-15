"""Send the questions in evaluation/tasks.csv to Claude and save the answers.

Run from the repository root after the notebook has written tasks.csv:

    pip install anthropic
    set ANTHROPIC_API_KEY=sk-ant-...          (Windows; use `export` on macOS/Linux)
    python evaluation/run_claude.py
    python evaluation/run_claude.py --model claude-haiku-5-5

Answers go to evaluation/responses_<model>.csv. Tasks already answered are skipped,
so an interrupted run can be restarted. Re-run the scoring cell in the notebook afterwards.
"""

import argparse
import json
import os
from pathlib import Path

import anthropic
import pandas as pd

HERE = Path(__file__).resolve().parent

SYSTEM = (
    "You are helping a prostate cancer biologist interpret gene expression data. "
    "Answer from your own knowledge and the information in the question; you do not have access to the dataset. "
    "Give your single best answer even when unsure. 'confidence' is your probability (0 to 1) that the answer is correct. "
    "Keep the rationale under 80 words."
)

# Models that accept server-side refusal fallbacks. The model that actually answered
# is recorded in `served_by`, so a fallback cannot silently change what is being evaluated.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"}


def output_schema(task):
    if task.scoring == "auto":
        answer = {"type": "string", "enum": task.answer_options.split("|")}
    else:
        answer = {"type": "string"}
    return {
        "type": "object",
        "properties": {
            "answer": answer,
            "confidence": {"type": "number"},
            "rationale": {"type": "string"},
        },
        "required": ["answer", "confidence", "rationale"],
        "additionalProperties": False,
    }


def ask(client, model, effort, task):
    prompt = task.question
    if task.scoring == "auto":
        prompt += "\n\nAnswer with exactly one of: " + ", ".join(task.answer_options.split("|"))
    else:
        prompt += "\n\nGive the answer in under 200 words."

    extra = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"} if model in FALLBACK_MODELS else {}
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": output_schema(task)}},
        **extra,
    )

    row = {"task_id": task.task_id, "model": model, "served_by": response.model,
           "stop_reason": response.stop_reason, "input_tokens": response.usage.input_tokens,
           "output_tokens": response.usage.output_tokens}
    if response.stop_reason == "refusal":
        return row | {"answer": "REFUSED", "confidence": None, "rationale": ""}
    text = next(b.text for b in response.content if b.type == "text")
    return row | json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="claude-opus-5-5")
    parser.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    args = parser.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first (https://console.anthropic.com/settings/keys).")

    tasks = pd.read_csv(HERE / "tasks.csv").fillna("")
    out = HERE / f"responses_{args.model}.csv"
    done = set(pd.read_csv(out).task_id) if out.exists() else set()

    client = anthropic.Anthropic()
    for task in tasks.itertuples():
        if task.task_id in done:
            continue
        try:
            row = ask(client, args.model, args.effort, task)
        except anthropic.BadRequestError as e:
            print(f"{task.task_id}: bad request, skipped ({e.message})")
            continue
        except anthropic.AuthenticationError:
            print("API key missing or invalid: set ANTHROPIC_API_KEY and re-run")
            break
        except anthropic.APIStatusError as e:
            print(f"{task.task_id}: API error {e.status_code}, stopping; re-run to resume")
            break
        except anthropic.APIConnectionError:
            print(f"{task.task_id}: connection error, stopping; re-run to resume")
            break
        pd.DataFrame([row]).to_csv(out, mode="a", header=not out.exists(), index=False)
        print(f"{task.task_id} {task.task_type:16s} {task.gene:10s} -> {str(row['answer'])[:60]}")

    print(f"saved to {out}")


if __name__ == "__main__":
    main()
