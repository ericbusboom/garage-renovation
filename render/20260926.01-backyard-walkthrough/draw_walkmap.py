"""Draw walkmap.json as walkmap.png: walkable light, blocked dark, footprint outlined."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parent
m = json.loads((R / 'walkmap.json').read_text())
S = 4
img = Image.new('RGB', (m['nx'] * S, m['ny'] * S), '#2b2f33')
d = ImageDraw.Draw(img)
for j, row in enumerate(m['rows']):
    for i, c in enumerate(row):
        if c == '.':
            y = (m['ny'] - 1 - j) * S              # north up
            d.rectangle([i * S, y, i * S + S - 1, y + S - 1], fill='#e9e4d6')
fx0, fx1, fy0, fy1 = m['footprint']
px = lambda x: (x - m['x0']) / m['cell'] * S
py = lambda y: (m['ny'] - (y - m['y0']) / m['cell']) * S
d.rectangle([px(fx0), py(fy1), px(fx1), py(fy0)], outline='#d05a2a', width=2)
img.save(R / 'walkmap.png')
