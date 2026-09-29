# Independent developer trial

Status: no independent trials collected. No retention or customer demand claims.

## Who this is for

A Python developer with a recurring single-label English text-classification task and permission to use their dataset. Start with the synthetic support example, then a representative dataset with explicit train/validation/test splits. Do not send us customer data or model files; trained models may expose training vocabulary.

## Thirty-minute baseline trial

1. Follow the README installation and support example without assistance. Record installation problems and time to first prediction.
2. Create your own task.yaml with at least two labels. Each label must appear in training. Use a representative held-out test set and group related messages together.
3. Run validate, train, evaluate, and predict. Record the run manifest and metrics locally.
4. Define your required quality, latency, and operational constraints. Determine whether the baseline meets them before adding the neural backend.
5. Optionally import predictions from your current system and calculate costs using your own assumptions.

Neural installation, model downloads, and training may take substantially longer; no completion time is promised.

## Feedback form

- OS, Python version, PocketForge version:
- Task and approximate dataset size (no sensitive examples):
- Current approach and recurring difficulty:
- Time to first successful prediction:
- Steps that failed or required undocumented knowledge:
- Which report changed a decision, if any:
- Is the exported model usable in your application:
- What prevents adoption:
- Would you use this for a second task or retraining run:
- If comfortable, public issue link or preferred follow-up channel:

## Acceptance and follow-up

Success means the developer can complete the workflow using the docs and can make a justified decision about model suitability. A correct conclusion that the baseline or existing system is better is still a useful result. Track completed trials, integrations, and second uses separately. Suggested targets: five trials, three integrations, two repeat uses. These are targets, not observed metrics.

The maintainer can share this kit directly. The assistant has not contacted anyone or scheduled outreach. Obtain consent before publishing attributed feedback or using contributed data.
