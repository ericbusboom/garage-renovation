# Chapter 8 data

All tables are supporting data for SOL-001 revision 1 (draft, 2026-09-15).

| File | Meaning |
|---|---|
| `angle-comparison.csv` | Annual, winter (DJF), summer (JJA), July and August kWh per kW at 30°, 35° and 40°; nameplate targets. |
| `monthly-angle-production.csv` | Monthly kWh per installed kW and for 6 kW; modeled household use. |
| `roof-geometry.csv` | Two modes: fixed 325 ft² face and fixed 30° horizontal run. Feet/inches/square feet are identified in column names. |
| `system-comparison.csv` | Thirty current dispatch/finance cases; kW DC, battery kWh, annual energy flows, USD costs and modeled savings. |
| `energy-balance-checks.csv` | Annual conservation residual for each case; tolerance 0.00001 kWh. |
| `power-bills-2026.csv` | Six owner-reported bills, including corrected March and April usage. |
| `bill-fit.csv` | Retained temperature model residuals against the six bills. |
| `prior-monthly.csv` | Historical normal-weather load/bill backfill and 7 kW example. |
| `prior-sensitivity.csv` | Prior financial/operational uncertainty sweep; older roof-fit constraint. |
| `sun-geometry.csv` | Mid-month sunrise/sunset and solar angles for approximate site coordinates. |
| `prior-azimuth.csv`, `azimuth.csv` | Retained 15° orientation comparison; compass azimuth, south = 180°. |
| `tilt-and-area.csv` | Historical broader tilt sweep based on the older 401 ft² face; not the current roof capacity. |

`annual_equipment` is the annual equivalent of discounted installation, maintenance and replacement costs. `annual_net_saving` is levelized savings minus that cost. `npv` is 25-year net present value at the assumed real discount rate. None is a contractor quote or guaranteed return.

Geometry fields labeled `cap_area` and `envelope_*_area` are gross roof-envelope calculations over the full study width. They are not net usable loft floor area. Roof thickness, side slopes, walls, openings and actual deck limits require deduction.

Hourly 6 kW dispatch runs and original raw weather, irradiance, tariff/export and analysis inputs are preserved in `../solar-analysis-source.zip` rather than duplicated here.
