import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/garage-solar-mpl")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).parent
OUT = ROOT / "results"
s = json.loads((OUT / "summary.json").read_text())
monthly = pd.read_csv(OUT / "monthly.csv")
tilts = pd.read_csv(OUT / "tilt-and-area.csv")
systems = pd.read_csv(OUT / "system-comparison.csv")
sens = pd.read_csv(OUT / "sensitivity.csv")
bfit = pd.read_csv(OUT / "bill-fit.csv")

# Complete the missing angle figure independently from the slower optimization.
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].plot(tilts.tilt_deg, tilts.august_kwh_per_kw, "o-", label="August")
ax[0].plot(tilts.tilt_deg, tilts.july_kwh_per_kw, "o-", label="July")
ax[0].axvline(13, color="#299273", ls="--", label="August per-kW optimum")
ax[0].set(xlabel="Roof tilt (degrees)", ylabel="kWh per installed kW",
          title="Summer output per panel")
ax[0].legend(fontsize=8); ax[0].grid(alpha=.2)
ax[1].plot(tilts.tilt_deg, tilts.roof_sqft_at_90pct_coverage, "o-",
           label="Area needed for 1,200 kWh in August")
ax[1].plot(tilts.tilt_deg, tilts.existing_envelope_sqft, "o-",
           label="Area over current roof footprint")
ax[1].axvline(30, color="#4f6cb2", ls="--", label="Current design")
ax[1].set(xlabel="Roof tilt (degrees)", ylabel="Sloped area (sq ft)",
          title="22% active cells and 90% active coverage")
ax[1].legend(fontsize=8); ax[1].grid(alpha=.2)
fig.tight_layout()
fig.savefig(OUT / "roof-angle-and-fit.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# Add a compact comparison chart focused on the actual decision.
fig, ax = plt.subplots(figsize=(11, 6))
rows = systems[(systems.tilt == 30) & systems.solar_kw.isin([4, 5, 6, 7, 8])]
for battery, color in [(0, "#587da7"), (13.5, "#299273"), (27, "#c58549")]:
    q = rows[rows.battery_kwh == battery]
    ax.plot(q.solar_kw, q.annual_bill, "o-", lw=2, color=color,
            label=f"{battery:g} kWh battery")
ax.set(xlabel="Solar capacity (kW DC)", ylabel="Estimated annual utility bill ($)",
       title="A battery captures most of the value; the eighth solar kW adds almost none")
ax.legend(); ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig(OUT / "bill-by-system.png", dpi=170, bbox_inches="tight")
plt.close(fig)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontName="Helvetica-Bold",
                          fontSize=24, leading=28, textColor=colors.HexColor("#183247"),
                          alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold",
                          fontSize=15, leading=18, textColor=colors.HexColor("#183247"),
                          spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.5,
                          leading=13, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=7.8,
                          leading=10, textColor=colors.HexColor("#555555")))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
                          fontSize=12, leading=16, textColor=colors.HexColor("#174b3b"),
                          backColor=colors.HexColor("#e8f3ee"), borderPadding=10,
                          spaceBefore=6, spaceAfter=12))

def money(v): return f"${v:,.0f}"
def pct(v): return f"{v:.1f}%"
def para(text, style="Bodyx"): return Paragraph(text, styles[style])
def table(data, widths=None, font=7.5):
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#183247")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), font),
        ("LEADING", (0,0), (-1,-1), font+2),
        ("GRID", (0,0), (-1,-1), .25, colors.HexColor("#aeb9c0")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f6f7")]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def footer(canvas, doc):
    canvas.saveState(); canvas.setFillColor(colors.HexColor("#666666")); canvas.setFont("Helvetica", 7)
    canvas.drawString(.45*inch, .25*inch, "Garage solar planning study — preliminary model, September 2026")
    canvas.drawRightString(10.55*inch, .25*inch, f"Page {doc.page}"); canvas.restoreState()

doc = BaseDocTemplate(str(OUT / "Garage-Solar-Optimization.pdf"), pagesize=landscape(letter),
                      leftMargin=.45*inch, rightMargin=.45*inch,
                      topMargin=.4*inch, bottomMargin=.4*inch)
frame = Frame(doc.leftMargin, doc.bottomMargin+.1*inch, doc.width, doc.height-.1*inch, id="main")
doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=footer))
story = []
story += [para("Garage Solar Sizing and Cost Optimization", "Title2"),
          para("ZIP 92109 • August target: 1,200 kWh • shade-free south-facing roof", "H2x")]
