"""Warm, sequential inference measurements with explicit workload metadata."""

import platform
import statistics
import time
from pathlib import Path

from .core import ContractError, artifact_files, load_model, load_task, write_json


def benchmark(run, task, *, batch_size=1, repeats=20, warmup=3):
    if batch_size < 1 or repeats < 2 or warmup < 0:
        raise ContractError("batch_size >= 1, repeats >= 2, and warmup >= 0 are required.")
    config, data, hashes = load_task(task)
    _, manifest = load_model(run)
    if config != manifest["task"] or hashes != manifest["dataset_sha256"]:
        raise ContractError("Task or dataset changed since training; create a new run.")
    texts = [row["text"] for row in data["test"]]
    if batch_size > len(texts):
        raise ContractError("batch_size must not exceed the test dataset size.")
    # Fixed batches wrap at the boundary; identical workloads are used for every model.
    batches = [[texts[(i * batch_size + j) % len(texts)] for j in range(batch_size)]
               for i in range(repeats)]
    results = {}
    for name in manifest["validation"]:
        model, _ = load_model(run, name)
        for _ in range(warmup):
            model.predict(batches[0])
        elapsed = []
        for batch in batches:
            start = time.perf_counter_ns()
            model.predict(batch)
            elapsed.append((time.perf_counter_ns() - start) / 1_000_000)
        ordered = sorted(elapsed)
        # Nearest-rank p95; measurements represent entire batches, not individual items.
        import math
        results[name] = {
            "batch_latency_ms_median": statistics.median(elapsed),
            "batch_latency_ms_p95": ordered[math.ceil(0.95 * len(ordered)) - 1],
            "throughput_items_per_second": repeats * batch_size / (sum(elapsed) / 1000),
            "model_file_bytes": sum(p.stat().st_size for p in artifact_files(run, name) if p.is_file()),
            "batch_latency_ms_samples": elapsed,
        }
    report = {
        "measurement": "warm sequential model.predict; preprocessing included; model loading and network excluded",
        "batch_size": batch_size, "repeats": repeats, "warmup_batches": warmup,
        "concurrency": 1, "test_rows": len(texts),
        "workload": "fixed-size batches from test order, wrapping at end; warmup uses first batch",
        "platform": platform.platform(), "machine": platform.machine(),
        "python": platform.python_version(), "versions": manifest["versions"],
        "dataset_sha256": hashes, "results": results,
        "limitations": "Single-process local measurements; shared-host load affects results. No production throughput, cost, or memory claim.",
    }
    write_json(Path(run) / "benchmark.json", report)
    return report
