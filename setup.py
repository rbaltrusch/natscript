#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Packaging script"""

from pathlib import Path

if __name__ == "__main__":
    project_dir = Path(__file__).parent

    import setuptools

    from natscript import VERSION

    setuptools.setup(
        name="natscript",
        version=VERSION,
        description="Natscript interpreter",
        long_description=project_dir.joinpath("README.md").read_text(encoding="utf-8"),
        long_description_content_type="text/markdown",
        keywords=["python"],
        author="Richard Baltrusch",
        url="https://github.com/rbaltrusch/natscript",
        packages=setuptools.find_packages("."),
        package_dir={"": "."},
        python_requires=">=3.8",
        include_package_data=True,
        package_data={
            "natscript": ["py.typed", "../natscript_lib/*.py", "../natscript_lib/*.nat"]
        },  # py.typed for mypy
        # This is a trick to avoid duplicating dependencies in both setup.py and requirements.txt.
        # requirements.txt must be included in MANIFEST.in for this to work.
        install_requires=project_dir.joinpath("requirements.txt")
        .read_text()
        .split("\n"),
        zip_safe=False,
        license="MIT",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            # 3.12 doesn't work with setup.py, see: https://stackoverflow.com/questions/73533994/sub-package-not-importable-after-installation  pylint: disable=line-too-long
            # "Programming Language :: Python :: 3.12",
            "Topic :: Software Development",
            "Topic :: Software Development :: Interpreters",
            "Typing :: Typed",
        ],
    )