story.append(para(
    "The practical answer is to keep the 30° roof. A 13–14° south-facing array is the mathematical "
    "August optimum per installed kilowatt, but it produces only 2.7% more in August and about 4.2% "
    "less over the full year than 30°. More seriously, the shallower roof loses sloped surface area "
    "over this fixed footprint. The present 30° roof needs about 8.01 kW to make 1,200 kWh in a typical "
    "August. That requires 391.9 sq ft of active 22%-efficient cells on the roughly 401.3 sq ft exposed "
    "solar slope: 97.7% active coverage. At 23% efficiency it requires 93.5% coverage. Therefore the "
    "target is possible only with a very tightly packed custom solar skin, higher-efficiency cells, a "
    "modest roof enlargement, or a steeper slope."))
story.append(para(
    "Economic result: under the central custom-roof cost assumptions, the model selects 6 kW plus one "
    "13.5 kWh battery. Its first-year utility saving is about $3,465, but after annualizing installation, "
    "maintenance and replacement costs over 25 years at a 5% real discount rate, the margin is only "
    "$58/year. A target-sized 8 kW array with one battery barely lowers the bill beyond 7 kW because "
    "the extra midday energy is exported cheaply. If the custom roofing work belongs to the building "
    "budget anyway, the same 6 kW + battery case improves to about $590/year of levelized net savings." , "Callout"))
story.append(Image(str(OUT / "monthly-energy-and-cost.png"), width=9.6*inch, height=7.37*inch))
story.append(PageBreak())

story += [para("Load estimate from the six bills", "H2x"),
          para(f"February establishes a steady load of 768/28 = {s['base_kwh_day']:.2f} kWh/day, or "
               f"{s['base_continuous_kw']:.2f} kW continuously. The fitted cooling model is "
               f"daily kWh = {s['base_kwh_day']:.2f} + {s['cooling_slope_kwh_per_day_per_F']:.2f} × "
               f"max(mean temperature − {s['balance_temperature_F']:.1f}°F, 0). Its error over the six "
               f"bills is {s['fit_rmse_kwh']:.0f} kWh/month. April is the largest mismatch; real billing "
               "dates, occupancy and non-cooling loads are unavailable."),
          Image(str(OUT / "temperature-fit.png"), width=9.8*inch, height=4.08*inch)]
fitdata = [["Bill", "Mean °F", "Actual kWh", "Model kWh", "Residual"]]
for _, r in bfit.iterrows():
    fitdata.append([r.month, f"{r.temperature_F:.1f}", f"{r.usage_kwh:,.0f}",
                    f"{r.model_kwh:,.0f}", f"{r.residual_kwh:+,.0f}"])
story += [table(fitdata, [.9*inch,.75*inch,.8*inch,.8*inch,.75*inch]), Spacer(1, 6),
          para(f"Normal-year estimate: {s['annual_normal_kwh']:,.0f} kWh/year. The warmer 2016–2025 "
               f"average gives {s['annual_recent_kwh']:,.0f} kWh/year. August 2026 was "
               f"{s['august_2026_temperature']-s['august_normal_temperature']:.1f}°F warmer than the "
               "1991–2020 ERA5 average, consistent with the exceptional 1,409 kWh bill.", "Smallx")]
story.append(PageBreak())

story += [para("Angle, area and summer production", "H2x"),
          Image(str(OUT / "roof-angle-and-fit.png"), width=9.8*inch, height=4.08*inch)]
sel = tilts[tilts.tilt_deg.isin([0,13,20,30,35,40,45])]
ad = [["Tilt", "Jul / kW", "Aug / kW", "kW for Aug target", "Roof needed at 90%", "Roof over footprint", "Aug max on footprint"]]
for _,r in sel.iterrows():
    ad.append([f"{r.tilt_deg:.0f}°", f"{r.july_kwh_per_kw:.1f}", f"{r.august_kwh_per_kw:.1f}",
               f"{r.target_kw:.2f}", f"{r.roof_sqft_at_90pct_coverage:.0f} ft²",
               f"{r.existing_envelope_sqft:.0f} ft²",
               f"{r.capacity_kw_at_22pct_90pct*r.august_kwh_per_kw:.0f} kWh"])
