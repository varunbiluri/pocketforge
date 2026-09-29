# PocketForge — roadmap to an open-source alpha

Created: September 29, 2026. Status: alpha engineering delivered; independent adoption and registry publication pending.
Public repository: varunbiluri/pocketforge. PyPI returned 404 for this name during the September 29 check; that is not a reservation. Domain and trademark clearance remain unverified.

## Product and audience

Help application developers turn a repeated text-classification task into a tested, locally deployable model. Show whether a simple baseline or a trained model meets their requirements before recommending replacement of an existing system.

Initial audience: Python developers at small software companies who have fixed-label classification tasks, representative labeled examples, and a reason to improve operating cost, latency, or deployment control. Support-ticket routing is the first example.

The six-week objective is a useful public alpha, not a general training platform or a promised level of adoption. A four-week checkpoint should produce a usable local preview. Week numbers are relative to implementation kickoff, not release promises.

## First release scope

- English, single-label text classification with a user-declared finite label set.
- Local CSV/JSONL import with documented fields, validation, and actionable errors.
- Explicit train, validation, and test partitions; checks for exact duplicate leakage and configurable grouping of related examples.
- Majority-class and TF-IDF/linear-classifier baselines; one small pretrained text-model training backend.
- A user-supplied current-system prediction file for comparison, so no paid API is required.
- Evaluation covering macro-F1, accuracy, per-class precision/recall, confusion matrix, inference latency, model size, and disclosed cost assumptions.
- Versioned artifacts containing the model, label mapping, preprocessing configuration, dependency versions, dataset fingerprints, and training recipe.
- A Python prediction interface and local CLI. A static HTML report and machine-readable report share the same underlying results.
- One complete support-routing example first; two additional licensed examples only after the core workflow works.

Defer generative agents, arbitrary JSON extraction, automated synthetic-data creation, multiple training backends, hosted infrastructure, billing, and a model marketplace. These are future options, not alpha commitments.

Core CLI (implemented):

```text
pocketforge validate task.yaml
pocketforge train task.yaml --output runs/example
pocketforge evaluate runs/<run-id> --task task.yaml
pocketforge predict runs/<run-id> --text "I need help with my invoice"
```

## Six-week delivery plan

| Week | Work | Evidence required to finish |
| --- | --- | --- |
| 1 — problem and baseline | Compare direct alternatives on the same task; choose a redistributable dataset; write the data and metric contract; scaffold the package; implement import validation and CPU baselines. Prepare an interview guide for developer feedback. | One reproducible baseline report; documented dataset rights and splits; explicit proposed advantage over existing tools; prioritized feedback where users are available. |
| 2 — complete local workflow | Implement configuration, run manifests, evaluation, model persistence, prediction, and reports for the baseline backend. | A clean environment can go from examples to saved model to predictions using the documented path; invalid data fails clearly; metrics agree with independent calculations. |
| 3 — small-model training | Add one pretrained-model backend, select checkpoints with validation data, record seeds/dependencies, and export trained artifacts. | The trained model reloads correctly; comparison against the baseline uses the same held-out cases; quality and resource results are recorded, even if the simpler model wins. |
| 4 — useful preview | Add reproducible latency measurements, a cost worksheet, installation documentation, and the first runnable example. Invite trials only through user-authorized outreach. | Another developer can run the workflow from the docs; the report identifies a useful tradeoff or clearly reports no advantage. Local preview ready. |
| 5 — external trials and reliability | Fix problems from independent trials; test label imbalance, empty input, unseen labels, oversized inputs, and artifact compatibility. Add additional examples if capacity allows. | Trial feedback and fixes recorded; supported environments pass required checks; a second task works without core-code edits. |
| 6 — release | Finalize README, walkthrough, limitations, contribution guide, code license, dataset/model notices, package build, and clean-install verification. Prepare release assets. | All release checks pass for the exact revision; release claims link to reproducible evidence; public publication is a separate launch action. |

## Week-one backlog, in execution order

