import json
import shutil
from pathlib import Path

import pytest

from pocketforge.core import ContractError, evaluate, load_task, predict, score, train


@pytest.fixture
def task(tmp_path):
    source = Path(__file__).parents[1] / "examples" / "support"
    shutil.copytree(source, tmp_path / "data")
    return tmp_path / "data" / "task.yaml"


def test_metrics_match_hand_calculation():
    result = score(["a", "b"], ["a", "a", "b", "b"], ["a", "b", "b", "b"])
    assert result["accuracy"] == 0.75
    assert result["macro_f1"] == pytest.approx((2 / 3 + 0.8) / 2)
    assert result["confusion_matrix"] == [[1, 1], [0, 2]]


def test_labels_do_not_collide_with_metric_names():
    result = score(["accuracy", "macro avg"], ["accuracy", "macro avg"], ["accuracy", "macro avg"])
    assert result["macro_f1"] == 1.0
    assert result["per_class"]["accuracy"]["support"] == 1


def test_roundtrip_and_holdout(task, tmp_path):
    run = tmp_path / "run"
    manifest = train(task, run)
    assert "test" not in manifest["validation"]
    assert manifest["counts"] == {"train": 12, "validation": 6, "test": 6}
    before = predict(run, "Please cancel my subscription")
    report = evaluate(run, task)
    assert predict(run, "Please cancel my subscription") == before
    assert report["selected_on_validation"] == manifest["selected_model"]
    assert (run / "report.html").exists()
    with pytest.raises(ContractError, match="already exists"):
        train(task, run)


def test_changed_test_labels_do_not_change_selection(task, tmp_path):
    first = train(task, tmp_path / "first")
    test_path = task.parent / "test.jsonl"
    rows = [json.loads(line) for line in test_path.read_text().splitlines()]
    for row in rows:
        row["label"] = "technical"
    test_path.write_text("\n".join(json.dumps(row) for row in rows))
    second = train(task, tmp_path / "second")
    assert first["validation"] == second["validation"]
    assert first["selected_model"] == second["selected_model"]
    with pytest.raises(ContractError, match="changed"):
        evaluate(tmp_path / "first", task)


@pytest.mark.parametrize("row,match", [
    ({"text": " PLEASE   CANCEL MY SUBSCRIPTION ", "label": "cancellation"}, "duplicate"),
    ({"text": "Something new", "label": "unknown"}, "label"),
    ({"text": "", "label": "billing"}, "text"),
    ({"text": "Something new", "label": "billing", "secret": 1}, "expected"),
])
def test_invalid_inputs(task, row, match):
    with (task.parent / "test.jsonl").open("a") as stream:
        stream.write(json.dumps(row) + "\n")
    with pytest.raises(ContractError, match=match):
        load_task(task)


def test_group_leakage(task):
    for split in ["train", "test"]:
        path = task.parent / f"{split}.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[0]["group"] = "same-customer"
        path.write_text("\n".join(json.dumps(row) for row in rows))
    with pytest.raises(ContractError, match="group crosses"):
        load_task(task)


def test_artifact_tampering(task, tmp_path):
    run = tmp_path / "run"
    manifest = train(task, run)
    (run / f"{manifest['selected_model']}.joblib").write_bytes(b"invalid")
    with pytest.raises(ContractError, match="checksum"):
        predict(run, "A new message")


def test_csv_and_missing_class(task):
    import csv
    import yaml
    config = yaml.safe_load(task.read_text())
    for split in config["splits"]:
        source = task.parent / config["splits"][split]
        rows = [json.loads(line) for line in source.read_text().splitlines()]
        with source.with_suffix(".csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["text", "label"])
            writer.writeheader()
            writer.writerows(rows)
        config["splits"][split] = f"{split}.csv"
    task.write_text(yaml.safe_dump(config))
    assert len(load_task(task)[1]["train"]) == 12
    config["labels"].append("missing")
    task.write_text(yaml.safe_dump(config))
    with pytest.raises(ContractError, match="Every declared label"):
        load_task(task)


@pytest.mark.parametrize('example', ['documents', 'intents'])
def test_additional_task_without_core_changes(tmp_path, example):
    task = Path(__file__).parents[1] / 'examples' / example / 'task.yaml'
    run = tmp_path / example
    train(task, run)
    assert evaluate(run, task)['split'] == 'test'


def test_limits_versions_and_missing_support(task, tmp_path):
    run = tmp_path / 'run'
    train(task, run)
    with pytest.raises(ContractError, match='text'):
        predict(run, 'x' * 10001)
    manifest_path = run / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['versions']['scikit-learn'] = '0.invalid'
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ContractError, match='version'):
        predict(run, 'message')
    result = score(['a', 'b'], ['a'] * 10, ['a'] * 10)
    assert result['accuracy'] == 1
    assert result['macro_f1'] == 0.5
    assert result['absent_reference_labels'] == ['b']
