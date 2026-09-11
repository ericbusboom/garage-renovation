#!/usr/bin/env python3
"""Current generator: renovated loft on the preserved full frame."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().with_name("renovated-loft-generator.py")),run_name="__main__")
