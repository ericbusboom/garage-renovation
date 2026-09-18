# Chapter 8 analysis and report build

This extension reuses the retained analysis definitions in `../optimization/analyze.py`, redirecting intermediate outputs into `results/`. It adds 30°, 35° and 40° battery/PV cases and two roof-geometry comparisons. It does not overwrite prior results or change the CAD model.

Run from the garage project root:

```sh
solar-study/optimization/.venv/bin/python solar-study/chapter8/analyze_chapter.py
solar-study/optimization/.venv/bin/python solar-study/chapter8/build_report.py
```

The environment requires Python, numpy, pandas, scipy, pvlib, matplotlib and reportlab. Raw solar/weather/utility inputs remain under `solar-study/optimization/data/`; no network access is needed to reproduce the calculation. The build creates the Chapter 8 PDF, Markdown, figures, data, historical copies and source archive in `report/08-solar-electrical-and-energy/`.

`results/summary.json` records a SHA-256 hash of the reused analysis program. `energy-balance-checks.csv` verifies conservation for each case. The source ZIP includes the current analysis and report builders plus retained code/data/reports and source paths/checksums in the separate inventory.

Limitations: synthesized hourly load; perfect-foresight dispatch; approximate credit banking/non-bypassable charges; unconfirmed CCA/provider and export vintage; 2005–2015 irradiance climate; owner-reported bill data; cost allowances; gross roof-envelope geometry; unverified module/access and zoning fit. These are stated in the report.
