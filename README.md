# PocketForge

[![CI](https://github.com/varunbiluri/pocketforge/actions/workflows/ci.yml/badge.svg)](https://github.com/varunbiluri/pocketforge/actions/workflows/ci.yml)

A local toolkit for validating labeled text data, comparing simple classifiers with optional pretrained MiniLM models, and exporting a tested model. Public alpha: fixed-label English text classification, with no claim of production readiness. Code is MIT licensed; datasets retain their separately stated licenses.

## Run locally

Requires Python 3.11 or 3.12 and uv. Python 3.13+ is not part of the supported alpha test matrix yet. If your system `python3` points at a newer interpreter or creates a venv without pip, use uv to choose a supported interpreter:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pocketforge==0.1.0a4
.venv/bin/python -m pocketforge.cli --help
```

From this repository checkout:

```bash
uv sync --extra dev --locked
uv run pocketforge validate examples/support/task.yaml
uv run pocketforge train examples/support/task.yaml --output runs/demo
uv run pocketforge evaluate runs/demo --task examples/support/task.yaml
uv run pocketforge predict runs/demo --text "Please cancel my membership"
uv run pocketforge benchmark runs/demo --task examples/support/task.yaml --repeats 100
uv run pytest
```

Training refuses to overwrite an existing run. Choose another output directory for the next experiment. Open `runs/demo/report.html` after evaluation for the report, or read `report.json`. Training writes a manifest and both candidate models. Selection uses validation macro-F1 with ties going to the majority baseline. Test results never select the model.

Python use after installation:

```python
from pocketforge.core import predict
label = predict("runs/demo", "There is an unexpected charge on my invoice")
```

## Data contract

The YAML task contains exactly `name` (nonblank string), `labels` (at least two unique trimmed strings), and `splits` with `train`, `validation`, and `test` file paths relative to the YAML file. Example: [task.yaml](examples/support/task.yaml).

Data is UTF-8 CSV or JSONL. Each record contains exactly `text`, `label`, and optionally `group`. Text must be nonblank and at most 10,000 Unicode characters. Labels match the declared strings exactly; every label must appear in training. Group is an optional string; an empty string means ungrouped. Extra fields, missing required values, invalid labels, and empty splits are errors. Blank JSONL lines are ignored. CSV header names must be unique.

Duplicate text is rejected within and across splits after Unicode NFKC normalization, case folding, and whitespace collapsing. Nonempty group identifiers may repeat within a split but must not span splits. These checks do not detect semantic paraphrases or undisclosed relationships: dataset authors must assign groups appropriately. Training uses original text, not the duplicate-detection normalization.

Validation and test may omit a class; reports explicitly list absent reference labels. Macro-F1 includes every declared label with undefined precision/recall set to zero. Confusion-matrix rows are true labels, columns predicted labels, in the declared order. No model-quality acceptance threshold is imposed by the package.

## What is implemented

- Majority and character TF-IDF + logistic-regression baselines with fixed parameters.
- Explicit partitions, group/duplicate checks, dataset SHA-256 fingerprints, and dependency manifests.
- Validation-based selection; held-out accuracy, macro-F1, per-class metrics, confusion matrices, and predictions.
- Model persistence, a Python prediction function, and JSON/HTML reports.
- Local inference benchmarks: median/p95 batch latency, throughput, model size, and raw timing samples in `benchmark.json`. Timing includes preprocessing but excludes model loading and network transport. Batch size, warmup, repetitions, and environment are recorded; these are local measurements rather than production capacity estimates.

The included original 24-message fixture tests the workflow only. Its scores are not evidence of real-world model quality or commercial savings. A pinned public-data preparation script and a measured [BANKING77 CPU baseline](benchmarks/BANKING77.md) are also available. Optional MiniLM training, current-system prediction imports, inference benchmarks, and cost scenarios are implemented. Independent trials and broader product comparisons remain on the [roadmap](ROADMAP.md).

## Artifacts and reproducibility

Evaluation requires the same task and byte-identical datasets used at training time. It records test predictions without exporting source text. The manifest includes label order, versions, platform, and fixed random seed. Model files are checksummed, and loading requires the recorded scikit-learn version. Use the lockfile and recorded environment when reproducing a run; cross-platform numerical identity is not guaranteed.

Only load run directories you trust. Joblib model files can execute code; checksums detect accidental corruption but do not authenticate an untrusted author. Text features in trained models may reveal parts of training data, so model exports must receive the same privacy review as other derived data. The workflow makes no network inference calls.

## Optional pretrained models

```bash
uv sync --locked --extra dev --extra neural
uv run --extra neural pocketforge train examples/support/task.yaml --output runs/neural --neural
# Optional encoder fine-tuning (CPU; can take longer):
uv run --extra neural pocketforge train examples/support/task.yaml --output runs/finetuned --neural --epochs 1
uv run --extra neural pocketforge evaluate runs/finetuned --task examples/support/task.yaml
```

Frozen mode trains a classifier over embeddings. Fine-tuned mode updates the encoder before fitting its classifier. Both compare against simpler baselines on validation data. A pinned public model downloads on first use; exported models reload offline. MiniLM truncates at 256 wordpieces. Read the [walkthrough](docs/WALKTHROUGH.md) for checkpoint selection, deployment, external prediction schema, and cost assumptions.

## Try your own workflow

- [Developer trial kit](docs/TRIAL_KIT.md): quick start and feedback questions.
- [Alpha validation plan](docs/VALIDATION_PLAN.md): public intake, counting rules, and current validation queue.
- [Supported environments](docs/SUPPORT.md) and [third-party notices](docs/THIRD_PARTY.md).
- [Alternative tools](docs/COMPETITORS.md): existing capabilities and unvalidated differentiation.
- Additional original fixtures: `examples/documents/task.yaml` and `examples/intents/task.yaml`.
- `pocketforge cost examples/costs.json` calculates a hypothetical scenario, not promised savings.
- `pocketforge evaluate RUN --task TASK --predictions predictions.jsonl` compares your current system without changing model selection.

Install from PyPI or this repository:

```bash
python -m pip install pocketforge==0.1.0a4
```

Domain and trademark clearance remain unverified.

Maintainers: [publishing procedure](docs/PUBLISHING.md) and [independent trial evidence](docs/TRIAL_RESULTS.md).
