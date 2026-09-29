# PocketForge 0.1.0a4 — public alpha

This alpha implements a local fixed-label text-classification workflow with audited data splits, simple baselines, optional MiniLM training, current-system comparisons, HTML/JSON reports, warm inference benchmarks, and a hypothetical cost worksheet.

Three original synthetic tasks demonstrate usage. A pinned preparation script supports a documented modified BANKING77 experiment. Results are limited to those workloads; no commercial savings, independent adoption, or state-of-the-art claim is made.

Optional neural dependencies and a model download are required for MiniLM. Exported runs can reload offline. The core package is MIT licensed; datasets and base models retain their own terms. Trusted artifacts only: joblib loading executes code.

Version 0.1.0a4 is a documentation polish release after live-user dogfooding. It adds clearer Python 3.11/3.12 install guidance, a from-scratch first-task walkthrough, and a helper for current-system prediction hashes.

Install from PyPI with `python -m pip install pocketforge==0.1.0a4`, install the wheel from the matching GitHub release, or clone the repository and use the lockfile. User trials, independent competitor workflow measurement, and market validation remain pending; use docs/TRIAL_KIT.md to participate.
