# Alpha validation plan

Status: PyPI alpha is published. Independent trial counts remain zero until a consenting developer reports a completed workflow.

## Goal

Validate whether Python developers can use PocketForge on real fixed-label text-classification tasks and make a justified adoption decision. A trial can succeed even when the result favors a simpler baseline, an existing system, or no adoption.

## Public intake

Ask testers to install the current PyPI alpha and open a GitHub issue using the **Developer trial feedback** template. The issue template collects consent, environment, task shape, acceptance criteria, outcome, integration status, and repeat-use signal without asking for private data.

Share this install command:

```bash
python -m pip install pocketforge==0.1.0a4
```

Send testers to [TRIAL_KIT.md](TRIAL_KIT.md) for the thirty-minute workflow. Record only aggregate or synthetic reproductions in public issues.

## Counting rules

- Completed trial: a distinct consenting developer installs PocketForge and completes or clearly fails the documented validate/train/evaluate/predict workflow with enough detail to diagnose the outcome.
- Integration: the developer uses an exported model or report in their own application, evaluation harness, or deployment decision process.
- Repeat use: the same developer returns for a second task, retraining run, or deeper comparison after the initial trial.
- Current-system comparison: PocketForge and the existing system are evaluated on the same held-out cases with fixed acceptance criteria.
- Commercial comparison: a commercial or account-gated alternative is evaluated by someone with authorized access and recorded with the same task constraints.

Do not count stars, downloads, issue reactions, internal examples, BANKING77 experiments, or assistant-run smoke tests as independent trials.

## Maintainer workflow

1. Label incoming feedback as `trial`, `bug`, `docs`, `comparison`, `integration`, or `repeat-use`.
2. Check whether the report includes consent and enough aggregate detail to count.
3. If a failure is reproducible with synthetic or public data, open or link a bug issue and fix that issue before chasing new features.
4. Update [TRIAL_RESULTS.md](TRIAL_RESULTS.md) with an anonymized trial ID only after the report is complete enough to count.
5. Keep targets separate: five completed trials, three integrations, two repeat uses, and representative current-system/commercial comparisons.

## Current queue

| Item | Status | Evidence |
| --- | --- | --- |
| Public PyPI install | Complete | `pocketforge==0.1.0a4` verified from the public PyPI index with fresh pip and uv installs. |
| Public feedback intake | Complete | GitHub issue template and this plan. |
| Completed independent trials | 0 / 5 | No consenting developer reports yet. |
| Integrations | 0 / 3 | No external integration evidence yet. |
| Repeat uses | 0 / 2 | No second-use evidence yet. |
| Current-system comparisons | 0 | Requires authorized user data or public equivalent. |
| Commercial comparisons | 0 | Requires account access and comparable task setup. |

## Outreach checklist

Use only channels and contacts where outreach is welcome. Do not send private data. A useful request is short:

```text
PocketForge is a local Python alpha for fixed-label text classification. Could you try the 30-minute workflow on a non-sensitive task or the synthetic support example and open a GitHub trial-feedback issue with aggregate results? Install: python -m pip install pocketforge==0.1.0a4
```

The maintainer or a delegated assistant can post a public GitHub issue inviting trials. Direct messages, email, Slack, or forum posts require appropriate account access and permission from the account owner.
