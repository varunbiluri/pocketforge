from pathlib import Path

import pytest

from pocketforge.benchmark import benchmark
from pocketforge.core import ContractError, train


def test_benchmark_metadata_and_arithmetic(tmp_path):
    task = Path(__file__).parents[1] / "examples/support/task.yaml"
    run = tmp_path / "run"
    train(task, run)
    result = benchmark(run, task, batch_size=2, repeats=3, warmup=1)
    assert result["concurrency"] == 1
    assert result["batch_size"] == 2
    for candidate in result["results"].values():
        samples = candidate["batch_latency_ms_samples"]
        assert len(samples) == 3
        assert candidate["batch_latency_ms_p95"] == max(samples)
        assert candidate["throughput_items_per_second"] == pytest.approx(6000 / sum(samples))
        assert candidate["model_file_bytes"] > 0
    assert (run / "benchmark.json").is_file()
    with pytest.raises(ContractError, match="dataset size"):
        benchmark(run, task, batch_size=7)


@pytest.mark.parametrize("kwargs", [{"batch_size": 0}, {"repeats": 1}, {"warmup": -1}])
def test_invalid_measurement_parameters(kwargs):
    with pytest.raises(ContractError):
        benchmark("unused", "unused", **kwargs)
