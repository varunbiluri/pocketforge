"""Explicit data contracts and a reproducible CPU baseline workflow."""

import csv
import hashlib
import io
import json
import platform
import shutil
import tempfile
import unicodedata
from importlib.metadata import version
from pathlib import Path

import joblib
import yaml
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.pipeline import make_pipeline


class ContractError(ValueError):
    """An input does not meet the documented contract."""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_task(path):
    path = Path(path).resolve()
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != {"name", "labels", "splits"}:
        raise ContractError("Task must contain exactly name, labels, and splits.")
    if not isinstance(config["name"], str) or not config["name"].strip():
        raise ContractError("name must be a nonempty string.")
    labels = config["labels"]
    if (not isinstance(labels, list) or len(labels) < 2
            or any(not isinstance(x, str) or not x or x != x.strip() for x in labels)
            or len(set(labels)) != len(labels)):
        raise ContractError("labels must contain at least two unique, nonempty, trimmed strings.")
    splits = config["splits"]
    if not isinstance(splits, dict) or set(splits) != {"train", "validation", "test"}:
        raise ContractError("splits must contain exactly train, validation, and test.")
    data, hashes, seen_text, seen_group = {}, {}, {}, {}
    for split, filename in splits.items():
        if not isinstance(filename, str) or not filename:
            raise ContractError(f"{split}: expected a file path.")
        source = (path.parent / filename).resolve()
        raw = source.read_bytes()
        hashes[split] = digest(raw)
        text = raw.decode("utf-8")
        if source.suffix == ".jsonl":
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        elif source.suffix == ".csv":
            reader = csv.DictReader(io.StringIO(text))
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)):
                raise ContractError(f"{split}: duplicate CSV column names.")
            rows = list(reader)
        else:
            raise ContractError(f"{split}: use .csv or .jsonl.")
        if not rows:
            raise ContractError(f"{split}: empty dataset.")
        for index, row in enumerate(rows, 1):
            where = f"{split} row {index}"
            if not isinstance(row, dict) or not {"text", "label"} <= row.keys() or row.keys() - {"text", "label", "group"}:
                raise ContractError(f"{where}: expected text, label, and optional group only.")
            value = row["text"]
            if not isinstance(value, str) or not value.strip() or len(value) > 10000:
                raise ContractError(f"{where}: text must have 1–10000 characters and not be blank.")
            if not isinstance(row["label"], str) or row["label"] not in labels:
                raise ContractError(f"{where}: unknown or invalid label.")
            key = normalized(value)
            if key in seen_text:
                raise ContractError(f"{where}: duplicate normalized text (also in {seen_text[key]}).")
            seen_text[key] = where
            group = row.get("group", "")
            if not isinstance(group, str):
                raise ContractError(f"{where}: group must be a string.")
            if group:
                if group in seen_group and seen_group[group] != split:
                    raise ContractError(f"{where}: group crosses split boundaries.")
                seen_group[group] = split
        data[split] = rows
    if set(row["label"] for row in data["train"]) != set(labels):
        raise ContractError("Every declared label must occur in train.")
    return config, data, hashes


def score(labels, truth, predictions):
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predictions, labels=labels, zero_division=0)
    return {
        "accuracy": accuracy_score(truth, predictions),
        "macro_f1": float(f1.mean()),
        "per_class": {label: {"precision": float(precision[i]), "recall": float(recall[i]),
                              "f1-score": float(f1[i]), "support": int(support[i])}
                      for i, label in enumerate(labels)},
        "confusion_matrix": confusion_matrix(truth, predictions, labels=labels).tolist(),
        "label_order": labels,
        "absent_reference_labels": [label for label in labels if label not in truth],
    }


