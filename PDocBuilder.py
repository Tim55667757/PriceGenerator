# -*- coding: utf-8 -*-
# Author: Timur Gilmullin

"""
A coroutine that generates the API documentation for the PriceGenerator module using pdoc-engine: https://pdoc.dev/docs/pdoc.html

To build new documentation:
1. Remove the `./docs` directory from the repository root.
2. Go to the root of the repository.
3. Just run: `python PDocBuilder.py`.
"""


import os
import sys
import pdoc
from pathlib import Path


curdir = os.path.curdir

sys.path.extend([
    curdir,
    os.path.abspath(os.path.join(curdir, "pricegenerator")),
])

pdoc.pdoc(
    Path("pricegenerator").resolve(),
    output_directory=Path("docs").resolve(),
)