story += [table(ad, [.48*inch,.65*inch,.65*inch,.9*inch,1.05*inch,1.05*inch,1.05*inch], 7), Spacer(1,7),
          para("At fixed 22% cell efficiency and 90% active coverage, approximately 40° is required to "
               "approach 1,200 kWh on the present footprint. That changes the building height and roof "
               "geometry. Keeping 30° and using 23–24% cells or adding roughly 34 sq ft of solar slope "
               "is the less disruptive path. A southwest azimuth can add about 1.7% in August in this "
               "historical weather model, but it reduces annual output and cannot be achieved by a roof-integrated "
               "array unless the solar plane itself is reoriented.", "Smallx")]
story.append(PageBreak())

story += [para("Monthly energy backfill", "H2x")]
md = [["Month", "Normal mean °F", "Use", "7.80 kW @ 13°", "8.01 kW @ 30°", "7 kW @ 30°"]]
v30 = json.loads((ROOT / "data" / "pv-30.json").read_text())["outputs"]["monthly"]["fixed"]
kw30 = 1200 / v30[7]["E_m"]
for i,r in monthly.iterrows():
    md.append([r.month, f"{r.normal_temperature_F:.1f}", f"{r.modeled_use_kwh:,.0f}",
               f"{r.target_array_kwh:,.0f}", f"{v30[i]['E_m']*kw30:,.0f}",
               f"{r.seven_kw_30deg_kwh:,.0f}"])
story += [table(md, [.65*inch,.9*inch,.8*inch,1.0*inch,1.0*inch,.9*inch]), Spacer(1,8),
          para(f"The 13° summer-target system produces about {s['target_annual_kwh']:,.0f} kWh/year; "
               f"the 30° target system produces about {sum(x['E_m'] for x in v30)*kw30:,.0f} kWh/year. "
               "PVGIS includes historical cloud and irradiance variation. ERA5 1991–2020 mean cloud "
               "cover was approximately 50% in February, 31% in July, and 24% in August. On August 15, "
               "the modeled sun is above the horizon from about 6:12 a.m. to 7:34 p.m.; July 15 is "
               "about 5:51 a.m. to 7:58 p.m.", "Smallx")]
story.append(PageBreak())

story += [para("System economics", "H2x"),
          Image(str(OUT / "bill-by-system.png"), width=8.8*inch, height=4.8*inch)]
ed = [["30° system", "Installed assumption", "Utility bill", "First-year saving", "Annualized equipment", "Levelized net"]]
for k,b in [(4,0),(6,0),(5,13.5),(6,13.5),(7,13.5),(8,13.5),(7,27)]:
    r=systems[(systems.tilt==30)&(systems.solar_kw==k)&(systems.battery_kwh==b)].iloc[0]
    ed.append([f"{k:.0f} kW + {b:g} kWh", money(r.upfront), money(r.annual_bill), money(r.first_year_saving), money(r.annual_equipment), money(r.annual_net_saving)])
story += [table(ed, [1.1*inch,1.05*inch,.85*inch,1.0*inch,1.05*inch,.85*inch], 7), Spacer(1,8),
          para("Why the battery matters: new Solar Billing Plan imports and exports are valued hourly, "
               "and SDG&E's 4–9 p.m. imports are expensive. The model charges the battery only from "
               "surplus solar and uses it against the most valuable imports. It does not assume grid "
               "arbitrage. Export and delivery credit buckets are modeled separately; annual net surplus "
               "is reduced to net-surplus compensation.", "Smallx")]
story.append(PageBreak())

story += [para("Sensitivity and decision", "H2x")]
sd = [["Scenario", "Selected system", "Annualized net", "25-year NPV"]]
for _,r in sens.iterrows():
    sd.append([r.scenario, f"{r.solar_kw:g} kW + {r.battery_kwh:g} kWh",
               money(r.annual_net_saving), money(r.npv)])
