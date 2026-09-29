# Alternatives and differentiation hypothesis

Reviewed September 29, 2026. This is a capability review, not a measured usability or performance comparison. No claim that PocketForge is first or superior is supported yet.

| Alternative | Existing capability | PocketForge's proposed focus |
| --- | --- | --- |
| scikit-learn pipelines | Text vectorization, classifiers, metrics, persistence | A single explicit dataset contract, split auditing, and portable comparison reports around those primitives. PocketForge reuses scikit-learn rather than inventing these algorithms. |
| Hugging Face SetFit | Few-shot sentence-transformer fine-tuning and classifier training | Joint comparison with simpler baselines and the user's existing predictions. SetFit already covers much of the model-training need. |
| Arcee DistillKit | Online/offline language-model distillation | A narrower fixed-label application workflow; PocketForge does not currently distill a teacher model. |
| Distil Labs | Task-specific model creation, deployment, private offerings | Local open-source workflow with explicit splits and simple baselines; ease-of-use differentiation needs independent trials. |

Sources: https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html ; https://github.com/huggingface/setfit ; https://github.com/arcee-ai/DistillKit ; https://www.distillabs.ai/faq/

## Reproducible comparison protocol

Use the prepared BANKING77 data unchanged. Fix training budget and validation selection rule before testing. Measure installation effort, number of manually supplied artifacts, training/evaluation quality, export/reload behavior, inference latency on the same hardware, and total resource cost. Keep account-gated commercial trials pending if access is unavailable. Record failed setups without treating them as model-quality failures.

Current measured comparison: PocketForge's majority, TF-IDF, and MiniLM candidates, plus an independent plain scikit-learn script (`scripts/compare_sklearn.py`) on the same BANKING77 partitions. The independent script matched every TF-IDF test prediction (87.56% accuracy, 87.42% macro-F1). This is not a completed independent product comparison. A baseline script using the same algorithms is expected to reach equivalent quality; the product hypothesis concerns reproducibility and workflow convenience, not a novel learning algorithm.
