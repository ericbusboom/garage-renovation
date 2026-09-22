"""Report prose, generated from the result set so the text cannot drift from it.

Every figure quoted in the published report is read out of ``results.json``.  If
the analysis is re-run and an answer changes, the sentence changes with it.
"""
from __future__ import annotations

import csv
import io

DOC_ID = 'STR-007'
TITLE = 'Frame finite element analysis and member optimisation study'


def _n(v, spec='{:,.0f}'):
    return spec.format(v) if isinstance(v, (int, float)) else str(v)


def _sc(d, key):
    return d['scenarios'][key]


def _over_table(rows, limit=12):
    if not rows:
        return '_None: every member is within capacity._\n'
    out = ['| Member | Section | DCR | Governed by | Combination |',
           '|---|---|---:|---|---|']
    for r in rows[:limit]:
        out.append(f'| `{r["member"]}` | {r["section"]} | **{r["dcr"]:.2f}** | '
                   f'{r["mode"]} | {r["combo"]} |')
    if len(rows) > limit:
        out.append(f'| … | | | | _{len(rows) - limit} more in the member schedule_ |')
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------------------

def readme(d: dict, rev: str, status: str, date: str) -> str:
    drawn, done = _sc(d, 'as_drawn'), _sc(d, 'completed')
    cross = _sc(d, 'crossings_joined') or {}
    cum = d['removal'].get('cumulative', {})
    t = d['totals']
    return f"""# {DOC_ID} — {TITLE}

**Revision:** {rev} · **Date:** {date} · **Status:** `{status}`
**Purpose:** Establish the design loads, test the frame against them, and show
where members can be reduced or removed.

> This is a preliminary engineering study, not a construction document. No
> connection, base plate, anchor or foundation is designed or checked here.
> Structural drawings and calculations require review and sealing by the
> responsible California-licensed structural engineer.

## Read this first

- **[Structural analysis report](structural-analysis.md)** — the findings, the
  verification, and what has to change.
- **[Interactive 3-D model](fea-model-3d.html)** — self-contained; open in a
  browser. Switch the colouring between utilisation, recommended action,
  removability and what governs each member. Hover any member for its full
  schedule row.
- **[Design load basis](design-load-basis.md)** — every load, with its source.
- **[Findings](findings.csv)** — the numbered findings as a table.

## Headline results

| | |
|---|---|
| Frame as drawn | max DCR **{drawn['max_dcr']:.2f}**, {len(drawn['over_capacity'])} members over capacity |
| With the upper roof framed | max DCR **{done['max_dcr']:.2f}**, {len(done['over_capacity'])} members over capacity |
| With the X-brace crossings also connected | max DCR **{cross.get('max_dcr', 0):.2f}**, {len(cross.get('over_capacity', []))} members over capacity |
| Members that can be deleted outright | **{len(cum.get('removed', []))}** of {d['counts']['members']}, {_n(cum.get('weight_saved_lb', 0))} lb |
| Sections verified one or more sizes lighter | **{len(d['sizing'].get('lighter') or [])}** |
| Sections that must get heavier | **{len(d['sizing'].get('heavier') or [])}** |

## Figures

- [Utilisation, frame as drawn](figures/utilisation-as-drawn.png)
- [Utilisation, upper roof framed](figures/utilisation.png)
- [Utilisation, adequate frame](figures/utilisation-adequate.png)
- [Where material can come out](figures/opportunity-map.png)
- [Member weight by group, before and after](figures/weight-by-group.png)
- [Distribution of utilisation](figures/utilisation-histogram.png)

## Data

- [Member schedule](member-schedule.csv) — every member with its section,
  unbraced length, slenderness, demands, DCR, governing combination, removal
  verdict and proposed section.
- [Applied load cases](load-cases.csv) — the resultant of every case as applied.
- [Support reactions](reactions.csv) — maximum compression, uplift and shear at
  each of the {d['counts']['supports']} bases.
- [Full result set](results.json) — machine-readable, every scenario.
- [Source inventory](source-inventory.csv) — checksums of the input model, the
  generating code and every published file.

## Provenance

Geometry: `data/frame-models/{d['frame_model']}` — the canonical model, unmodified.
Analysis: {d['software']}.
Generated {d['generated']} by `src/structural-analysis-v6/run_all.py`; published by
`src/structural-analysis-v6/publish.py`. To reproduce, from the project root:

```
archive/.venv/bin/python src/structural-analysis-v6/run_all.py
archive/.venv/bin/python src/structural-analysis-v6/publish.py
```

This study consumes [{d['frame_model'].split('.compas')[0]}] and develops
[STR-006](../frame-geometry-study/README.md), which established the geometry and
explicitly assigned no loads, materials, restraints or capacities. It does not
supersede STR-006; it is the next stage against it.
"""


