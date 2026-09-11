"""Render the current renovated loft."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().with_name("preview-renovated-loft.py")), run_name="__main__")
