from pathlib import Path

root = Path(__file__).resolve().parent
fragment = (root / 'viewer-fragment.html').read_text().replace('GARAGE_SCENE_DATA', (root / 'scene.json').read_text())
inline = Path('/Users/eric/.codex/visualizations/2026/09/07/01a07d7a-3f27-76b1-a9a6-1bb2de899796/garage-3d.html')
if inline.parent.exists():
    inline.write_text(fragment)
style = 'body{margin:24px auto;padding:0 20px;max-width:1050px;font:14px system-ui;color:#202b32;background:#f7f7f4}button,input,select{font:inherit;padding:6px}label{margin:5px 0}#garage-status{margin-top:12px;color:#596269}'
(root / 'garage-viewer.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Garage 3D</title><style>'+style+'</style></head><body>'+fragment+'</body></html>')
