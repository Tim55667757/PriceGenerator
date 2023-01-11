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

pdoc.render.configure(
    docformat="restructuredtext",
    favicon="https://github.com/Tim55667757/PriceGenerator/blob/develop/media/logo-pricegenerator-256x256px.png?raw=true",
    footer_text="⚙ Good luck for you in trade automation! And profit!",
    logo="https://github.com/Tim55667757/PriceGenerator/blob/develop/media/logo-pricegenerator-420x610px.png?raw=true",
    show_source=False,
)
pdoc.pdoc(
    Path("pricegenerator").resolve(),
    output_directory=Path("docs").resolve(),
)
