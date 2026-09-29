# From examples to a local model

Clone the repository and run `uv sync --locked --extra dev`. Run the README's support example first. Inspect `manifest.json` to see which model validation selected; inspect `report.html` to compare test quality. Keep final test results out of future model selection.

## Your own task

Create a task YAML and three CSV/JSONL files following the README contract. Include every label in training and enough independent examples to evaluate important classes. Assign related examples the same nonempty `group` and keep groups in one split. The validator rejects exact normalized duplicates, but it cannot discover every semantic relationship.

## Pretrained model

```bash
uv sync --locked --extra dev --extra neural
uv run --extra neural pocketforge train examples/support/task.yaml --output runs/neural --neural
uv run --extra neural pocketforge evaluate runs/neural --task examples/support/task.yaml
uv run --extra neural pocketforge benchmark runs/neural --task examples/support/task.yaml --repeats 100
```

The first run downloads a pinned Apache-2.0 MiniLM checkpoint from Hugging Face. The frozen mode trains only a logistic classifier over normalized embeddings. Add `--epochs 1` to fine-tune the encoder first. Fine-tuning uses cross-entropy with an auxiliary linear head, AdamW at 2e-5, batch size 32, gradient clipping 1.0, and seed 0 on CPU. The highest validation macro-F1 checkpoint of that auxiliary head selects the encoder; a fresh logistic classifier is then fitted to its normalized training embeddings. Candidate selection compares the final classifiers on validation data. The manifest records the checkpoint, epochs, training history and dependencies.

The frozen mode is not encoder fine-tuning or teacher distillation. Fine-tuning is not guaranteed to improve quality. Text is truncated to 256 wordpieces for MiniLM. Export includes tokenizer, encoder, and trained classifier; reloading requires no model download. Use `uv run --extra neural` for neural inference as well. Exported neural files retain the base model's Apache-2.0 terms, distinct from the MIT package code.

## Compare your existing system

Supply UTF-8 JSONL with exactly one record for each zero-based test row. Records may be out of order, but no row may be missing or repeated:

```json
{"row_index": 0, "text_sha256": "SHA256_OF_EXACT_UTF8_TEXT", "prediction": "billing"}
```

The checksum is over original text bytes, not normalized text. Prediction must be a declared label. Run:

```bash
uv run pocketforge evaluate runs/demo --task examples/support/task.yaml --predictions current-system.jsonl
```

A current-system score is displayed alongside candidates, but cannot change the selected model. Test labels must not be used to generate real comparison predictions. Tests of this importer use deliberately fabricated predictions solely to verify accounting.

## Cost scenario

```bash
uv run pocketforge cost examples/costs.json
```

Edit all assumptions to match your workload. The example is hypothetical INR arithmetic. Monthly replacement cost equals hosting + maintenance + retraining + amortized training + fallback traffic. Break-even uses the same fixed hosting assumption; capacity is not automatically inferred from the local timing test. Quality, fallback rate, and sufficient serving capacity must be verified separately.

## Deployment

Copy the complete trusted run directory to an environment matching its manifest. Load once with `model, manifest = pocketforge.core.load_model(run)` and reuse `model.predict([...])` for batch application calls. The CLI `predict` loads per invocation; benchmark measures already-loaded inference. No hosted service is required. Joblib files execute code when loading: never load an untrusted run.
