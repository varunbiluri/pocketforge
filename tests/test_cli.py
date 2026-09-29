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
    assert payload["files"] == ["task.yaml", "train.jsonl", "validation.jsonl", "test.jsonl"]

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
