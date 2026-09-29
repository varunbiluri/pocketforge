"""Standalone readable reports, external predictions, and explicit cost scenarios."""
import html
import json
import math
from pathlib import Path


def render_report(path, report):
    rows = ''.join('<tr><td>' + html.escape(name) + '</td><td>' + f'{value["accuracy"]:.2%}' + '</td><td>' + f'{value["macro_f1"]:.2%}' + '</td></tr>' for name, value in report['results'].items())
    detail = html.escape(json.dumps(report, indent=2, ensure_ascii=False))
    Path(path).write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PocketForge evaluation</title>
<style>body{max-width:960px;margin:40px auto;padding:20px;font:16px system-ui;color:#172536;background:#f7f9fc}table{width:100%;border-collapse:collapse;background:white}td,th{padding:16px;text-align:left;border-bottom:1px solid #ddd}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:24px}h1{font-size:36px}</style>
<h1>PocketForge evaluation</h1><p>Held-out test results. Selection uses validation only; this is not a guarantee of future performance.</p><table><thead><tr><th>Candidate</th><th>Accuracy</th><th>Macro-F1</th></tr></thead><tbody>''' + rows + '</tbody></table><details><summary>Full metrics and predictions</summary><pre>' + detail + '</pre></details></html>', encoding='utf-8')


def external_predictions(path, rows, labels):
    from .core import ContractError, digest
    values = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(values) != len(rows):
        raise ContractError('External predictions must cover each test row exactly once.')
    indexed = {}
    for value in values:
        if not isinstance(value, dict) or set(value) != {'row_index', 'text_sha256', 'prediction'}:
            raise ContractError('Prediction records require row_index, text_sha256, and prediction only.')
        index = value['row_index']
        if type(index) is not int or not 0 <= index < len(rows) or index in indexed:
            raise ContractError('Invalid or duplicate prediction row_index.')
        if value['text_sha256'] != digest(rows[index]['text'].encode('utf-8')):
            raise ContractError('Prediction text_sha256 does not match the test row.')
        if value['prediction'] not in labels:
            raise ContractError('External prediction uses an undeclared label.')
        indexed[index] = value['prediction']
    return [indexed[i] for i in range(len(rows))]


def costs(path):
    from .core import ContractError
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    required = {'currency', 'monthly_requests', 'current_cost_per_1000', 'hosting_monthly',
                'maintenance_monthly', 'training_one_time', 'amortization_months',
                'retraining_monthly', 'fallback_fraction', 'fallback_cost_per_1000'}
    if not isinstance(data, dict) or set(data) != required:
        raise ContractError('Cost scenario must contain exactly the fields in examples/costs.json.')
    if not isinstance(data['currency'], str) or not data['currency'].strip():
        raise ContractError('currency must be a nonempty string; all costs use that currency.')
    for key in required - {'currency'}:
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ContractError(f'{key} must be a finite nonnegative number.')
    if data['amortization_months'] <= 0 or data['fallback_fraction'] > 1:
        raise ContractError('amortization_months must be positive; fallback_fraction must be <= 1.')
    fixed = data['hosting_monthly'] + data['maintenance_monthly'] + data['retraining_monthly'] + data['training_one_time'] / data['amortization_months']
    current = data['monthly_requests'] * data['current_cost_per_1000'] / 1000
    fallback = data['monthly_requests'] * data['fallback_fraction'] * data['fallback_cost_per_1000'] / 1000
    saving_per_request = (data['current_cost_per_1000'] - data['fallback_fraction'] * data['fallback_cost_per_1000']) / 1000
    return {'kind': 'hypothetical user-supplied scenario, not a measured savings claim', 'assumptions': data,
            'current_monthly': current, 'replacement_monthly': fixed + fallback,
            'monthly_savings': current - fixed - fallback,
            'break_even_monthly_requests': fixed / saving_per_request if saving_per_request > 0 else None,
            'limitations': 'Assumes hosting supports the stated volume and fallback fraction is achieved at acceptable quality. Include labeling and engineering in training/maintenance inputs. No automatic capacity or quality guarantee.'}