1. Inspect the available Python environment and compute hardware; record a CPU-first development path. Identify an optional GPU path without provisioning paid resources.
2. Create the package skeleton, development configuration, and minimal CI plan.
3. Specify dataset fields, label rules, missing/extra-content handling, input limits, grouping, split policy, and metric definitions before implementation.
4. Audit a candidate public dataset's license, provenance, and redistribution terms. Keep public examples separate from private user data and unrelated task materials.
5. Implement validation and the majority-class baseline, then TF-IDF plus a linear classifier.
6. Add meaningful tests for leakage detection, invalid labels, metric correctness, and save/load prediction equivalence.
7. Produce the first report, with a small hand-checked fixture for metric verification and a larger legitimate dataset for performance measurement.
8. Compare the workflow against direct alternatives; write down where PocketForge is better, worse, or indistinguishable.
9. Prepare a short user interview and trial checklist. The user selects and contacts prospective testers unless outreach is explicitly delegated.

The first implementation milestone is: **a valid classification dataset becomes a reproducible baseline report and a reloadable model.** No GPU or API purchase should be necessary for this milestone.

## Evaluation contract and safeguards against misleading results

- Freeze acceptance criteria before viewing the final test results. Use validation data for model selection; do not tune against the test set.
- Keep related records and derived variants together when splitting. Report duplicate checks and the limits of those checks.
- Treat teacher predictions as predictions, not independent truth. Use authorized human labels or another justified reference.
- Report macro-F1 and per-class behavior alongside accuracy. For unsupported or undersampled classes, expose the limitation rather than hiding it in an aggregate.
- Record hardware, batch size, concurrency, warmup, sample size, and cold/warm status for latency claims. Compare candidates under the same stated conditions.
- Record repeated-run variability where applicable. Exact reproducibility is expected for deterministic artifacts; training variability must be disclosed rather than promised away.
- Cost reports include traffic assumptions, hosting utilization, training/data work, retraining, maintenance, and any fallback calls. Hypothetical inputs must be visibly labeled.
- A trained model need not beat a simple classifier for the software to work. If the simpler model satisfies the user's contract, recommend it.
- Do not describe observed test performance as a guarantee for future traffic.

## Decision gates

**End of week 1:** continue if the workflow has a concrete usefulness hypothesis and a reproducible baseline. If existing tools already provide the same experience, narrow or change the proposed advantage before building more infrastructure.

**End of week 4:** continue toward a product launch if an independent developer can use the preview and at least one representative workload shows a worthwhile benefit in workflow effort, quality, latency, cost, or deployment control. If no independent users are available, record adoption as unvalidated; technical work can continue without pretending this gate passed.

**Release:** publish performance claims only after reproducing them. If the model provides no advantage, publish the honest comparison or revise the product positioning; do not fabricate a win.

Suggested adoption targets, not forecasts: five independent trials, three completed integrations, and two users returning for a second project or retraining run. Track observed retention separately from stars, downloads, and demo views. These external outcomes may extend beyond six weeks.

## Release checklist

- [x] Dataset schema, acceptance behavior, and limitations documented.
- [x] Local tests, build, and clean-install workflow verified; exact-head CI is required before the GitHub release.
- [x] Baseline and pretrained-model runs have manifests and reports; one neural run per configuration, no training-variance claim.
- [x] Offline neural reload preserves evaluated validation predictions in the integration test.
- [x] Examples have recorded provenance and licenses; model notices included in new exports.
- [x] Private data, downloaded datasets, model weights, and scratch outputs excluded from source commits.
- [x] MIT code license and separate dataset/model terms documented.
- [x] GitHub name available and created; PyPI name checked, not reserved.
- [x] Documentation includes measured gains, regressions, and limitations.
- [x] Contribution guide, issue templates, support policy, and trial kit ready.
- [ ] Independent developer trials, integrations, and retention targets achieved — no testers yet.
- [ ] Commercial competitor usability trials completed — access/participants unavailable.
- [ ] PyPI publication — publisher credentials or trusted-publishing setup not configured.

