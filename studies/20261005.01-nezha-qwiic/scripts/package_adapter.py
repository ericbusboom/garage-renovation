#!/usr/bin/env python3
"""Package checked manufacturing outputs; no machine program is generated."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
assert json.loads((root / 'checks/validation.json').read_text())['status'] == 'PASS'
# Keep optional KiCad job metadata out of manufacturing ZIPs: its nominal
# bounding-box size includes the outline stroke, and it omits custom rules.
suffixes = {'.gtl', '.gbl', '.gts', '.gbs', '.gto', '.gtp', '.gm1', '.drl', '.txt'}
for source, name in [('fabrication', 'fabrication'), ('milling', 'milling-inputs')]:
    files = sorted(p for p in (root / 'exports' / source).iterdir()
                   if p.suffix in suffixes and not p.name.startswith('.')
                   and not p.name.endswith('-PTH.drl'))
    assert any(p.name.endswith('-NPTH.drl') for p in files)
    assert any(p.name.endswith('-F_Cu.gtl') for p in files)
    assert any(p.name.endswith('-Edge_Cuts.gm1') for p in files)
    target = root / 'exports' / f'nezha-qwiic-revA-{name}.zip'
    with ZipFile(target, 'w', ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.name)
    print(f'{target.name}: {len(files)} files')

manifest = root / 'exports/SHA256SUMS.txt'
files = sorted(p for folder in ['design', 'exports'] for p in (root / folder).rglob('*')
               if p.is_file() and p != manifest and p.suffix != '.kicad_prl'
               and not any(part.startswith('.') for part in p.relative_to(root).parts))
manifest.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root)}\n'
                            for p in files))
