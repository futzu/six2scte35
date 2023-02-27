#!/usr/bin/env python3

import setuptools
import six2scte35

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="six2scte35",
    version=six2scte35.version(),
    author="Adrian of Doom",
    author_email="spam@iodisco.com",
    description="ffmpeg changes SCTE-35 stream type to 0x6, six2scte35 changes it back",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/futzu/six2scte35",
    py_modules=["six2scte35"],
    scripts=["bin/six2scte35"],
    platforms="all",
    install_requires=[
        "threefive >= 2.3.69",
        "new_reader >= 0.1.3",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.6",
)
