from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize
import numpy as np
import os

package_version = os.environ.get("JOURNALKIT_VERSION", "0.1.0")

extensions = [
    Extension(
        name="journalkit.entry",
        sources=["journalkit/entry.pyx"],
        include_dirs=[np.get_include()],
    )
]
setup(
    name="journalkit-poc",
    version=package_version,
    description="A tiny journaling library for a Docker wheel-build POC",
    packages=find_packages(),
    include_package_data=True,
    ext_modules=cythonize(extensions),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
