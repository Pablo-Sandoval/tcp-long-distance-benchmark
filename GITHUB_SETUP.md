# GitHub setup

## Option A: GitHub CLI

1. Review all files and replace placeholders in `CITATION.cff`.
2. Add the production automation script under `scripts/`.
3. From the directory containing this repository, run:

```bash
cd tcp-long-distance-benchmark
git init -b main
git add .
git commit -m "Initial research artifact scaffold"
gh repo create tcp-long-distance-benchmark --public --source=. --remote=origin --push
```

## Option B: GitHub website

Create a new empty repository named `tcp-long-distance-benchmark`. Do not pre-populate it if pushing this existing local directory. Then follow the command-line instructions shown by GitHub for an existing repository.

## First stable research release

1. Finish the security and publication checklist.
2. Update the version and release date in `CITATION.cff`.
3. Commit and push the reproducible code, documentation, data, and notebook.
4. Create a tagged release such as `v1.0.0`.
5. Enable GitHub archiving in Zenodo and publish the release to obtain a DOI.
6. Add the DOI to `CITATION.cff`, the README, and the final article.

## Important

Never commit credentials or private keys. If this project is subject to employer or university review, keep the repository private until publication approval is complete.