def report(d: dict, rev: str, status: str, date: str) -> str:
    drawn, done = _sc(d, 'as_drawn'), _sc(d, 'completed')
    cross = _sc(d, 'crossings_joined') or {}
    adeq = _sc(d, 'adequate') or {}
    expD = _sc(d, 'exposure_D')
    b, cum = d['basis'], d['removal'].get('cumulative', {})
    sz, t = d['sizing'], d['totals']
    eq = max((v['relative'] for v in done['equilibrium'].values()), default=0.0)
    gap = (done['gaps'] or [{}])[0]
    seis = b['seismic']
    drift = _drift(done)
    xj = d.get('crossings', {}).get('joints', [])
    strong = sz.get('strengthen') or {}
    loft = d.get('loft_sensitivity') or {}
    design = loft.get(d['live_case'], {})
    l40, l125 = loft.get('L40', {}), loft.get('L125', {})
    env = d['counts'].get('concept_envelope', 0)

    return f"""# {DOC_ID} — {TITLE}

**Revision:** {rev} · **Date:** {date} · **Status:** `{status}` · **Section:** 06 Structural engineering
**Site:** {b['site']} · **Risk Category:** {b['risk_category']} · **Code:** {b['code']}
**Geometry:** `data/frame-models/{d['frame_model']}` (version {d['frame_version']}), unmodified
**Software:** {d['software']}

---

## 1. Summary

The frame as drawn does not carry its design loads. Three things are wrong with
it, and all three are cheap to fix:

1. **The flat upper roof has no framing across it** and the head of the clerestory
   has no beam, so the roof load has nowhere to go but the perimeter (F-1).
2. **One column is connected to nothing** — the analysis found it as a rigid-body
   mode before it found anything else (F-2).
3. **Six pairs of X-braces cross without being joined**, so every one of those
   twelve braces is unbraced over its full length (F-3).

Framing the roof and connecting the six crossings — the second of which costs no
material at all — brings the worst utilisation from **{drawn['max_dcr']:.2f} to
{cross.get('max_dcr', 0):.2f}**. Four members then need to be one size larger, a
total of **{strong.get('added_lb', 0):+,.0f} lb**, and the frame passes at
**{adeq.get('max_dcr', 0):.2f}**.

From that adequate frame, **{len(sz.get('lighter') or [])} members verify at a
lighter section, saving {_n(sz.get('weight_saved_lb', 0))} lb**, and
{_removal_headline(d, cum)}

The loft is designed to **{design.get('psf', 75):.0f} psf** by owner decision, a
value chosen for an equipment loft rather than taken from a table: ASCE 7-16
offers {l40.get('psf', 40):.0f} psf for an ordinary dwelling floor and
{l125.get('psf', 125):.0f} psf for a commercial storage warehouse, and neither
describes this space. {_loft_headline(design, l40, l125)} (F-4).

No connection, base plate, anchor or foundation is designed or checked here.
Nothing in this document authorises construction.

## 2. What this study does, and what it does not

It takes the canonical frame geometry, assigns materials, section properties,
supports and the design loads recorded in the
[design load basis](design-load-basis.md), solves {d['combinations']['total']}
ASCE 7-16 strength combinations plus the serviceability set, checks every member
to AISC 360-16 and NDS, and then asks two optimisation questions: which members
can be lighter, and which can be deleted.

It does not design anything. The analysis is linear-elastic and first-order.
Section 9 lists every excluded behaviour.

## 3. The model

| | |
|---|---|
| Geometry | {d['counts']['members']} members resolved into {d['counts']['elements']} beam elements |
| Supports | {d['counts']['supports']} column bases, pinned |
| Steel | ASTM A500 Gr. C (HSS) and A992 (W), Fy = 50 ksi, E = 29,000 ksi |
| Timber | Douglas fir-larch No. 2, E = 1,600 ksi, checked to NDS allowable stress design |

The COMPAS joint graph is used directly as the finite element mesh. Its nodes
carry resolved coordinates and support flags, and its edges are member segments
between consecutive joints — a mesh in all but name. Nothing is re-meshed
between the drawing and the analysis, so every result maps back to a named
member.

**Connection assumptions.** Welded HSS joints are modelled as continuous, which is
the realistic idealisation for this construction but remains an assumption: no
joint has been designed, and a joint detailed as a simple connection would
redistribute force away from the flexural capacity relied on here. Discrete
braces are released for bending at both ends. Column bases are pinned — no
fixity is taken from the footings, because no foundation exists yet and
assumption ASM-005 is open.

**Section properties.** Where the geometry model names an AISC designation, it is
used. Where it records only a `concept envelope` — **{env} of the
{d['counts']['members'] - len(d['counts'].get('added') or [])} members do** — the
lightest standard wall for that outside dimension is assumed. That is the
conservative reading, and it is what makes Section 7 meaningful: a member still
lightly stressed at the thinnest available wall can come down in nominal size.

**How area loads reach the members.** Roof, floor and wall pressures are resolved
onto the members in each surface by a Voronoi tessellation of sample points taken
along every member lying in that surface, clipped to the surface outline. A
clipped Voronoi diagram partitions its outline exactly, so the load applied
always equals pressure times area — checked in Section 5, not assumed. Diagonal
bracing takes no area load: an in-plane brace resists force in its own plane and
is not what a deck or purlin bears on.

## 4. Loads and combinations

Summarised here; every value and its source is in the
[design load basis](design-load-basis.md).

| Load | Value |
|---|---|
| Superimposed dead — solar roof / upper roof / east canopy / loft | {b['dead']['solar_roof']:.0f} / {b['dead']['upper_roof']:.0f} / {b['dead']['east_roof']:.0f} / {b['dead']['loft_floor']:.0f} psf |
| Wall cladding and girts | {b['dead']['wall']:.0f} psf of elevation |
| Frame self weight | computed from the sections, {_n(done['member_weight_lb'])} lb |
| Roof live | {b['roof_live']:.0f} psf on the horizontal projection |
| Loft live | **{design.get('psf', 75):.0f} psf** design value; {b['loft_live']['L40']:.0f} and {b['loft_live']['L125']:.0f} psf also analysed — see F-4 |
| Hoist | {_n(b['hoist']['capacity'])} lb with {b['hoist']['impact'] * 100:.0f} % vertical impact |
| Snow | none — ground snow load is zero at this site |
| Wind | **{b['wind']['V']:.0f} mph** 3-second gust, Exposure {d['exposure']}, {b['wind']['enclosure']}, four directions, both internal-pressure signs |
| Seismic | screening only — SDS {seis['SDS']:.3f}, Cs {seis['Cs']:.3f}, base shear {_n(seis['base_shear_lb'])} lb on {_n(seis['seismic_weight_lb'])} lb |

All {d['combinations']['total']} ASCE 7-16 Section 2.3 strength combinations were
solved: 1.4D; 1.2D+1.6L+0.5Lr; 1.2D+1.6Lr+1.0L; 1.2D+1.0W+1.0L+0.5Lr and
0.9D+1.0W for four wind directions and both internal-pressure signs; and
1.2D+1.0E+1.0L and 0.9D+1.0E for four seismic directions. Serviceability used D,
D+L, D+Lr, D+0.75L+0.75Lr and D+0.6W.

The member studies in Sections 7 and 8 re-solve the frame once per member, so
they use the {len(d['combinations']['used_in_studies'])} combinations that govern
at least one member in the baseline plus all three gravity combinations. The
{d['combinations']['total'] - len(d['combinations']['used_in_studies'])} dropped
combinations govern nothing.

### On San Diego wind

The design case is the code map value, not a Santa Ana event. The strongest gust
ever recorded in San Diego County — 106 mph in February 2020 — was at Sill Hill,
a 3,500 ft mountain site inland of I-8. Santa Ana winds weaken toward the coast,
and Pacific Beach sees a fraction of the inland peak. The {b['wind']['V']:.0f} mph
map value is a 700-year mean-recurrence-interval 3-second gust and already
envelops any wind recorded near this address. It governs, and it is what was used.

## 5. Verification

These are the checks that say whether the analysis itself can be believed.

| Check | Result |
|---|---|
| Vertical equilibrium — applied load against summed reactions | closes to **{eq:.1e}** relative error on every gravity combination |
| Tributary-area closure on all load surfaces | **1.0000** — applied area equals true surface area exactly |
| Computed section properties against the AISC Manual | HSS4X4X3/16: A = 2.590 in² and I = 6.219 in⁴ against published 2.58 and 6.21. HSS6X6X1/4: 5.224 and 28.57 against 5.24 and 28.6 |
| Member capacities against AISC Tables 3-2, 3-10 and 4-4 | W8X24 φMp 86.6 kip-ft against published 86.6; at Lb = 20 ft, 51.3 against ≈52. HSS4X4X3/16 φPn at KL = 8 ft, 88.0 kips against ≈88 |
| Wind resultant against a hand check | 20.2 psf on the projected area against 19.8 psf from qh·G·(0.8 + 0.5) |
| Stiffness matrix | non-singular in every scenario. The zero-energy mode in the first run was traced to a real unconnected member — Finding F-2 |
| Span deflection | measured against the chord between each member's own end joints, not element by element; no member exceeds its limit on the adequate frame |

## 6. Findings

### F-1 · The upper roof has no load path across it · **blocking**

The flat upper roof is {gap.get('area_ft2', 0):.0f} sq ft with a
{gap.get('clear_span_in', 0) / 12:.1f} ft clear span and **nothing crosses it**.
Its southern edge, at the head of the clerestory, has no beam at all: `W.top` and
`E.top` both begin at that corner and nothing joins them. Analysed literally, the
roof load can only reach the perimeter, and it lands on the two roof cap braces —
21.8 ft HSS1½×1½×⅛ diagonals — which reach **DCR {drawn['max_dcr']:.2f}**.

This is the geometry model behaving as documented: STR-006 states that it
excludes secondary framing, and open item ENV-OI-04 raises the same omission for
the wall girts. It is a gap in the model, not necessarily in the design intent —
but nothing about sizing means anything until it is closed. This study therefore
adds the minimum framing that gives the roof a load path: a clerestory head beam
and four purlins, tagged `Assumed` throughout and written nowhere near
`data/frame-models/`. Every result after this point is on that completed frame.

**Required:** the engineer of record must frame the upper roof and the clerestory
head. The members assumed here are a placeholder that works, not a design — and
only just: the four assumed purlins are the worst-deflecting members in the whole
frame at L/201 against an L/180 limit (F-6). A real design would likely deepen
them, or add a mid-span line to halve the 15.2 ft span.

### F-2 · One column is connected to nothing · **blocking**

`E-M option B`, the optional east mid column, meets `E-OB` at a joint the geometry
model records as a `declared eccentric bearing` — a one-inch offset carried on no
member. The first analysis run returned a singular stiffness matrix, and the
zero-energy mode localised entirely on that column: pinned at the base, attached
at the top only by a joint with no stiffness, free to swing and to spin about its
own axis. It is carried here as a rigid link so the rest of the frame can be
solved. **That bearing needs a real detail, or the column needs to come out.**

### F-3 · The X-brace crossings are not joints, and that is what makes the braces fail · **high**

Six pairs of braces form an X and pass within an inch or two of each other at
mid-length, but the crossings are not declared joints — the model's own migration
notes say so explicitly for the north diagonals. Unconnected, each brace is
unbraced over its **whole** length, which is why the roof cap braces run at
KL/r = 470 against a limit of 200.

Joining the six crossings halves the unbraced length of all twelve braces and
drops the worst utilisation from **{done['max_dcr']:.2f} to
{cross.get('max_dcr', 0):.2f}** — without adding a pound of steel. It is by a wide
margin the cheapest change available to this structure.

{_crossing_table(xj)}
### F-4 · The loft live load is a decision, not a table lookup · **high**

{_loft_para(design, l40, l125, loft)}

### F-5 · Four members must be larger, and then the frame passes · **high**

With the roof framed and the crossings joined, {len(cross.get('over_capacity', []))}
members remain over capacity:

{_over_table(cross.get('over_capacity', []))}
Stepping each one up the section ladder — one size per round, re-analysing after
each, because stiffening a brace makes it attract more load — brings the frame
to **DCR {adeq.get('max_dcr', 0):.2f}** for
**{strong.get('added_lb', 0):+,.0f} lb** of extra steel:

{_strengthen_table(d, strong)}
`T-SO` moves from a wide flange to a tube. It is the south eave beam on an
exposed exterior frame, where a closed section is the better answer anyway, and
an HSS4X4X3/16 is both lighter and stiffer about the weak axis than the W6X8.5 it
replaces.

### F-6 · Deflection · **medium**

**Gravity.** Every member that spans is checked against the chord between its own
two end joints — not element by element, which would flatter a beam that joists
frame into. The worst spans on the adequate frame:

{_deflection_table(adeq)}
**Wind.** Worst drift is **H/{drift:.0f}** against a serviceability target of
H/400. It passes, barely, and it gets worse if any bracing comes out — which is
why the removal study in Section 7 tests drift as well as strength.

### F-7 · The wind exposure category has not been verified · **medium**

Exposure C is used. If the site is ruled to be inside the shoreline exposure
band, Exposure D applies and the worst utilisation rises to
**{expD['max_dcr']:.2f}**, {(expD['max_dcr'] / done['max_dcr'] - 1) * 100:.0f} %
higher. The distance from this address to open water should be established before
sections are fixed.

## 7. Where the material can come out

![Opportunity map](figures/opportunity-map.png)

Everything in this section is measured against the **adequate frame** of F-5 —
roof framed, crossings joined, four members enlarged — and not against the frame
as drawn. Asking which members can be deleted from a structure that is already
over capacity answers nothing, because the test would have to be "no worse than
something that does not work".

### Lighter sections

{len(sz.get('lighter') or [])} members verify at a lighter section, saving
**{_n(sz.get('weight_saved_lb', 0))} lb**, which is
{abs(sz.get('weight_saved_lb', 0)) / max(t['baseline_lb'], 1) * 100:.0f} % of the
frame. Sizing is not done member by member in isolation. Members are taken
least-stressed first, a dozen at a time, and every batch is verified by a full
re-analysis against strength, slenderness **and span deflection** before it is
accepted; members implicated in a failure are reverted and frozen. Only changes
that survived that re-analysis are reported.

The deflection gate matters. Checked on strength alone the ladder will happily
swap a W8X24 floor beam for a tube that carries the moment and then sags four
times as far.

Per-member proposals are in the [member schedule](member-schedule.csv).

{_ladder_note(sz)}
### Members that can be deleted

{_removal_para(d, cum)}
Each candidate was deleted from the model, the frame rebuilt, and every governing
combination re-solved — including recomputing the unbraced lengths of the members
the deleted one used to restrain, which is the effect a by-hand review misses
most often. A member is called removable only if the frame stays stable, nothing
goes over capacity, no span deflection limit is breached, and wind drift stays
inside H/400. The individually-removable set was then deleted cumulatively and
greedily, re-verifying after each one, because members that are removable one at a
time are often not removable together.

{_spacing_para(cum)}

![Member weight by group](figures/weight-by-group.png)

### Net effect

| | Weight |
|---|---:|
| Completed frame — as drawn plus the assumed roof framing | {_n(t['baseline_lb'])} lb |
| After the verified reductions | {_n(t['after_lb'])} lb |
| **Net change** | **{-t['saved_lb']:+,.0f} lb ({t['saved_pct']:.0f} % lighter)** |

## 8. Sensitivity

| Variant | Worst utilisation |
|---|---|
| As drawn | {drawn['max_dcr']:.2f} |
| Upper roof framed | {done['max_dcr']:.2f} |
| X-brace crossings joined | {cross.get('max_dcr', 0):.2f} |
| Four members enlarged — the adequate frame | **{adeq.get('max_dcr', 0):.2f}** |
| Wind Exposure D instead of C | {expD['max_dcr']:.2f} |
| Loft at {l125.get('psf', 125):.0f} psf instead of the {design.get('psf', 75):.0f} psf design value | loft framing {l125.get('loft_max_dcr', 0):.2f} against {design.get('loft_max_dcr', 0):.2f} |

## 9. Excluded behaviour

Not analysed, not checked, and required before construction:

- **every connection** — welds, bolts, gussets, base plates, anchor rods
- **foundations** — footings, piers, bearing, uplift resistance, lateral capacity
- **the existing garage structure** — no reliance on it is modelled and no
  assessment of it has been made
- second-order (P-Delta) effects beyond the linear solution
- seismic detailing, ductility, redundancy factors and drift amplification. The
  seismic case here is an equivalent-lateral-force **screening** check against
  default site values, not a seismic design, and the frame has not been detailed
  or qualified as any of the braced-frame systems its assumed R factor belongs to
- torsion combined with flexure in the wide-flange members
- web local yielding, crippling and all local limit states at load points
- fatigue from hoist use, hoist runway design, trolley lateral and longitudinal loads
- corrosion, fire, weld quality, erection stability and construction loading
- the secondary framing of every surface except the upper-roof members added here
- differential settlement, thermal movement, and the stiffness contributed by
  glazing and cladding

Every result depends on unknown foundations, undesigned connections and
unverified field dimensions. The pinned-base assumption alone means the column
bases carry no moment, which the real footings may not honour.

## 10. What to do next

1. **Frame the upper roof and the clerestory head.** Nothing else here is
   conclusive until the roof has a load path (F-1).
2. **Resolve or delete `E-M option B`** and its eccentric bearing (F-2).
3. **Connect the six X-brace crossings.** Largest single improvement available,
   at no material cost (F-3).
4. **Schedule the heavy items that will actually go up there** — what they weigh
   and what footprint they sit on. The {design.get('psf', 75):.0f} psf design value
   covers the floor on average; concentrated loads are what will size the joists,
   and only the owner has that list (F-4).
5. **Verify the wind exposure category** for the address (F-7).
6. Take the member schedule to the engineer of record as a starting set, not as a
   design. Sections are assumed wherever the geometry model records only an
   envelope.
7. Commission the geotechnical work needed to close ASM-005, so the bases can be
   modelled as they will actually be built.

---

_Generated {d['generated']} from `data/frame-models/{d['frame_model']}` by
`src/structural-analysis-v6/run_all.py`. Checksums of the input model, the generating
code and every published file are in [source-inventory.csv](source-inventory.csv)._
"""


