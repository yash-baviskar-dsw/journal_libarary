# journalkit POC

A small journaling library used to simulate the `unifyai_library` Docker wheel build pipeline. The package contains a minimal entry model and keeps the focus on building a compiled wheel inside Docker.

## Wheel file generation

The Docker build uses Ubuntu 22.04, installs Python build tools and pinned Cython/NumPy dependencies, renames package `.py` files to `.pyx`, and compiles them through `setup.py`. The container builds both a source archive and a wheel, then copies them into the host-mounted output directory.

From this directory:

```sh
docker build -t journalkit-wheel -f package/Dockerfile .
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD/Docker_Generated_JournalKit_wheel:/artifacts:Z" journalkit-wheel
```

The `:Z` volume option lets Docker write to the mounted directory on SELinux-enabled Linux hosts. After the container exits, `Docker_Generated_JournalKit_wheel/` contains the `.tar.gz` source archive and `.whl` wheel.

## GitHub Actions build

The **Build JournalKit Wheel** workflow is started manually from the Actions tab. GitHub requires its `workflow_dispatch` file to be present on the repository's default branch for the workflow to be available; from there, select the desired branch in **Run workflow**. The workflow checks out the selected commit and builds through the same Dockerfile and shell script described above. The package version is `0.0.0+<7-character-commit-id>`: the commit ID is in Python's valid local-version suffix. GitHub Actions uploads both the wheel and source archive as a downloadable artifact named `journalkit-dist-<commit-id>`.

## Local usage after installing the wheel

```python
from journalkit import Journal

entry = Journal.create_entry("A quiet morning", mood="calm")
print(entry.as_dict())
```
