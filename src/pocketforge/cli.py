import argparse
import json
import sys
from pathlib import Path

import yaml

from .core import ContractError, evaluate, load_task, predict, predict_many, read_prediction_rows, train
from .benchmark import benchmark


DEFAULT_LABELS = ["billing", "technical"]


def parse_labels(value):
    labels = [label.strip() for label in value.split(",") if label.strip()]
    if len(labels) < 2 or len(set(labels)) != len(labels):
        raise ContractError("--labels must contain at least two unique comma-separated labels.")
    return labels


def starter_rows(labels):
    examples = {
        "billing": ["There is an unexpected charge on my invoice", "Please send a refund for the duplicate payment"],
        "technical": ["The app crashes when I upload a file", "I cannot sign in after resetting my password"],
        "cancellation": ["Please cancel my subscription", "I want to close my account"],
        "shipping": ["Where is my package right now", "My delivery is late and tracking has not updated"],
        "refund": ["I want a refund for my damaged order", "Please return my money for this purchase"],
        "account": ["I cannot log into my account", "Please reset my password"],
    }
    split_rows = {"train": [], "validation": [], "test": []}
    for label in labels:
        sample = examples.get(label, [f"Example request for {label}", f"Another {label} message"])
        split_rows["train"].append({"text": sample[0], "label": label, "group": f"{label}-train-1"})
        split_rows["train"].append({"text": sample[1], "label": label, "group": f"{label}-train-2"})
        split_rows["validation"].append({"text": f"Validation example for {label}", "label": label, "group": f"{label}-validation-1"})
        split_rows["test"].append({"text": f"Test example for {label}", "label": label, "group": f"{label}-test-1"})
    return split_rows


def write_rows(path, rows, output_format):
    if output_format == "jsonl":
        lines = [json.dumps(row, ensure_ascii=False) for row in rows]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    import csv
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["text", "label", "group"])
        writer.writeheader()
        writer.writerows(rows)


def write_starter_task(destination, *, name="starter-intents", labels=None, output_format="jsonl"):
    labels = labels or DEFAULT_LABELS
    if output_format not in {"jsonl", "csv"}:
        raise ContractError("--format must be jsonl or csv.")
    if not name or name != name.strip():
        raise ContractError("--name must be a nonempty trimmed string.")
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ContractError("Destination already exists and is not empty; choose a new folder.")
    destination.mkdir(parents=True, exist_ok=True)
    suffix = output_format
    task = {
        "name": name,
        "labels": labels,
        "splits": {"train": f"train.{suffix}", "validation": f"validation.{suffix}", "test": f"test.{suffix}"},
    }
    (destination / "task.yaml").write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")
    rows = starter_rows(labels)
    for split, split_rows in rows.items():
        write_rows(destination / f"{split}.{suffix}", split_rows, output_format)
    readme = destination / "README.md"
    readme.write_text(
        f"# {name}\n\n"
        "Replace these starter examples with your own labeled text before making product decisions.\n\n"
        "```bash\n"
        f"python -m pocketforge.cli validate {destination / 'task.yaml'}\n"
        f"python -m pocketforge.cli train {destination / 'task.yaml'} --output runs/{name}\n"
        f"python -m pocketforge.cli evaluate runs/{name} --task {destination / 'task.yaml'}\n"
        "```\n",
        encoding="utf-8",
    )
    files = ["task.yaml", *(f"{split}.{suffix}" for split in ["train", "validation", "test"]), "README.md"]
    return {
        "created": str(destination),
        "files": files,
        "next": [
            f"python -m pocketforge.cli validate {destination / 'task.yaml'}",
            f"python -m pocketforge.cli train {destination / 'task.yaml'} --output runs/{name}",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate local text classifiers.")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a starter task folder")
    init.add_argument("destination")
    init.add_argument("--name", default="starter-intents")
    init.add_argument("--labels", default=",".join(DEFAULT_LABELS), help="comma-separated labels")
    init.add_argument("--format", choices=["jsonl", "csv"], default="jsonl")
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
    input_group = prediction.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text")
    input_group.add_argument("--input", help="CSV or JSONL file with a text column")
    prediction.add_argument("--output", help="write batch predictions to this JSON file")
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
            result = write_starter_task(args.destination, name=args.name, labels=parse_labels(args.labels), output_format=args.format)
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
            if args.input:
                result = predict_many(args.run, read_prediction_rows(args.input))
                if args.output:
                    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            else:
                result = {"label": predict(args.run, args.text)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ContractError, OSError, ValueError, ImportError, yaml.YAMLError) as error:
        print(f"pocketforge: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