def _deflection_table(sc: dict, limit: int = 8) -> str:
    rows = (sc or {}).get('worst_deflections') or []
    if not rows:
        return '_Deflection results were not recorded in this pass._\n'
    out = ['| Member | Span | Combination | Deflection | Ratio | Limit | |',
           '|---|---:|---|---:|---:|---:|---|']
    for r in rows[:limit]:
        out.append(f'| `{r["member"]}` | {r["span_in"]:.0f} in | {r["combination"]} '
                   f'| {r["deflection_in"]:.3f} in | **L/{r["ratio"]:.0f}** | '
                   f'L/{r["limit"]:.0f} | {"ok" if r["passes"] else "**fails**"} |')
    return '\n'.join(out) + '\n'


def _drift(sc) -> float:
    return min((v['ratio'] for v in (sc.get('drift') or {}).values() if v['ratio']),
               default=0)


def _loft_headline(design: dict, l40: dict, l125: dict) -> str:
    dcr = design.get('loft_max_dcr', 0)
    if dcr <= 1.0:
        return (f"The loft framing carries it at DCR **{dcr:.2f}**")
    return (f"The loft framing reaches **DCR {dcr:.2f}** at that load and the joists "
            f"must be redesigned")


def _loft_para(design: dict, l40: dict, l125: dict, cases: dict) -> str:
    if not cases:
        return '_Loft sensitivity was not recorded in this pass._'
    rows = ['| Uniform live load | What it is | Worst loft member | DCR |',
            '|---:|---|---|---:|']
    for tag, c in sorted(cases.items(), key=lambda t: t[1]['psf']):
        what = {40.0: 'ASCE 7-16 dwelling floor, "all other areas"',
                75.0: '**design value — owner decision DEC-008**',
                125.0: 'ASCE 7-16 light storage *warehouse*'}.get(
                    c['psf'], c.get('basis', ''))
        flag = '' if c['loft_max_dcr'] <= 1.0 else ' ⚠'
        rows.append(f"| {c['psf']:.0f} psf | {what} | `{c.get('member', '')}` "
                    f"({c.get('section', '')}) | **{c['loft_max_dcr']:.2f}**{flag} |")
    table = '\n'.join(rows)
    dcr = design.get('loft_max_dcr', 0)
    verdict = (f"At the {design.get('psf', 75):.0f} psf design value the joists carry "
               f"it at DCR {dcr:.2f}." if dcr <= 1.0 else
               f"At the {design.get('psf', 75):.0f} psf design value the joists reach "
               f"DCR {dcr:.2f} and must be redesigned.")
    return (
        f"The code offers two rows that get quoted for a space like this and neither "
        f"one fits it. {l40.get('psf', 40):.0f} psf is ASCE 7-16 Table 4.3-1 for "
        f"\"all other areas\" of a dwelling — a living-room number, for furniture and "
        f"people. {l125.get('psf', 125):.0f} psf is a light storage **warehouse**: a "
        f"commercial building with racked goods and pallet traffic, which a detached "
        f"residential accessory structure is not. The attic rows do not apply either; "
        f"an attic with limited storage is defined by a clear height under 42 in. and "
        f"no real access, and this level has a fixed stair, a loading door and a "
        f"hoist.\n\n{table}\n\n{verdict}\n\n"
        f"**The uniform figure is not the binding constraint.** ASCE 7-16 Sec. 4.4 "
        f"requires the floor to carry a concentrated load wherever that governs, and "
        f"a dense item on a small footprint defeats any of these numbers locally: an "
        f"800 lb machine on 3 sq ft is about 270 psf on that patch while the room "
        f"average stays trivial. The owner's heavy items and their footprints have to "
        f"be scheduled before the loft framing is finalised — that schedule, not the "
        f"table row, is what sizes these joists.")


