import json
import subprocess
import sys


def run_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "pocketforge.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def test_init_creates_valid_starter_task(tmp_path):
    destination = tmp_path / "starter"
    result = run_cli("init", str(destination))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["files"] == ["task.yaml", "train.jsonl", "validation.jsonl", "test.jsonl", "README.md"]

    validation = run_cli("validate", str(destination / "task.yaml"))
    assert validation.returncode == 0, validation.stderr
    counts = json.loads(validation.stdout)["counts"]
    assert counts == {"train": 4, "validation": 2, "test": 2}


def test_init_refuses_nonempty_destination(tmp_path):
    destination = tmp_path / "starter"
    destination.mkdir()
    (destination / "notes.txt").write_text("keep me")
    result = run_cli("init", str(destination))
    assert result.returncode == 2
    assert "not empty" in result.stderr


def test_bad_task_error_names_found_keys_and_initializer(tmp_path):
    bad = tmp_path / "task.yaml"
    bad.write_text("name: bad\ndata:\n  train: missing.csv\n")
    result = run_cli("validate", str(bad))
    assert result.returncode == 2
    assert "found data, name" in result.stderr
    assert "missing labels, splits" in result.stderr
    assert "unexpected data" in result.stderr
    assert "pocketforge init PATH" in result.stderr


def test_init_accepts_custom_labels_and_csv(tmp_path):
    destination = tmp_path / "custom"
    result = run_cli(
        "init",
        str(destination),
        "--name",
        "custom-routing",
        "--labels",
        "refund,shipping,account",
        "--format",
        "csv",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["files"] == ["task.yaml", "train.csv", "validation.csv", "test.csv", "README.md"]
    assert "runs/custom-routing" in payload["next"][1]

    task = (destination / "task.yaml").read_text()
    assert "custom-routing" in task
    assert "refund" in task
    assert (destination / "train.csv").read_text().splitlines()[0] == "text,label,group"

    validation = run_cli("validate", str(destination / "task.yaml"))
    assert validation.returncode == 0, validation.stderr
    counts = json.loads(validation.stdout)["counts"]
    assert counts == {"train": 6, "validation": 3, "test": 3}


def test_batch_prediction_jsonl_and_output_file(tmp_path):
    destination = tmp_path / "starter"
    run = tmp_path / "run"
    batch = tmp_path / "batch.jsonl"
    output = tmp_path / "predictions.json"
    assert run_cli("init", str(destination)).returncode == 0
    trained = run_cli("train", str(destination / "task.yaml"), "--output", str(run))
    assert trained.returncode == 0, trained.stderr
    batch.write_text('{"id":"a","text":"I need help with an invoice"}\n{"id":"b","text":"The app crashes"}\n')

    result = run_cli("predict", str(run), "--input", str(batch), "--output", str(output))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    written = json.loads(output.read_text())
    assert written == payload
    assert payload["selected_model"] in {"majority", "tfidf_linear"}
    assert [row["row_index"] for row in payload["predictions"]] == [0, 1]
    assert [row["id"] for row in payload["predictions"]] == ["a", "b"]
    assert all(row["prediction"] in {"billing", "technical"} for row in payload["predictions"])


def test_batch_prediction_rejects_bad_rows(tmp_path):
    destination = tmp_path / "starter"
    run = tmp_path / "run"
    batch = tmp_path / "batch.csv"
    assert run_cli("init", str(destination)).returncode == 0
    assert run_cli("train", str(destination / "task.yaml"), "--output", str(run)).returncode == 0
    batch.write_text("text\n\n")
    result = run_cli("predict", str(run), "--input", str(batch))
    assert result.returncode == 2
    assert "empty dataset" in result.stderr or "text must have" in result.stderr
