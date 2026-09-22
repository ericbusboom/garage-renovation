# B2 location and B3 removal comparison

See beam-position-comparison.pdf for the four-page review. These are conditional gravity layouts, not construction or lifting ratings.

Run `run_sweep.py` for all nine layouts. NumPy and SciPy are required; the script currently names the local FreeCAD Python runtime. `test_layout.py` accepts BEAM_YS (JSON array of one or two north coordinates in inches) and LAYOUT (output name). Run make_plans.py with Matplotlib and report.py with ReportLab.

This study retains revision 4 option B for T1 and depends on ../structural-analysis-v4/selected-options.json. That option uses W6x16 below, W6x20 above, lighter verticals and larger end diagonals. Revision 3 supplies the original calculation/source basis. These folders are included together in the comparison source package.

Model checks: every solve checks free-DOF residuals and force/moment equilibrium; all nine layouts preserve identical nonprimary applied gravity load; B3 is absent from every section schedule. Physical north floor support is moved to T-N, not to an existing wall. No change to column locations is made.
