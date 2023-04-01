# -*- coding: utf-8 -*-
"""Can be used to approximately benchmark language speed as a whole.
Run from root directory using e.g. python -m cProfile -o o tools/benchmarking/run_all_examples.py
"""

import glob
import os

from interpreter import interpret

original_dir = os.getcwd()
for filepath in glob.glob("examples/**/*.nat", recursive=True):
    # skipping constants because they cannot be run more than once
    # skipping lib import file due to time delay
    if filepath.endswith("constants.nat") or filepath.endswith("lib_imports.nat"):
        continue
    print(f"Running {filepath}...")

    os.chdir(os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    tokens = interpret.construct_tokens(filename)
    interpret.interpret(tokens, iterations=100)
    os.chdir(original_dir)