The public alpha can be distributed through GitHub artifacts without claiming these external validation items are complete. Package registry publication and independent user outcomes must not be inferred from implementation or stars.

## Responsibilities and resource assumptions

Assistant: implementation, tests, documentation, reproducible reports, competitor comparisons, and preparation of release assets during active work sessions.

User: product decisions, access to consenting trial users and authorized data, compute budget, and launch/account ownership. No background work or outreach is scheduled by this document.

Start locally with CPU baselines. GPU availability, spending limits, weekly user availability, and access to real datasets remain unknown; resolve them before GPU-dependent training or paid services. Narrow scope or extend the schedule if those resources are unavailable.

## Competitive references

These sources were reviewed during the September 29 planning conversation. Recheck capabilities and terms during week one; they establish existing alternatives, not demand for PocketForge.

- [Arcee DistillKit](https://github.com/arcee-ai/DistillKit): distillation infrastructure.
- [Distil Labs production-trace example](https://github.com/distil-labs/distil-dlthub-models-from-traces): an existing traces-to-small-model workflow.
- [Distil Labs pricing](https://www.distillabs.ai/pricing/): training, hosted inference, and private-deployment offerings.
- [Microsoft Agent Lightning](https://github.com/microsoft/agent-lightning): agent-training infrastructure; adjacent rather than the initial classification scope.
- [Hugging Face endpoint pricing](https://huggingface.co/docs/inference-endpoints/pricing): an input to future deployment comparisons, not a savings guarantee.

## Current status

| Milestone | Evidence/status |
| --- | --- |
| 1 — baseline and problem definition | Pinned BANKING77 data and CPU report; independent plain scikit-learn comparison matches all predictions. Commercial differentiation remains a hypothesis. |
| 2 — complete local workflow | Validator, training, reload, Python/CLI prediction, manifests, and held-out reports implemented. |
| 3 — pretrained training | Pinned MiniLM frozen mode and optional encoder fine-tuning implemented; offline reload integration tested; full BANKING77 experiments recorded. |
| 4 — usable preview | Readable HTML, external prediction imports, warm timing, cost worksheet, walkthrough, and examples implemented. Independent usability unvalidated. |
| 5 — reliability and trials | Edge cases tested; two further tasks work without core changes. Trial kit prepared at user's request; no trial results collected. |
| 6 — release preparation | MIT license, third-party notices, issue templates, versioned wheel/sdist, and CI configured. GitHub v0.1.0a2 published after passing CI; PyPI remains pending owner setup. |

Measured BANKING77 accuracy: TF-IDF 87.56%, frozen MiniLM 90.19%, one-epoch adapted MiniLM 87.20% on our modified split. The adaptation regression is retained and disclosed. See benchmarks/BANKING77.md and benchmarks/results for the protocol and evidence.

No autonomous outreach or background monitoring is scheduled. Next external work: share docs/TRIAL_KIT.md with consenting developers and collect usage evidence. Next product work should follow their failures and priorities rather than add features merely to fill a calendar.

## Next delivery pipeline

- [x] Remove unrelated organization references from project documentation.
- [x] Exercise installed wheel and source distribution across all three examples in CI, including invalid input and overwrite refusal.
- [x] Add manually dispatched, version-tag-checked PyPI trusted publishing after core/neural CI and distribution validation. See docs/PUBLISHING.md.
- [x] Add a trial evidence ledger and explicit outcome definitions in docs/TRIAL_RESULTS.md.
- [ ] Owner configures PyPI trusted publisher and GitHub environment; release a new tagged version using docs/PUBLISHING.md.
- [ ] Collect five independent trials, three integrations, and two repeat uses; prioritize reliability fixes from recorded failures.
- [ ] Complete representative current-system and commercial competitor comparisons with authorized data/access.

These implementation checkmarks do not claim external validation or successful PyPI publication. No outreach has been performed.