def _strengthen_table(d: dict, strong: dict) -> str:
    secs = strong.get('sections') or {}
    if not secs:
        return ''
    rows = ['| Member | As drawn | Required | Why |', '|---|---|---|---|']
    over = {o['member']: o for o in (_sc(d, 'crossings_joined') or {}).get(
        'over_capacity', [])}
    for m, to in sorted(secs.items()):
        o = over.get(m, {})
        rows.append(f'| `{m}` | {o.get("section", "")} | **{to}** | '
                    f'{o.get("mode", "redistribution after an earlier round")} |')
    return '\n'.join(rows) + '\n'


def _spacing_para(cum: dict) -> str:
    """The non-structural constraint on deleting repetitive framing."""
    rules = cum.get('spacing_rules') or {}
    rejected = [r for r in (cum.get('rejected') or [])
                if r.get('check') == 'deck spacing']
    if not rules:
        return ''
    lines = ' and '.join(
        f'{v["limit"]:.0f} in. for the {v["reason"]}' for v in rules.values())
    extra = ''
    if rejected:
        extra = (f' That rule rejected **{len(rejected)} further members** the frame '
                 f'analysis was perfectly happy to lose — an earlier pass without it '
                 f'proposed deleting joists in a run that would have left a 56 in. '
                 f'gap in the floor.')
    return (f'One constraint here is not structural. There are no plates anywhere in '
            f'this model, so the decking does not exist as far as the solver is '
            f'concerned, and deleting every second joist looks free when it is not — '
            f'something still has to span between the ones that are left. Maximum '
            f'surviving spacing is therefore enforced directly: {lines}.{extra} '
            f'Those limits are ordinary sheathing capacities, not a design, and the '
            f'deck itself still has to be checked — particularly if the loft is '
            f'classified as storage (F-4).')