story += [table(sd, [2.4*inch,1.3*inch,1.0*inch,1.0*inch], 7), Spacer(1,8),
          para("The recommendation is robust in shape, but not in profitability: 5–7 kW plus one battery "
               "is usually the useful range, while a second battery is too expensive and the eighth solar "
               "kilowatt adds little bill value. Profitability changes sign with installation cost, real "
               "discount rate, utility rates, and battery aging. Obtain quotes that separately price (1) the "
               "waterproof roof, fascia and architectural solar skin, (2) active PV hardware, and (3) battery "
               "and controls. Treating all custom-roof work as a solar cost makes the project approximately "
               "break-even; treating that finish as required building work makes solar economically attractive."),
          para("A conditional San Diego Community Power battery rebate improves the modeled 6 kW + one-battery "
               "case, but it is not included in the central result because the bill's generation provider and "
               "rate plan have not been confirmed. The current federal homeowner Residential Clean Energy "
               "Credit is unavailable for systems placed in service after December 31, 2025, so no 30% federal "
               "credit is deducted.", "Smallx")]
story.append(PageBreak())

story += [para("Model boundaries and data sources", "H2x"),
          para("This is a planning model, not a contractor proposal or utility bill guarantee. The load model "
               "has six monthly observations and no interval data. Calendar months substitute for billing "
               "periods. Air-conditioning timing is synthesized from hourly temperature. Gas, climate credits, "
               "taxes, minimum charges and unknown CCA generation rates are excluded. Results currently use "
               "bundled SDG&E EV-TOU-5 rates effective August 1, 2026 and the NBT00 records actually present in "
               "SDG&E's downloaded 'Current 2026' export file. SDG&E's readme describes NBT26, creating a source "
               "inconsistency that should be resolved against the eventual interconnection application."),
          para("Weather: Open-Meteo ERA5 reanalysis, 1991–2026, 0.25° grid. Solar: European Commission PVGIS "
               "5.2 with NSRDB 2005–2015, crystalline-silicon building mounting, 14% system loss, and no external "
               "horizon obstruction. Hourly dispatch uses PVGIS typical meteorological year shapes normalized "
               "to PVGIS monthly energy. Cost: September 2026 EnergySage San Diego average $2.56/W; central battery "
               "$14,250 for 13.5 kWh; custom solar-roof allowance $7,500; electrical allowance $2,500; year-15 "
               "inverter plus 60% battery replacement; 0.5%/year PV value degradation; 5% real discount rate; "
               "25-year horizon. Utility rates and equipment prices are held constant after inflation."),
          para("Files supplied with this report: monthly.csv, bill-fit.csv, tilt-and-area.csv, azimuth.csv, "
               "system-comparison.csv, sensitivity.csv, sun-geometry.csv, and a compressed 8,760-hour audit file. "
               "The analysis program and downloaded source files are retained alongside the results.", "Smallx")]

doc.build(story)

# Concise Markdown companion.
(OUT / "README.md").write_text(f"""# Garage solar optimization

**Recommendation:** retain the 30° roof. Use **6–7 kW plus one roughly 13.5 kWh battery** if bill savings are the main objective. A typical-August target of 1,200 kWh requires **8.01 kW at 30°**, but the extra capacity has little financial value under SDG&E's Solar Billing Plan.

The mathematical August optimum is 13–14° south-facing: 7.80 kW reaches 1,200 kWh. It loses annual output and cannot fit on the current footprint at normal panel packing. At 30°, 8.01 kW needs 97.7% active coverage with 22%-efficient cells, or 93.5% with 23%-efficient cells.

Normal-year household use is estimated at **{s['annual_normal_kwh']:,.0f} kWh/year**, based on a **{s['base_continuous_kw']:.2f} kW** steady computer/base load plus temperature-related cooling.

Under central custom-roof costs, 6 kW + one battery is approximately break-even: **{money(s['best_candidate']['first_year_saving'])} first-year utility saving**, **{money(s['best_candidate']['upfront'])} installed assumption**, and **{money(s['best_candidate']['annual_net_saving'])}/year** levelized net saving over 25 years. Removing the $7,500 custom-roof allowance from the solar investment raises modeled net savings to about **$590/year**.

Open `Garage-Solar-Optimization.pdf` for the full charts, monthly backfill, assumptions and sensitivity analysis.
""")
print(OUT / "Garage-Solar-Optimization.pdf")
