import json
from pathlib import Path
import pytest
from pocketforge.core import ContractError, digest, evaluate, load_task, train
from pocketforge.reports import costs, external_predictions, render_report


def test_external_predictions_alignment(tmp_path):
    rows = [{'text': 'one', 'label': 'a'}, {'text': 'two', 'label': 'b'}]
    values = [{'row_index': i, 'text_sha256': digest(r['text'].encode()), 'prediction': r['label']} for i, r in enumerate(rows)]
    path = tmp_path / 'predictions.jsonl'
    path.write_text('\n'.join(json.dumps(v) for v in reversed(values)))
    assert external_predictions(path, rows, ['a', 'b']) == ['a', 'b']
    values[1]['text_sha256'] = 'wrong'
    path.write_text('\n'.join(json.dumps(v) for v in values))
    with pytest.raises(ContractError, match='sha256'):
        external_predictions(path, rows, ['a', 'b'])


def test_cost_arithmetic_and_invalid_inputs(tmp_path):
    source = Path(__file__).parents[1] / 'examples/costs.json'
    result = costs(source)
    assert result['current_monthly'] == 200000
    assert result['replacement_monthly'] == 100000
    assert result['monthly_savings'] == 100000
    data = json.loads(source.read_text())
    path = tmp_path / 'cost.json'
    data['fallback_fraction'] = 1
    path.write_text(json.dumps(data))
    assert costs(path)['break_even_monthly_requests'] is None
    data['hosting_monthly'] = float('nan')
    path.write_text(json.dumps(data))
    with pytest.raises(ContractError):
        costs(path)


def test_report_escapes_untrusted_labels(tmp_path):
    path = tmp_path / 'report.html'
    render_report(path, {'results': {'<script>alert(1)</script>': {'accuracy': 1, 'macro_f1': 1}}})
    assert '<script>' not in path.read_text()


def test_external_evaluation_does_not_change_selected_model(tmp_path):
    task = Path(__file__).parents[1] / 'examples/support/task.yaml'
    run = tmp_path / 'run'
    manifest = train(task, run)
    _, data, _ = load_task(task)
    predictions = tmp_path / 'external.jsonl'
    predictions.write_text('\n'.join(json.dumps({'row_index': i, 'text_sha256': digest(r['text'].encode()), 'prediction': r['label']}) for i,r in enumerate(data['test'])))
    report = evaluate(run, task, predictions=predictions)
    assert report['results']['current_system']['accuracy'] == 1
    assert report['selected_on_validation'] == manifest['selected_model']