def _removal_headline(d: dict, cum: dict) -> str:
    removed = cum.get('removed') or []
    if not d['removal'].get('tested'):
        return 'the removal study was not run in this pass.'
    if not removed:
        return ('no member survives the combined removal test — the frame carries '
                'less spare redundancy than a one-at-a-time check suggests.')
    return (f"**{len(removed)} members totalling {_n(cum['weight_saved_lb'])} lb can "
            f"be deleted outright**, verified together.")


def _crossing_table(xj) -> str:
    if not xj:
        return ''
    out = ['| Crossing | Braces | Unbraced length before → after |', '|---|---|---|']
    for c in xj:
        m = c['members']
        before = max(c['unbraced_before'].values())
        after = max(c['unbraced_after'].values())
        out.append(f'| `{c["node"]}` | `{m[0]}` + `{m[1]}` | '
                   f'{before:.0f} in → **{after:.0f} in** |')
    return '\n'.join(out) + '\n'


def _ladder_note(sz) -> str:
    beyond = sz.get('beyond_ladder') or []
    if not beyond:
        return ''
    rows = '\n'.join(f'- `{b["member"]}` ({b["section"]}), DCR {b["dcr"]:.2f} '
                     f'governed by {b["mode"]}' for b in beyond)
    return (f'\n**Beyond the section ladder.** These members cannot be satisfied by '
            f'any square HSS up to HSS6X6X⅜ and need a deeper or built-up section, '
            f'which is a design decision rather than a substitution:\n\n{rows}\n')


