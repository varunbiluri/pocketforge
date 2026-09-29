# PocketForge

An early local CLI for validating labeled text data, comparing CPU classifiers, and exporting a tested model. This is the first roadmap milestone, not the complete small-model training product. The project name and package name are provisional. Code is MIT licensed; datasets retain their separately stated licenses.

## Run locally

Requires Python 3.11+ and uv. From this directory:

```bash
uv sync --extra dev --locked
uv run pocketforge validate examples/support/task.yaml
uv run pocketforge train examples/support/task.yaml --output runs/demo
uv run pocketforge evaluate runs/demo --task examples/support/task.yaml
uv run pocketforge predict runs/demo --text "Please cancel my membership"
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

The included original 24-message fixture tests the workflow only. Its scores are not evidence of real-world model quality or commercial savings. A pinned public-data preparation script and a measured [BANKING77 CPU baseline](benchmarks/BANKING77.md) are also available. Pretrained-model fine-tuning, current-system comparison imports, latency/cost reports, and independent trials remain on the [roadmap](ROADMAP.md).

## Artifacts and reproducibility

Evaluation requires the same task and byte-identical datasets used at training time. It records test predictions without exporting source text. The manifest includes label order, versions, platform, and fixed random seed. Model files are checksummed, and loading requires the recorded scikit-learn version. Use the lockfile and recorded environment when reproducing a run; cross-platform numerical identity is not guaranteed.

Only load run directories you trust. Joblib model files can execute code; checksums detect accidental corruption but do not authenticate an untrusted author. Text features in trained models may reveal parts of training data, so model exports must receive the same privacy review as other derived data. The workflow makes no network inference calls.
