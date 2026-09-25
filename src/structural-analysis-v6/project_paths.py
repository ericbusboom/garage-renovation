"""Canonical locations after the 2026-09-21 workspace reorganization."""
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SOURCE_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
FRAME_DIR = DATA_DIR / 'frame-models'
MODEL_DIR = DATA_DIR / 'model'
REPORT_DIR = PROJECT_ROOT / 'report'
STUDIES_DIR = PROJECT_ROOT / 'studies'
VIZ_ROOT = PROJECT_ROOT / 'viz'
# ``latest`` is an intentional, repository-tracked symlink. Repointing it rolls
# the working visualization forward or back without renaming a release.
VIZ_DIR = VIZ_ROOT / 'latest'
ANALYSIS_STUDY_DIR = STUDIES_DIR / '20260924.01-lean-to-frame-development'