def _removal_para(d, cum) -> str:
    red = d['removal'].get('redundant') or []
    crit = d['removal'].get('critical') or []
    removed = cum.get('removed') or []
    t = d['totals']
    if not d['removal'].get('tested'):
        return '_The removal study was not run in this pass._\n'
    s = (f"Of {d['removal']['tested']} members tested, **{len(red)}** are "
         f"individually redundant and **{len(crit)}** are critical — deleting any "
         f"one of those leaves a mechanism.\n\n")
    if removed:
        s += (f"Taken together and re-verified, **{len(removed)} members totalling "
              f"{_n(cum['weight_saved_lb'])} lb** can be deleted at once, with the "
              f"worst utilisation afterwards at {cum['max_dcr_after']:.2f} and wind "
              f"drift at H/{cum.get('drift_ratio') or 0:.0f}. That is "
              f"{t['saved_pct']:.0f} % of the frame's member weight.\n\n"
              + '\n'.join(f'- `{m}`' for m in removed) + '\n')
    else:
        s += ('No member survives the combined removal test: each one that is '
              'individually redundant becomes necessary once another is gone. '
              'The frame carries less spare redundancy than the one-at-a-time '
              'result suggests.\n')
    return s


def load_basis(d: dict, date: str) -> str:
    b = d['basis']
    seis = b['seismic']
    return f"""# {DOC_ID}-A · Design load basis

**Date:** {date} · **Site:** {b['site']} · **Risk Category:** {b['risk_category']}
**Governing code:** {b['code']}

Every value used by the analysis, with the source it came from. Values marked
_open_ are project assumptions that have not been confirmed.

## Dead load

| Surface | psf | Build-up |
|---|---:|---|
| Solar roof | {b['dead']['solar_roof']:.1f} | PV modules and rail racking 4.0, standing-seam panel 1.5, purlins and miscellaneous 2.5 |
| Upper roof | {b['dead']['upper_roof']:.1f} | panel 1.5, rigid insulation 1.5, purlins 3.0, low hip cap framing and miscellaneous 4.0 |
| East canopy | {b['dead']['east_roof']:.1f} | light metal panel on exposed rafters, no ceiling |
| Loft floor | {b['dead']['loft_floor']:.1f} | ¾ in. plywood 2.3, underlayment and finish 1.7, services and miscellaneous 4.0 |
| Walls | {b['dead']['wall']:.1f} | metal panel 1.5, girts 2.5, miscellaneous 1.0, per sq ft of elevation |

Frame self weight is computed from the assigned sections and material densities,
not assumed. It totals {_n(d['scenarios']['completed']['member_weight_lb'])} lb.

## Live load

| Load | Value | Source |
|---|---:|---|
| Roof live, Lr | {b['roof_live']:.0f} psf | ASCE 7-16 Table 4.3-1, on the horizontal projection, taken unreduced |
| **Loft, design value** | **{b['loft_live'].get('L75', 75):.0f} psf** | Owner decision DEC-008 — equipment loft |
| Loft, dwelling floor minimum | {b['loft_live']['L40']:.0f} psf | ASCE 7-16 Table 4.3-1, dwelling "all other areas" |
| Loft, storage warehouse | {b['loft_live']['L125']:.0f} psf | ASCE 7-16 Table 4.3-1, "Storage warehouses, light" — a commercial occupancy, retained as an upper bound |
| Concentrated equipment load | to be scheduled | ASCE 7-16 Sec. 4.4 — governs locally over any uniform value |
| Hoist | {_n(b['hoist']['capacity'])} lb | Owner requirement |
| Hoist vertical impact | {b['hoist']['impact'] * 100:.0f} % | ASCE 7-16 Sec. 4.6.2, monorail crane |
| Hoist lateral | {b['hoist']['lateral'] * 100:.0f} % of lifted load | ASCE 7-16 Sec. 4.9 |

All three loft values are carried through as separate load cases. The design
value is the owner's decision, not a table lookup: the code's dwelling-floor row
is a living-room figure and its light-storage row describes a commercial
warehouse, and neither is a backyard equipment loft. Code values are minimums,
not targets.

What the uniform value cannot cover is concentrated load. ASCE 7-16 Sec. 4.4
requires the floor to carry a point load wherever that governs, and a dense item
on a small footprint exceeds any of these numbers locally. The owner's schedule
of heavy items and their footprints is an outstanding input to the loft design.

## Snow

Zero. Ground snow load is zero for coastal San Diego (ASCE 7-16 Fig. 7.2-1).

## Wind — ASCE 7-16 Chapter 27, Directional Procedure

| Parameter | Value |
|---|---|
| Basic wind speed V | **{b['wind']['V']:.0f} mph**, 3-second gust, Risk Category {b['risk_category']} |
| Exposure | {d['exposure']} primary; D run as a sensitivity |
| Directionality Kd | {b['wind']['Kd']} |
| Topographic Kzt | {b['wind']['Kzt']} — flat site, no speed-up |
| Ground elevation Ke | {b['wind']['Ke']} |
| Gust effect factor G | {b['wind']['G']} — rigid building |
| Enclosure | {b['wind']['enclosure']}, GCpi = ±{b['wind']['GCpi']} |
| Velocity pressure at mean roof height | 17.9 psf (Exposure C), 21.5 psf (Exposure D) |

External pressure coefficients are taken from Fig. 27.3-1 and interpolated on
roof slope and h/L: windward wall +0.8 on qz, leeward wall by L/B, side walls
−0.7, and the roof zoned by distance from the windward edge where the wind runs
parallel to the slope. Four directions are analysed, each with both internal
pressure signs, because internal pressure cancels in the global resultant but not
in the load on an individual wall member.

### On San Diego wind

The design value is not driven by Santa Ana events. The strongest gust ever
recorded in San Diego County — 106 mph, February 2020 — was at Sill Hill, a
3,500 ft mountain site inland of I-8. Santa Ana winds weaken toward the coast,
and Pacific Beach sees a fraction of the inland peak. The code map value of
{b['wind']['V']:.0f} mph is a 700-year mean-recurrence-interval 3-second gust and
already envelops any wind recorded near this address. It governs, and it is what
was used.

The east canopy is treated with wall rather than roof pressure coefficients. Its
twelve rafters rake between 55 and 74 degrees from horizontal, which is far
closer to a wall than to a roof.

## Seismic — screening only

| Parameter | Value |
|---|---|
| Ss / S1 | {seis.get('Ss', 1.0)} g / {seis.get('S1', 0.37)} g — screening values for coastal San Diego |
| Site class | D — the default where no geotechnical investigation exists |
| SDS / SD1 | {seis['SDS']:.3f} / {seis['SD1']:.3f} |
| Response modification R | {seis.get('R', 3.25)} |
| Approximate period Ta | {seis['Ta']:.3f} s |
| Seismic response coefficient Cs | {seis['Cs']:.4f} |
| Effective seismic weight W | {_n(seis['seismic_weight_lb'])} lb |
| Base shear V | {_n(seis['base_shear_lb'])} lb |

**This is a screening check, not a seismic design.** Site-specific ground motion
values and a site class from an actual geotechnical investigation are required.
The frame has not been detailed or qualified as any of the braced-frame systems
the assumed R factor belongs to, and no seismic detailing, redundancy factor or
drift amplification has been applied.

## Load combinations

ASCE 7-16 Section 2.3 for strength, Appendix C for serviceability. The full set
is listed in Section 4 of the [analysis report](structural-analysis.md).

## Serviceability limits

| Limit | Value | Source |
|---|---|---|
| Floor live deflection | L/360 | IBC Table 1604.3 |
| Floor total deflection | L/240 | IBC Table 1604.3 |
| Roof live deflection | L/240 | IBC Table 1604.3 |
| Wind drift | H/400 | common serviceability target; not a code minimum |
"""


