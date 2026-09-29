"""Opt-in integration tests; download a pinned public model when explicitly enabled."""
import os
from pathlib import Path
import pytest
from pocketforge.core import load_model, load_task, train


@pytest.mark.skipif(os.environ.get('POCKETFORGE_NEURAL_TEST') != '1', reason='opt-in model download')
def test_neural_finetune_and_offline_reload(tmp_path, monkeypatch):
    pytest.importorskip('sentence_transformers')
    task = Path(__file__).parents[1] / 'examples/support/task.yaml'
    run = tmp_path / 'run'
    manifest = train(task, run, neural=True, epochs=1)
    assert manifest['neural']['selected_epoch'] == 1
    assert len(manifest['neural']['history']) == 1
    monkeypatch.setenv('HF_HUB_OFFLINE', '1')
    model, _ = load_model(run, 'minilm')
    _, data, _ = load_task(task)
    texts = [r['text'] for r in data['validation']]
    before = model.predict(texts).tolist()
    reloaded, _ = load_model(run, 'minilm')
    assert reloaded.predict(texts).tolist() == before
    from pocketforge.core import score
    assert score(manifest['task']['labels'], [r['label'] for r in data['validation']], before) == manifest['validation']['minilm']
