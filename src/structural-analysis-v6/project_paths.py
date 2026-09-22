"""Canonical locations after the 2026-09-21 workspace reorganization."""
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SOURCE_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
FRAME_DIR = DATA_DIR / 'frame-models'
MODEL_DIR = DATA_DIR / 'model'
VIZ_DIR = PROJECT_ROOT / 'viz' / 'structural-analysis'
REPORT_DIR = PROJECT_ROOT / 'report'
STUDIES_DIR = PROJECT_ROOT / 'studies'