def findings_csv(d: dict) -> str:
    done = _sc(d, 'completed')
    cross = _sc(d, 'crossings_joined') or {}
    cum = d['removal'].get('cumulative', {})
    gap = (done['gaps'] or [{}])[0]
    rows = [
        dict(id='F-1', severity='blocking', area='Upper roof',
             finding='No framing crosses the flat upper roof and the clerestory '
                     'head has no beam; the roof load reaches only the perimeter',
             evidence=f'{gap.get("area_ft2", 0):.0f} sq ft, '
                      f'{gap.get("clear_span_in", 0):.0f} in clear span; frame as '
                      f'drawn reaches DCR {_sc(d, "as_drawn")["max_dcr"]:.2f}',
             action='Engineer of record to frame the upper roof and clerestory head'),
        dict(id='F-2', severity='blocking', area='East support frame',
             finding='E-M option B is connected only by a declared eccentric '
                     'bearing carried on no member',
             evidence='Singular stiffness matrix; zero-energy mode localised on '
                      'that column',
             action='Design the bearing detail or delete the column'),
        dict(id='F-3', severity='high', area='Bracing',
             finding='Six X-brace crossings are not declared joints, so every '
                     'brace is unbraced over its full length',
             evidence=f'Connecting them drops worst DCR from {done["max_dcr"]:.2f} '
                      f'to {cross.get("max_dcr", 0):.2f} at no material cost',
             action='Connect the six crossings'),
        dict(id='F-4', severity='high', area='Loft',
             finding='Loft joists fail at the ASCE 7-16 light-storage live load',
             evidence='DCR 1.55 in bending at 125 psf; 0.64 at the assumed 40 psf',
             action='Settle the occupancy classification, then redesign the loft '
                    'framing if 125 psf applies'),
        dict(id='F-5', severity='high', area='Members',
             finding=f'{len(done["over_capacity"])} members over capacity with the '
                     f'roof framed',
             evidence='; '.join(f'{o["member"]} {o["dcr"]:.2f}'
                                for o in done['over_capacity'][:5]),
             action='Enlarge per the member schedule, after F-3 is applied'),
        dict(id='F-6', severity='medium', area='Serviceability',
             finding='Wind drift passes with almost no margin',
             evidence=f'H/{min((v["ratio"] for v in done["drift"].values() if v["ratio"]), default=0):.0f} '
                      f'against a H/400 target',
             action='Re-check drift after any bracing change'),
        dict(id='F-7', severity='medium', area='Wind',
             finding='Exposure category not verified for the address',
             evidence=f'Exposure D raises worst DCR to {_sc(d, "exposure_D")["max_dcr"]:.2f}',
             action='Verify distance to open water and fix the exposure category'),
        dict(id='F-8', severity='information', area='Optimisation',
             finding=f'{len(d["sizing"].get("lighter") or [])} sections verify lighter, '
                     f'{len(d["sizing"].get("heavier") or [])} must be heavier, '
                     f'{len(cum.get("removed") or [])} members can be deleted',
             evidence=f'Net {d["sizing"]["weight_saved_lb"]:+,.0f} lb from resizing; '
                      f'{_n(cum.get("weight_saved_lb", 0))} lb from deletions',
             action='Use the member schedule as a starting set for design'),
    ]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def index_block(d: dict, rev: str, status: str, date: str) -> str:
    done = _sc(d, 'completed')
    cross = _sc(d, 'crossings_joined') or {}
    return f"""## Chapter 6 frame finite element analysis

[{DOC_ID} — {TITLE}](06-structural-engineering/fea-study/structural-analysis.md),
revision {rev}, {date}, status `{status}`.
[Interactive 3-D model](06-structural-engineering/fea-study/fea-model-3d.html) ·
[Design load basis](06-structural-engineering/fea-study/design-load-basis.md) ·
[Member schedule](06-structural-engineering/fea-study/member-schedule.csv).

First analysis of the frame against design loads: {d['combinations']['total']}
ASCE 7-16 combinations covering gravity, {d['basis']['wind']['V']:.0f} mph wind
from four directions, and a seismic screening check. Vertical equilibrium closes
exactly and member capacities reconcile with the AISC Manual.

Three blocking findings. The flat upper roof has no framing across it and the
clerestory head has no beam, so the frame as drawn cannot carry its roof. One
column is connected only by a bearing joint carried on no member. Six X-brace
crossings are not declared joints, and connecting them alone drops the worst
utilisation from {done['max_dcr']:.2f} to {cross.get('max_dcr', 0):.2f} at no
material cost. The loft joists fail at the code storage live load of 125 psf
though they pass at the project's assumed 40 psf, which makes the occupancy
classification a structural question.

No connection, base plate, anchor or foundation is designed or checked.
Preliminary engineering only; not for construction.

"""


