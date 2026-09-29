# Supported environments and limitations

Core CI: Ubuntu, Python 3.11 and 3.12. Local verification: macOS ARM64, Python 3.12. Windows and GPU execution are unverified. Neural backend uses CPU with four PyTorch threads and may change process-wide PyTorch thread settings. Other scikit-learn/BLAS operations can use their own threading defaults.

Model artifacts use executable joblib serialization: only load trusted run directories. Hashes detect changes; they do not establish trust. MiniLM tokenizer inputs longer than 256 wordpieces are truncated. No calibrated confidence, abstention guarantee, or out-of-distribution detector is implemented.

No support SLA is offered for this alpha. Report reproducible bugs through GitHub Issues, with versions and synthetic data. Do not attach credentials or private datasets. For security concerns, use GitHub private vulnerability reporting if enabled; otherwise contact the repository owner privately rather than posting an exploit with sensitive details publicly.
