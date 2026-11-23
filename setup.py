from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        name="journalkit.entry",
        sources=["journalkit/entry.pyx"],
        include_dirs=[np.get_include()],
    )
]
## Example
setup(
    name="journalkit-poc",
    version="0.1.0",
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
