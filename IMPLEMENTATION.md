# CI and Wheel Build Implementation Notes

This document records how the JournalKit POC build and PR pipelines work, the decisions made while implementing them, and the failures found and corrected.

## Final pipeline behavior

### Manual wheel build

`manual-build.yml` exposes a `workflow_dispatch` action. In GitHub Actions, choose a branch with **Run workflow**. It calls `reusable-build.yml`, which checks out the selected commit, builds the existing Ubuntu 22.04 Docker image, runs the Cython wheel build, and uploads the wheel and source archive as a downloadable Actions artifact.

The selected commit's short SHA is used as a valid Python local version, `0.0.0+<short-sha>`. The artifact is named `journalkit-dist-<short-sha>`.

### Pull request checks and build

`ci-test.yaml` listens for `opened`, `ready_for_review`, `synchronize`, and `reopened` pull request activity:

1. A draft PR's check jobs are skipped. A skipped workflow entry may still appear in the Actions tab; no scanners or build are run.
2. Marking the PR ready runs Bandit, Pylint, Gitleaks, and TruffleHog.
3. The reusable Docker build runs only after all test jobs pass.
4. Pushing another commit to a ready PR triggers the checks and build again. Each run has its own downloadable Actions artifact.
5. PR workflows use GitHub's speculative merge commit. A PR with merge conflicts does not produce that ref, so GitHub does not start a `pull_request` workflow. GitHub's native PR state and branch protection handle mergeability.

The build version identifies the tested merge commit. If a later push creates a new merge commit, its artifact has a new short-SHA version.

## Configuration files

| File | Purpose |
| --- | --- |
| `.bandit` | Bandit INI settings; excludes generated/test paths and starts with B101 skipped. |
| `pyproject.toml` | Pylint Python version, generated-path exclusions, common style-message disables, and line length. |
| `requirements-ci.txt` | Pins the Bandit and Pylint versions installed by CI. |
| `.gitleaks.toml` | Extends Gitleaks' default rules and excludes generated build output only. |
| `.trufflehog-exclude-paths.txt` | Newline-separated regex path exclusions for TruffleHog. |
| `.github/workflows/ci-test.yaml` | PR check and build orchestration. |
| `.github/workflows/reusable-build.yml` | Reusable Docker build and Actions artifact upload. |
| `.github/workflows/manual-build.yml` | Manual trigger for the reusable wheel build. |

The ignore lists are intended as a starting point. Add exceptions or rules in these root files as the project needs them; avoid broad secret-rule exclusions unless a finding has been reviewed.

## Issues found and resolutions

| Issue | Why it happened / implementation decision | Resolution |
| --- | --- | --- |
| The reference library's build script moves a hard-coded wheel filename. | The filename embeds an old version and Python/platform tag, so it can stop matching as soon as the package version or build environment changes. | The POC build script copies the generated `.whl` and `.tar.gz` files by extension. |
| The first POC container run could not write wheel files. | The host output directory was mounted over the container's `dist/` directory, hiding the build output directory. The host mount also had local UID/SELinux permissions that did not match a root container process. | Build in the container's own `dist/`, mount the host output separately at `/artifacts`, copy the completed files there, and run as the host UID/GID. The local README uses `:Z` for SELinux-enabled hosts. |
| The initial commit-based version `0.0.<hash>` was rejected. | Python packaging versions follow PEP 440; the hash cannot be a numeric release segment. The Docker build reported `InvalidVersion`. | Use `0.0.0+<short-sha>`, which preserves the commit identifier as a local version suffix. The same identifier appears in the artifact name. |
| Bandit failed to parse `.bandit` with `--configfile`. | `.bandit` is an INI file, but Bandit's `--configfile` option parses YAML/TOML. It therefore raised a YAML document-start parse error on `[bandit]`. | Keep `.bandit` as INI and run `bandit --recursive journalkit`. Recursive mode automatically discovers the root `.bandit` file. If switching to YAML/TOML in the future, pass that file with `--configfile` instead. |
| TruffleHog could not pull `ghcr.io/trufflesecurity/trufflehog:v3.99.8`. | The action's Git tag is `v3.99.8`, but its container image tag is `3.99.8` without the `v`. The action uses its `version` input to form the image tag. | Keep `uses: trufflesecurity/trufflehog@v3.99.8` and set `version: 3.99.8`. The GHCR package registry lists the numeric `3.99.8` image tag. |
| Draft PR pushes can create an Actions run entry. | GitHub dispatches the configured `pull_request` event on PR synchronization; draft state is available to job conditions, not as a filter that prevents the workflow event itself. | Each scanner/build job checks `github.event.pull_request.draft == false`, so draft runs show skipped jobs and execute no tools. A ready event and later ready-PR pushes execute the jobs. |

## Validation record

- Built the Docker image and generated wheel plus source archive with a commit-based version (`0.0.0+<short-sha>`).
- Ran the corrected Bandit command locally with the pinned CI requirements: no issues found.
- Ran Pylint locally with the pinned CI requirements: score 10.00/10.
- Confirmed the GHCR package registry publishes the numeric TruffleHog image tag `3.99.8`. A local image pull was attempted but stopped after the layer download stalled; the corrected TruffleHog action has not yet had a complete GitHub Actions run in this repository.
- The hosted PR workflow still needs a post-fix run to validate the full GitHub event, artifact, and branch-protection integration.

## GitHub repository settings to configure

1. Ensure all three workflow files are pushed to the repository's default branch so GitHub can discover the workflows.
2. In **Settings → Branches** or **Settings → Rulesets**, target the branch that PRs merge into.
3. Enable **Require status checks to pass before merging** and require **Bandit and Pylint**, **Gitleaks**, and **TruffleHog**. These are the independent test jobs that prevent merge when a tool fails.
4. Optionally require **Build PR wheel** if a downloadable package artifact must exist before merging.
5. Optionally require the PR branch to be up to date with its target branch. Conflicts are reported by GitHub itself; no workflow can run against a merge ref that GitHub cannot create.

No repository secrets are required by the current checks. The PR workflow requests read-only repository contents; artifacts are retained by GitHub Actions for 30 days.
