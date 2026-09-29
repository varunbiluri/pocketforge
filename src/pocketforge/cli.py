import argparse
import json
import sys

import yaml

from .core import ContractError, evaluate, load_task, predict, train


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate local text classifiers.")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("task")
    training = commands.add_parser("train")
    training.add_argument("task")
    training.add_argument("--output", required=True)
    evaluation = commands.add_parser("evaluate")
    evaluation.add_argument("run")
    evaluation.add_argument("--task", required=True)
    prediction = commands.add_parser("predict")
    prediction.add_argument("run")
    prediction.add_argument("--text", required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            _, data, hashes = load_task(args.task)
            result = {"counts": {key: len(rows) for key, rows in data.items()}, "sha256": hashes}
        elif args.command == "train":
            result = train(args.task, args.output)
        elif args.command == "evaluate":
            result = evaluate(args.run, args.task)
        else:
            result = {"label": predict(args.run, args.text)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ContractError, OSError, ValueError, yaml.YAMLError) as error:
        print(f"pocketforge: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
