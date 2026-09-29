import argparse
import json
import sys
from pathlib import Path

import yaml

from .core import ContractError, evaluate, load_task, predict, train
from .benchmark import benchmark


STARTER_TASK = """name: starter-intents
labels:
  - billing
  - technical
splits:
  train: train.jsonl
  validation: validation.jsonl
  test: test.jsonl
"""

STARTER_SPLITS = {
    "train.jsonl": [
        {"text": "There is an unexpected charge on my invoice", "label": "billing", "group": "b1"},
        {"text": "Please send a refund for the duplicate payment", "label": "billing", "group": "b2"},
        {"text": "The app crashes when I upload a file", "label": "technical", "group": "t1"},
        {"text": "I cannot sign in after resetting my password", "label": "technical", "group": "t2"},
    ],
    "validation.jsonl": [
        {"text": "My card was charged twice", "label": "billing", "group": "bv1"},
        {"text": "The dashboard shows an error page", "label": "technical", "group": "tv1"},
    ],
    "test.jsonl": [
        {"text": "I need help with a wrong invoice", "label": "billing", "group": "bt1"},
        {"text": "The export button is broken", "label": "technical", "group": "tt1"},
    ],
}


def write_starter_task(destination):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ContractError("Destination already exists and is not empty; choose a new folder.")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "task.yaml").write_text(STARTER_TASK, encoding="utf-8")
    for filename, rows in STARTER_SPLITS.items():
        lines = [json.dumps(row, ensure_ascii=False) for row in rows]
        (destination / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "created": str(destination),
        "files": ["task.yaml", *STARTER_SPLITS],
        "next": [
            f"python -m pocketforge.cli validate {destination / 'task.yaml'}",
            f"python -m pocketforge.cli train {destination / 'task.yaml'} --output runs/starter-intents",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate local text classifiers.")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a starter task folder")
    init.add_argument("destination")
    validate = commands.add_parser("validate")
    validate.add_argument("task")
    training = commands.add_parser("train")
    training.add_argument("task")
    training.add_argument("--output", required=True)
    training.add_argument("--neural", action="store_true")
    training.add_argument("--epochs", type=int, default=0)
    evaluation = commands.add_parser("evaluate")
    evaluation.add_argument("run")
    evaluation.add_argument("--task", required=True)
    evaluation.add_argument("--predictions")
    prediction = commands.add_parser("predict")
    prediction.add_argument("run")
    prediction.add_argument("--text", required=True)
    timing = commands.add_parser("benchmark")
    timing.add_argument("run")
    timing.add_argument("--task", required=True)
    timing.add_argument("--batch-size", type=int, default=1)
    timing.add_argument("--repeats", type=int, default=20)
    timing.add_argument("--warmup", type=int, default=3)
    cost = commands.add_parser("cost")
    cost.add_argument("scenario")
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = write_starter_task(args.destination)
        elif args.command == "validate":
            _, data, hashes = load_task(args.task)
            result = {"counts": {key: len(rows) for key, rows in data.items()}, "sha256": hashes}
        elif args.command == "train":
            result = train(args.task, args.output, neural=args.neural, epochs=args.epochs)
        elif args.command == "evaluate":
            result = evaluate(args.run, args.task, predictions=args.predictions)
        elif args.command == "benchmark":
            result = benchmark(args.run, args.task, batch_size=args.batch_size,
                               repeats=args.repeats, warmup=args.warmup)
        elif args.command == "cost":
            from .reports import costs
            result = costs(args.scenario)
        else:
            result = {"label": predict(args.run, args.text)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ContractError, OSError, ValueError, ImportError, yaml.YAMLError) as error:
        print(f"pocketforge: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
