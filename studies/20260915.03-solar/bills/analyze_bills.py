"""Analyze reported bills without correcting uncertain readings or filling missing months."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
with (P/'power-bills-2026.csv').open() as f: rows=list(csv.DictReader(f))
for r in rows:r['usage_kwh']=float(r['usage_kwh']);r['reported_bill_usd']=float(r['reported_bill_usd'])
def totals(rs):
 kwh=sum(r['usage_kwh'] for r in rs);usd=sum(r['reported_bill_usd'] for r in rs)
 return {'months':len(rs),'usage_kwh':kwh,'reported_bill_usd':usd,'blended_bill_usd_per_kwh':usd/kwh if kwh else None}
result={'all_readings_as_reported':totals(rows),'excluding_readings_pending_confirmation':totals([r for r in rows if r['status']!='needs_confirmation']),'monthly':[dict(month=r['month'],usage_kwh=r['usage_kwh'],reported_bill_usd=r['reported_bill_usd'],blended_bill_usd_per_kwh=r['reported_bill_usd']/r['usage_kwh'],status=r['status']) for r in rows],'limitations':['March and April usage corrected and confirmed by owner.','Missing months are missing, not zero. No annual consumption or cost projection made.','Billing period dates and durations are unknown. Month labels are those reported by owner.','Blended bill/usage is not a utility tariff or the marginal price avoided by solar. Fixed charges, taxes, gas, prior balances or credits have not been separately identified.']}
(P/'analysis-2026.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Reported 2026 power bills','', '| Month | kWh as reported | Bill | Bill / kWh | Status |','|---|---:|---:|---:|---|']
for r in result['monthly']:lines.append(f"| {r['month']} | {r['usage_kwh']:,.0f} | ${r['reported_bill_usd']:,.2f} | ${r['blended_bill_usd_per_kwh']:.3f} | {r['status']} |")
lines+=['','All six bills total $'+f"{result['all_readings_as_reported']['reported_bill_usd']:,.0f}.",'','All readings with no pending confirmations: '+f"{result['excluding_readings_pending_confirmation']['usage_kwh']:,.0f} kWh; ${result['excluding_readings_pending_confirmation']['reported_bill_usd']:,.0f}; ${result['excluding_readings_pending_confirmation']['blended_bill_usd_per_kwh']:.3f}/kWh blended.",'']+result['limitations']
(P/'README.md').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
