# Data and model notices

- Package code: MIT, see LICENSE.
- Original example JSONL data: CC0 1.0, stated in each example README.
- BANKING77: PolyAI / Casanueva, Temcinas, Gerz, Henderson, Vulić (2020), CC BY 4.0. The download/preparation process writes source revision, hashes, modifications, attribution, and the upstream license. Source: https://github.com/PolyAI-LDN/task-specific-datasets . Paper: https://arxiv.org/abs/2003.04807 . Data is not bundled in the wheel.
- all-MiniLM-L6-v2: sentence-transformers, Apache-2.0, pinned at 1110a243fdf4706b3f48f1d95db1a4f5529b4d41. Model card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 . Weights download only on explicit neural training and are not bundled in the package. Derived exports remain subject to the model license. MiniLM maps short text to embeddings; our classifier is an additional adaptation, not the upstream authors' endorsed product.
- Runtime dependencies retain their own licenses. uv.lock records exact resolved versions. The package license does not override dataset, model, or dependency terms.
