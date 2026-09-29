# BANKING77 CPU baseline

Measured locally September 29, 2026. This is a modified benchmark, not an official leaderboard submission or proof of production accuracy.

## Reproduce

From the project root, use a new output directory if a run already exists:

```bash
uv sync --extra dev --locked
uv run python scripts/prepare_banking77.py --output data/banking77
uv run pocketforge train data/banking77/task.yaml --output runs/banking77
uv run pocketforge evaluate runs/banking77 --task data/banking77/task.yaml
```

The preparation script downloads the upstream license and CSV files at commit `57ec275d8078af65b7731c2a98be812d844a6d6b`. It records source hashes, removed-row indices/reasons, and split rules in `provenance.json`. Downloaded and transformed data stay in the ignored `data/` directory. Models and generated reports stay under ignored `runs/`.

## Attribution and changes

[BANKING77](https://github.com/PolyAI-LDN/task-specific-datasets) by Iñigo Casanueva, Tadas Temcinas, Daniela Gerz, Matthew Henderson, and Ivan Vulić; [Efficient Intent Detection with Dual Sentence Encoders](https://arxiv.org/abs/2003.04807), 2020. Upstream data is CC BY 4.0; the preparation output includes the license and attribution.

The original sources contain 10,003 training and 3,080 test rows over 77 intents. For PocketForge's strict input contract, normalized duplicates are removed with priority to original test membership. Conflicting-label duplicates would all be excluded; none were found in this run. Twelve duplicate records were removed. The retained original training data is divided per class by a deterministic SHA-256 ordering: the first floor(n/5) rows become validation. This leaves 8,023 training, 1,969 validation, and 3,079 test rows.

The official test partition is therefore modified, and less data is used for fitting than the original training set. Do not compare these figures directly with results using the full original training/test protocol. Normalized-text checks do not rule out semantic overlap, collection bias, or prior exposure of public data to future pretrained-model candidates.

## Results

| Candidate | Test accuracy | Test macro-F1 |
| --- | ---: | ---: |
| Majority label | 1.30% | 0.03% |
| Character TF-IDF + logistic regression | 87.56% | 87.42% |

Validation macro-F1 for TF-IDF was 87.16%. Model selection used validation only; fixed hyperparameters were used with no tuning against test results. Macro-F1 is the equally weighted mean across all 77 labels.

Environment: macOS 26.2, ARM64, Python 3.12.12, scikit-learn 1.9.1, NumPy 2.5.3. Exact run details are in the generated manifest. These measurements do not include a latency benchmark, cost comparison, confidence intervals, pretrained model, or external commercial competitor.

## Verification

- Repeated source preparation produced byte-identical files.
- A mocked-source test checks duplicate precedence, conflicting-label exclusion, deterministic splitting, and compatibility with the dataset validator.
- The project suite passes 12 tests, including hand-calculated metrics, label-name collisions, split leakage, changed datasets, and artifact integrity.
- The original small demo also produced identical manifests, model files, and reports in two local runs. Full BANKING77 training was run once; no repeated-training variability claim is made here.

Next: compare a pretrained text encoder using this frozen protocol and measure latency/resource tradeoffs. A strong existing baseline is evidence that the workflow works, not yet evidence that PocketForge is differentiated.

## Pretrained-model experiments (September 29, 2026)

The same prepared partitions and fixed hyperparameters were used, without test-set tuning. Each neural configuration was trained once. Full manifest, per-class metrics, and timing samples are recorded under `benchmarks/results/`.

| Candidate | Test accuracy | Test macro-F1 | Warm median, ms/item | Model bytes |
| --- | ---: | ---: | ---: | ---: |
| TF-IDF + logistic regression (frozen-model comparison run) | 87.56% | 87.42% | 0.262 | 29,458,452 |
| Frozen MiniLM + logistic regression | 90.19% | 90.19% | 4.223 | 91,722,923 |
| MiniLM, one encoder fine-tuning epoch + logistic regression | 87.20% | 87.18% | 4.058 | 91,722,923 |

Timing: 100 sequential batch-size-one calls, three warmup batches, first 100 test rows, CPU, macOS ARM64. Preprocessing is included; model loading, disk checksum verification, and network are excluded. Shared-host activity can affect timings. Model byte totals exclude notices added during release preparation. These timings are not representative workload capacity estimates.

The one-epoch adaptation worsened test results relative to frozen MiniLM. This is disclosed rather than retuned against the test set. More training is not automatically better. To reproduce, add `--neural` to training for frozen embeddings, or `--neural --epochs 1` for adaptation; use a fresh output directory and the matching neural dependencies. The public model may have prior exposure to similar data; these results do not prove generalization to private workloads.

An independent plain scikit-learn script reproduced every TF-IDF prediction on this split. Run `uv run python scripts/compare_sklearn.py data/banking77/task.yaml --report runs/banking77/report.json` to check. This confirms algorithm parity, not superior developer experience.
