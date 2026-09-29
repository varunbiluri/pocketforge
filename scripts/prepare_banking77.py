"""Download pinned BANKING77 and prepare an explicitly modified benchmark."""

import argparse
import csv
import io
import json
import shutil
import tempfile
import urllib.request
from collections import defaultdict
from pathlib import Path

import yaml

from pocketforge.core import digest, load_task, normalized, write_json

REVISION = "57ec275d8078af65b7731c2a98be812d844a6d6b"
BASE = f"https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{REVISION}/"


def prepare(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output exists; use a new directory.")
    raw = {name: urllib.request.urlopen(BASE + name, timeout=60).read()
           for name in ["LICENSE", "banking_data/train.csv", "banking_data/test.csv"]}
    data = {split: [{"text": r["text"], "label": r["category"]}
                    for r in csv.DictReader(io.StringIO(raw[f"banking_data/{split}.csv"].decode("utf-8")))]
            for split in ["train", "test"]}
    labels_by_text = defaultdict(set)
    for rows in data.values():
        for row in rows:
            labels_by_text[normalized(row["text"])].add(row["label"])
    ambiguous = {key for key, labels in labels_by_text.items() if len(labels) > 1}
    removed, unique = [], {}
    seen = set()
    # Preserve test membership when the same normalized text occurs in both sources.
    for split in ["test", "train"]:
        unique[split] = []
        for index, row in enumerate(data[split]):
            key = normalized(row["text"])
            if key in ambiguous or key in seen:
                removed.append({"source": split, "row_index": index, "text_sha256": digest(key.encode()),
                                "reason": "conflicting_labels" if key in ambiguous else "duplicate"})
                continue
            seen.add(key)
            unique[split].append(row)
    grouped = defaultdict(list)
    for row in unique["train"]:
        grouped[row["label"]].append(row)
    splits = {"train": [], "validation": [], "test": unique["test"]}
    for label, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: digest(normalized(row["text"]).encode()))
        n = max(1, len(rows) // 5)
        splits["validation"].extend(rows[:n])
        splits["train"].extend(rows[n:])
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".banking77-", dir=output.parent))
    try:
        for split, rows in splits.items():
            (staging / f"{split}.jsonl").write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        config = {"name": "banking77-deduplicated", "labels": sorted(grouped),
                  "splits": {split: f"{split}.jsonl" for split in splits}}
        (staging / "task.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        (staging / "LICENSE.dataset.txt").write_bytes(raw["LICENSE"])
        (staging / "ATTRIBUTION.md").write_text(
            "BANKING77 by PolyAI / Casanueva, Temcinas, Gerz, Henderson and Vulić (2020).\n"
            "Efficient Intent Detection with Dual Sentence Encoders. https://arxiv.org/abs/2003.04807\n"
            "Source: https://github.com/PolyAI-LDN/task-specific-datasets\n"
            "License: CC BY 4.0. https://creativecommons.org/licenses/by/4.0/\n"
            "Modified: normalized-text deduplication, removal of conflicting-label text, "
            "and a deterministic validation partition from training. See provenance.json.\n", encoding="utf-8")
        provenance = {"revision": REVISION, "source_url": BASE,
                      "source_sha256": {name: digest(value) for name, value in raw.items()},
                      "original_counts": {key: len(rows) for key, rows in data.items()},
                      "prepared_counts": {key: len(rows) for key, rows in splits.items()},
                      "removed": removed,
                      "split_rule": "Per label, sort retained training rows by SHA256 of normalized text; first floor(n/5), minimum 1, become validation.",
                      "deduplication_rule": "NFKC/casefold/whitespace normalization; remove all conflicting-label texts; otherwise keep first test occurrence, then first training occurrence."}
        write_json(staging / "provenance.json", provenance)
        load_task(staging / "task.yaml")
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({"counts": result["prepared_counts"], "removed": len(result["removed"])}, indent=2))
