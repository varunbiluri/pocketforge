"""Exercise the installed distribution from outside the source tree."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='pocketforge-smoke-') as directory:
        def invoke(*args, expected=0):
            result = subprocess.run(
                [sys.executable, '-I', '-m', 'pocketforge.cli', *map(str, args)],
                cwd=directory, capture_output=True, text=True,
            )
            if result.returncode != expected:
                raise RuntimeError(f'{args}: exit {result.returncode}\n{result.stderr}')
            return json.loads(result.stdout) if expected == 0 else result.stderr

        for example in ('support', 'documents', 'intents'):
            task = ROOT / 'examples' / example / 'task.yaml'
            run = Path(directory) / example
            counts = invoke('validate', task)['counts']
            manifest = invoke('train', task, '--output', run)
            report = invoke('evaluate', run, '--task', task)
            assert report['selected_on_validation'] == manifest['selected_model']
            assert len(report['results']['majority']['predictions']) == counts['test']
            assert (run / 'report.html').is_file()
            prediction = invoke('predict', run, '--text', 'Please help with my request')
            assert prediction['label'] in manifest['task']['labels']
            timing = invoke('benchmark', run, '--task', task, '--repeats', 3)
            assert set(timing['results']) == set(manifest['validation'])
            assert 'text must have' in invoke('predict', run, '--text', ' ', expected=2)
            assert 'already exists' in invoke('train', task, '--output', run, expected=2)
            print(f'{example}: installed CLI workflow passed')
        assert invoke('cost', ROOT / 'examples/costs.json')['current_monthly'] == 200000


if __name__ == '__main__':
    main()