def train(task, output, *, neural=False, epochs=0):
    if not isinstance(epochs, int) or epochs < 0 or (epochs and not neural):
        raise ContractError("epochs must be nonnegative and requires neural=True when positive.")
    config, data, hashes = load_task(task)
    output = Path(output).resolve()
    if output.exists():
        raise ContractError("Output already exists; choose a new run directory.")
    x = [r["text"] for r in data["train"]]
    y = [r["label"] for r in data["train"]]
    vx = [r["text"] for r in data["validation"]]
    vy = [r["label"] for r in data["validation"]]
    models = {
        "majority": DummyClassifier(strategy="most_frequent"),
        "tfidf_linear": make_pipeline(
            TfidfVectorizer(analyzer="char", ngram_range=(1, 5), max_features=50000),
            LogisticRegression(max_iter=1000, random_state=0),
        ),
    }
    if neural:
        from .neural import MiniLMClassifier
        models["minilm"] = MiniLMClassifier(epochs=epochs)
    results = {}
    for name, model in models.items():
        if name == "minilm":
            model.fit(x, y, validation=(vx, vy))
        else:
            model.fit(x, y)
        results[name] = score(config["labels"], vy, model.predict(vx).tolist())
    # Stable tie: prefer the simpler majority classifier.
    winner = max(models, key=lambda name: results[name]["macro_f1"])
    manifest = {
        "format_version": 1, "task": config, "dataset_sha256": hashes,
        "counts": {key: len(rows) for key, rows in data.items()},
        "selected_model": winner, "selection": "validation macro-F1; majority wins ties",
        "validation": results,
        "versions": {name: version(name) for name in ["pocketforge", "scikit-learn", "numpy", "joblib", "PyYAML"]},
        "python": platform.python_version(), "platform": platform.platform(), "seed": 0,
        "recipe": {"tfidf": {"analyzer": "char", "ngram_range": [1, 5], "max_features": 50000},
                   "logistic": {"C": 1.0, "max_iter": 1000, "random_state": 0},
                   "majority": "most_frequent"},
    }
    if neural:
        from .neural import MODEL, REVISION
        manifest["neural"] = {"model": MODEL, "revision": REVISION, "license": "Apache-2.0",
                              "epochs": epochs, "selected_epoch": models["minilm"].selected_epoch,
                              "history": models["minilm"].history, "max_tokens": 256,
                              "device": "cpu", "threads": 4, "batch_size": 32, "learning_rate": 2e-5}
        manifest["versions"].update({n: version(n) for n in ["sentence-transformers", "torch", "transformers"]})
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".pocketforge-", dir=output.parent))
    try:
        for name, model in models.items():
            artifact = staging / f"{name}.joblib"
            if name == "minilm":
                model.save(staging / name)
            else:
                joblib.dump(model, artifact)
        manifest["model_sha256"] = {name: artifact_digest(staging, name) for name in models}
        write_json(staging / "manifest.json", manifest)
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return manifest


def load_model(run, name=None):
    run = Path(run)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format_version") != 1:
        raise ContractError("Unsupported artifact format.")
    name = name or manifest["selected_model"]
    if name not in {"majority", "tfidf_linear", "minilm"}:
        raise ContractError("Unknown model name.")
    artifact = run / f"{name}.joblib"
    if artifact_digest(run, name) != manifest["model_sha256"][name]:
        raise ContractError("Model checksum mismatch.")
    if manifest["versions"]["scikit-learn"] != version("scikit-learn"):
        raise ContractError("Use the scikit-learn version recorded in manifest.json.")
    # joblib is executable serialization: only load artifacts from trusted sources.
    if name == "minilm":
        from .neural import MiniLMClassifier
        for dependency in ["sentence-transformers", "torch", "transformers"]:
            if version(dependency) != manifest["versions"][dependency]:
                raise ContractError(f"Use the recorded {dependency} version.")
        return MiniLMClassifier.load(run / name), manifest
    return joblib.load(artifact), manifest


def artifact_files(run, name):
    root = Path(run)
    return sorted((root / name).rglob("*")) if name == "minilm" else [root / f"{name}.joblib"]


def artifact_digest(run, name):
    if name != "minilm":
        return digest((Path(run) / f"{name}.joblib").read_bytes())
    entries = [(str(p.relative_to(run)), digest(p.read_bytes())) for p in artifact_files(run, name) if p.is_file()]
    return digest(json.dumps(entries).encode())


def predict(run, text):
    if not isinstance(text, str) or not text.strip() or len(text) > 10000:
        raise ContractError("text must have 1–10000 characters and not be blank.")
    model, _ = load_model(run)
    return str(model.predict([text])[0])


def evaluate(run, task, *, predictions=None):
    config, data, hashes = load_task(task)
    _, manifest = load_model(run)
    if config != manifest["task"] or hashes != manifest["dataset_sha256"]:
        raise ContractError("Task or dataset changed since training; create a new run.")
    rows = data["test"]
    results = {}
    for name in manifest["validation"]:
        model, _ = load_model(run, name)
        predicted = model.predict([row["text"] for row in rows]).tolist()
        results[name] = score(config["labels"], [row["label"] for row in rows], predicted)
        results[name]["predictions"] = predicted
    if predictions is not None:
        from .reports import external_predictions
        external = external_predictions(predictions, rows, config["labels"])
        results["current_system"] = score(config["labels"], [row["label"] for row in rows], external)
        results["current_system"]["predictions"] = external
    report = {"split": "test", "selected_on_validation": manifest["selected_model"], "results": results}
    write_json(Path(run) / "report.json", report)
    from .reports import render_report
    render_report(Path(run) / "report.html", report)
    return report
