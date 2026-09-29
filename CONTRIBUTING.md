# Contributing

PocketForge is an early alpha. Start with a reproducible issue or a small change
to the local classification workflow.

Run `uv sync --extra dev --locked`, `uv run pytest -q`, and `uv build` before
submitting changes. Add tests for changed behavior. Keep benchmark data, models,
credentials, and generated run outputs out of commits.

Document dataset provenance, evaluation splits, and hardware for performance
claims. Never tune against a final test set or present toy results as production
evidence. Contributions to code are under the MIT license; example datasets
retain their separately stated licenses.
