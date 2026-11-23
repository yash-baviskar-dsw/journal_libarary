#!/bin/bash
set -euo pipefail

# Build in the package's normal dist directory, then copy to the host mount.
python3 setup.py sdist bdist_wheel --universal

# The Docker run mounts this directory from the host for artifact collection.
mkdir -p /artifacts
cp dist/*.tar.gz dist/*.whl /artifacts/