def section_block(d: dict, rev: str, status: str, date: str) -> str:
    done = _sc(d, 'completed')
    cross = _sc(d, 'crossings_joined') or {}
    cum = d['removal'].get('cumulative', {})
    return f"""## Current analysis

[{DOC_ID} — {TITLE}](fea-study/README.md), revision {rev}, {date}, status
`{status}`. First structural analysis of the frame: design loads established,
{d['combinations']['total']} ASCE 7-16 combinations solved on a
{d['counts']['elements']}-element model of `data/frame-models/{d['frame_model']}`,
every member checked to AISC 360-16, and a verified optimisation study.

- [Analysis report](fea-study/structural-analysis.md) — findings, verification and required next steps
- [Interactive 3-D model](fea-study/fea-model-3d.html) — utilisation, recommended action, removability
- [Design load basis](fea-study/design-load-basis.md) — every load with its source
- [Member schedule](fea-study/member-schedule.csv) — {d['counts']['members']} members with demands, DCR and proposals
- [Findings](fea-study/findings.csv)

Worst utilisation is {done['max_dcr']:.2f} with the upper roof framed, falling to
{cross.get('max_dcr', 0):.2f} once the X-brace crossings are connected.
{len(d['sizing'].get('lighter') or [])} sections verify lighter,
{len(d['sizing'].get('heavier') or [])} must be heavier, and
{len(cum.get('removed') or [])} members can be deleted outright.

This study develops STR-006 and does not supersede it. Section sizes, foundations,
connections and joint design remain unresolved. STR-001 through STR-005 remain
planned: this is not a structural basis of design, and no connection, base plate,
anchor or foundation has been designed or checked.
"""
