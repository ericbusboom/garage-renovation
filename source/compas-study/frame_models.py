"""Canonical frame-model store.

Every COMPAS serialization of the whole structure lives in ``frame-models/``, named
``frame-<YYYYMMDD>.<NN>-<description>.compas.json``. Scripts resolve paths through
this module rather than building them, so the store stays the single source of truth.

See ``frame-models/README.md`` for the convention and what does not belong there.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / 'frame-models'
SANDBOX = DIR / 'sandbox'

PATTERN = re.compile(
    r'^frame-(?P<date>\d{8})\.(?P<seq>\d{2})-(?P<description>[a-z0-9-]+)\.compas\.json$'
)


class FrameModelError(Exception):
    """Raised when the store is missing, empty, or asked for something absent."""


def _entries():
    """Every canonical model, oldest first. Sorts chronologically as plain text."""
    if not DIR.is_dir():
        raise FrameModelError(f'frame-models directory is missing: {DIR}')
    found = []
    for path in DIR.iterdir():
        m = PATTERN.match(path.name)
        if m:
            found.append((m.group('date'), m.group('seq'), m.group('description'), path))
    return sorted(found)


def versions(description=None):
    """Version strings (``YYYYMMDD.NN``), oldest first, optionally one lineage."""
    return [f'{d}.{s}' for d, s, desc, _ in _entries()
            if description is None or desc == description]


def descriptions():
    """The lineage slugs present in the store."""
    return sorted({desc for _, _, desc, _ in _entries()})


def latest(description=None) -> Path:
    """Newest model, or newest of one lineage. Raises if the store has no match."""
    matches = [e for e in _entries() if description is None or e[2] == description]
    if not matches:
        known = ', '.join(descriptions()) or 'none'
        raise FrameModelError(
            f'no frame model for {description!r} in {DIR} (lineages present: {known})'
        )
    return matches[-1][3]


def allocate(description, date=None) -> Path:
    """Path for the next version of a lineage: today's date, next free increment.

    Never returns a path that exists, so a same-day rebuild lands on a new
    version instead of overwriting the previous one.
    """
    if not re.fullmatch(r'[a-z0-9-]+', description):
        raise FrameModelError(
            f'description must be kebab-case (a-z, 0-9, -): {description!r}'
        )
    stamp = (date or _dt.date.today()).strftime('%Y%m%d')
    used = {s for d, s, desc, _ in _entries() if d == stamp and desc == description}
    for n in range(1, 100):
        seq = f'{n:02d}'
        if seq in used:
            continue
        path = DIR / f'frame-{stamp}.{seq}-{description}.compas.json'
        if not path.exists():
            return path
    raise FrameModelError(f'all 99 increments used for {description} on {stamp}')


def parse(path) -> dict:
    """Pull ``version``, ``date``, ``seq`` and ``description`` out of a model path."""
    m = PATTERN.match(Path(path).name)
    if not m:
        raise FrameModelError(f'not a canonical frame-model name: {Path(path).name}')
    d = m.groupdict()
    d['version'] = f"{d['date']}.{d['seq']}"
    return d


if __name__ == '__main__':
    print(f'store: {DIR}')
    for date, seq, desc, path in _entries():
        print(f'  {date}.{seq}  {desc:<24} {path.name}')
    for desc in descriptions():
        print(f'latest {desc}: {latest(desc).name}')
