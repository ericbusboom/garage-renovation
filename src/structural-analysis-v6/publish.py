#!/usr/bin/env python
"""Publish the reviewed analysis package into the report.

Follows the rules in ``report/AGENTS.md``: the working analysis stays here, the
controlled package goes into ``report/06-structural-engineering/fea-study/`` as
STR-007, and the manifest, master index and section README are updated in the
same change.  Every published file is checksummed into ``source-inventory.csv``
alongside the code that produced it.

    python publish.py [--revision 0] [--status draft]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import time
from pathlib import Path
from project_paths import PROJECT_ROOT as ROOT, VIZ_DIR as RESULTS, REPORT_DIR as REPORT, FRAME_DIR

HERE = Path(__file__).resolve().parent
DEST = REPORT / '06-structural-engineering' / 'fea-study'
DOC_ID = 'STR-007'
TITLE = 'Frame finite element analysis and member optimisation study'

COPY = ['results.json', 'member-schedule.csv', 'load-cases.csv', 'reactions.csv',
        'fea-model-3d.html']
FIGURES = ['utilisation-as-drawn.png', 'utilisation.png', 'utilisation-adequate.png',
           'opportunity-map.png', 'weight-by-group.png', 'utilisation-histogram.png']
CODE = ['sections.py', 'loads.py', 'frame.py', 'surfaces.py', 'loadcases.py',
        'codecheck.py', 'analysis.py', 'completion.py', 'studies.py',
        'visualize.py', 'viewer.py', 'narrative.py', 'run_all.py', 'publish.py']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--revision', default='0')
    ap.add_argument('--status', default='draft',
                    choices=['planned', 'draft', 'reviewed', 'verified', 'issued',
                             'superseded'])
    args = ap.parse_args()

    data = json.loads((RESULTS / 'results.json').read_text())
    date = time.strftime('%Y-%m-%d')
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / 'figures').mkdir(exist_ok=True)

    for name in COPY:
        shutil.copy2(RESULTS / name, DEST / name)
    for name in FIGURES:
        shutil.copy2(RESULTS / 'figures' / name, DEST / 'figures' / name)

    import narrative
    (DEST / 'README.md').write_text(
        narrative.readme(data, args.revision, args.status, date))
    (DEST / 'structural-analysis.md').write_text(
        narrative.report(data, args.revision, args.status, date))
    (DEST / 'design-load-basis.md').write_text(narrative.load_basis(data, date))
    (DEST / 'findings.csv').write_text(narrative.findings_csv(data))

    _source_inventory(data, date)
    _manifest(args, date)
    _index(data, args, date)
    _section_readme(data, args, date)
    print(f'published {DOC_ID} revision {args.revision} ({args.status}) to {DEST}')
    for f in sorted(DEST.rglob('*')):
        if f.is_file():
            print(f'  {f.relative_to(DEST)}  ({f.stat().st_size / 1024:.0f} kB)')


def _source_inventory(data: dict, date: str) -> None:
    rows = []
    frame_model = FRAME_DIR / data['frame_model']
    rows.append(dict(kind='input', path=f'../../../data/frame-models/{data["frame_model"]}',
                     sha256=sha256(frame_model), note='canonical frame geometry model'))
    for name in CODE:
        p = HERE / name
        if p.exists():
            rows.append(dict(kind='code', path=f'../../../src/structural-analysis-v6/{name}',
                             sha256=sha256(p), note='generator'))
    for p in sorted(DEST.rglob('*')):
        if p.is_file() and p.name != 'source-inventory.csv':
            rows.append(dict(kind='output', path=str(p.relative_to(DEST)),
                             sha256=sha256(p), note=f'published {date}'))
    with (DEST / 'source-inventory.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['kind', 'path', 'sha256', 'note'])
        w.writeheader()
        w.writerows(rows)


def _manifest(args, date: str) -> None:
    path = REPORT / 'document-manifest.csv'
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    rows = [r for r in rows if not r['document_id'].startswith(DOC_ID)]

    src = ('../src/structural-analysis-v6/run_all.py; '
           '../src/structural-analysis-v6/publish.py')
    auth = ('Preliminary engineering analysis by the project team; no structural '
            'adequacy is certified and no connection or foundation is designed')
    base = dict(section='06', discipline='Structural',
                required_for='Owner review and structural engineering handoff',
                authoritative_source=auth, working_source=src, last_verified=date,
                status=args.status)
    rows.append({**base, 'document_id': DOC_ID, 'title': TITLE,
                 'report_path': '06-structural-engineering/fea-study/structural-analysis.md',
                 'notes': f'Revision {args.revision}; SHA256 '
                          f'{sha256(DEST / "structural-analysis.md")}'})
    n = 1
    for p in sorted(DEST.rglob('*')):
        if not p.is_file() or p.name == 'structural-analysis.md':
            continue
        rel = p.relative_to(DEST)
        rows.append({**base, 'document_id': f'{DOC_ID}-A{n:02d}',
                     'title': str(rel),
                     'report_path': f'06-structural-engineering/fea-study/{rel}',
                     'notes': f'Revision {args.revision}; SHA256 {sha256(p)}'})
        n += 1
    rows.sort(key=lambda r: (r['section'], r['document_id']))
    with path.open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows({k: r.get(k, '') for k in fields} for r in rows)


def _index(data: dict, args, date: str) -> None:
    import narrative
    path = REPORT / '00-report-index.md'
    text = path.read_text()
    block = narrative.index_block(data, args.revision, args.status, date)
    marker = '## Chapter 6 frame finite element analysis'
    if marker in text:
        start = text.index(marker)
        end = text.find('\n## ', start + 1)
        text = text[:start] + block + (text[end + 1:] if end > 0 else '')
    else:
        anchor = '## Chapter 7 wall panel research'
        text = (text.replace(anchor, block + '\n' + anchor) if anchor in text
                else text.rstrip() + '\n\n' + block)
    row_old = ('| [06 Structural engineering](06-structural-engineering/) |')
    for line in text.splitlines():
        if line.startswith(row_old):
            parts = line.split('|')
            parts[-2] = (f' {DOC_ID} rev {args.revision}: frame FEA, gravity, wind '
                         f'and seismic screening; STR-006 geometry retained ')
            text = text.replace(line, '|'.join(parts))
            break
    text = text.replace('**Last updated:** 2026-09-17', f'**Last updated:** {date}')
    path.write_text(text)


def _section_readme(data: dict, args, date: str) -> None:
    import narrative
    path = REPORT / '06-structural-engineering' / 'README.md'
    text = path.read_text()
    block = narrative.section_block(data, args.revision, args.status, date)
    marker = '## Current analysis'
    if marker in text:
        text = text[:text.index(marker)] + block
    else:
        text = text.rstrip() + '\n\n' + block
    path.write_text(text)


if __name__ == '__main__':
    main()
