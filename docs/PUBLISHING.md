# Package publishing

PyPI alpha v0.1.0a4 is published and verified from the public PyPI index. Pushing main runs CI; it does not publish a package.

## One-time owner setup

1. GitHub repository environment setup is complete: the `pypi` environment exists, requires review from `varunbiluri`, and has a custom `v*` tag deployment policy. The release workflow also rejects any ref that is not the exact `refs/tags/v{project.version}` tag.
2. PyPI trusted publishing is configured for project `pocketforge`, owner `varunbiluri`, repository `pocketforge`, workflow `release.yml`, environment `pypi`.

Use [PyPI's trusted-publisher setup](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/). No long-lived API token is needed.

## Release procedure

1. Update the version in `pyproject.toml`, refresh `uv.lock`, and update release notes. Use a new version for changed code; do not move an existing release tag.
2. Run `uv sync --locked --extra dev --extra neural`, `POCKETFORGE_NEURAL_TEST=1 uv run --extra neural pytest -q`, and `uv build`. Review the changes and push. Wait for all CI jobs on that exact commit.
3. Create and push a matching `vVERSION` tag on the tested commit. The tag must contain `release.yml`; the existing v0.1.0a2 tag predates it.
4. Dispatch **Publish to PyPI** using that tag: `gh workflow run release.yml --ref vVERSION`.
5. The workflow rejects branch/version mismatches, runs core and neural CI, builds and validates distributions, then waits for any configured environment approval. It downloads those built artifacts into a separate publishing job using PyPI OIDC.
6. Confirm the workflow and PyPI file listing succeeded. Test installation of the exact version in a fresh environment before announcing availability. Attach the matching artifacts and release notes to a GitHub release.

Authentication failures require correcting the account publisher/environment settings. Never mark publication complete from a successful build alone.
