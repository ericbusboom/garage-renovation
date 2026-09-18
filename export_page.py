"""Export page from saved FCStd to PDF+SVG via FreeCAD GUI.
Run: /Applications/FreeCAD.app/Contents/MacOS/FreeCAD --console export_page.py
(Needs the GUI because TechDrawGui exports require Qt)
"""
import FreeCAD as App
import TechDraw, TechDrawGui
from pathlib import Path

R = Path(__file__).resolve().parent
fcstd = R / 'garage-elevations.FCStd'
assert fcstd.exists(), f"Not found: {fcstd}"

doc = App.openDocument(str(fcstd.resolve()))
page = doc.getObject('ElevationPage')
assert page, "ElevationPage not found"

for ext, method in [
    ('pdf', lambda p: TechDrawGui.exportPageAsPdf(page, p)),
    ('svg', lambda p: TechDrawGui.exportPageAsSvg(page, p)),
]:
    out = R / f'garage-elevations.{ext}'
    try:
        method(str(out.resolve()))
        print(f"✓ {out} ({out.stat().st_size:,} bytes)", flush=True)
    except Exception as e:
        print(f"✗ {ext} failed: {e}", flush=True)

App.closeDocument(doc.Name)
print("EXPORT DONE", flush=True)
App.Console.PrintLog("Export complete\n")
# Force exit — FreeCAD GUI may keep running
import sys; sys.exit(0)