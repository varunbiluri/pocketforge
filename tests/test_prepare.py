import importlib.util
import io
from pathlib import Path

from pocketforge.core import load_task


def test_preparation_preserves_test_and_removes_conflicts(monkeypatch, tmp_path):
    source = Path(__file__).parents[1] / "scripts" / "prepare_banking77.py"
    spec = importlib.util.spec_from_file_location("prepare_banking77", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    train = "text,category\n" + "".join(f"training {label} {i},{label}\n" for label in ["a", "b"] for i in range(6))
    train += "shared,a\nconflict,a\n"
    test = "text,category\nshared,a\nSHARED,a\nconflict,b\nother,b\n"
    raw = {"LICENSE": b"test license", "train.csv": train.encode(), "test.csv": test.encode()}
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda url, timeout: io.BytesIO(raw[url.rsplit('/', 1)[-1]]))
    result = module.prepare(tmp_path / "one")
    module.prepare(tmp_path / "two")
    assert len(result["removed"]) == 4
    config, data, _ = load_task(tmp_path / "one" / "task.yaml")
    assert [r["text"] for r in data["test"]] == ["shared", "other"]
    assert len(data["validation"]) == 2
    for path in (tmp_path / "one").iterdir():
        assert path.read_bytes() == (tmp_path / "two" / path.name).read_bytes()
