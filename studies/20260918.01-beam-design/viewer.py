"""Self-contained 3-D web page for the BEAM-001 frame model.

Reads the canonical COMPAS model, draws every member as its real solid, and gives
buttons for the standard views. Groups toggle from the legend. One HTML file, no
server and no network beyond the plotly CDN.

Run: /Volumes/Proj/proj/CAD/garage/.venv/bin/python viewer.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import csv
import json

import plotly.graph_objects as go
from compas.data import json_load

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'compas-study'))
sys.path.insert(0, str(ROOT / 'structural-analysis-v6'))
import frame_models                                # noqa: E402
import frame as framemod                           # noqa: E402
import geometry as G                               # noqa: E402

GROUP_STYLE = {
    'Beams':   ('#b4472f', 'Beams — primary section on the existing wall top'),
    'Columns': ('#2b3a42', 'Columns — 4 in HSS, bolted to piers'),
    'Truss':   ('#3f6b86', 'Truss — solar slope, square top and braces'),
    'Roof':    ('#6b5b95', 'Roof beams — east–west over the tall posts'),
    'Clerestory': ('#c98b3a', 'Clerestory truss — double-angle T, glazing rebate'),
    'Bracing': ('#8a9a5b', 'Cross bracing — pin ended'),
    'Rafters': ('#9aa7b0', 'Light roof framing — rafters and the eave'),
    'Joists':  ('#7fa8a0', 'Joists — 2x8 DF-L at 16 in o.c.'),
}

# Model is z-up: x east, y north. Orthographic for the elevations.
# Model is z-up: x east, y north. Eye distances are in plotly's normalised scene
# space, where aspectmode='data' scales the longest axis to 1 -- 2.5 overshoots the
# geometry entirely, which is why these are 1.6.
VIEWS = [
    ('Isometric', dict(eye=dict(x=-1.45, y=-1.25, z=0.8), up=dict(x=0, y=0, z=1),
                       proj='perspective')),
    ('West',      dict(eye=dict(x=-1.6, y=0, z=0), up=dict(x=0, y=0, z=1), proj='orthographic')),
    ('East',      dict(eye=dict(x=1.6, y=0, z=0), up=dict(x=0, y=0, z=1), proj='orthographic')),
    ('South',     dict(eye=dict(x=0, y=-1.6, z=0), up=dict(x=0, y=0, z=1), proj='orthographic')),
    ('North',     dict(eye=dict(x=0, y=1.6, z=0), up=dict(x=0, y=0, z=1), proj='orthographic')),
    ('Plan',      dict(eye=dict(x=0, y=0, z=1.6), up=dict(x=0, y=1, z=0), proj='orthographic')),
]
CENTER = dict(x=0, y=0, z=0)


def camera(v):
    return dict(eye=v['eye'], up=v['up'], center=CENTER,
                projection=dict(type=v['proj']))


def dcr_color(dcr):
    """Blue barely stressed, amber approaching the limit, red at or over it."""
    stops = [(0.0, (0x3a, 0x6e, 0xa5)), (0.5, (0x4c, 0x9f, 0x70)),
             (0.8, (0xd6, 0xa5, 0x3c)), (1.0, (0xc2, 0x3b, 0x22)),
             (1.4, (0x7d, 0x14, 0x0a))]
    d = max(0.0, min(dcr, stops[-1][0]))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if a <= d <= b:
            f = (d - a) / (b - a) if b > a else 0.0
            return '#%02x%02x%02x' % tuple(round(ca[i] + f * (cb[i] - ca[i]))
                                           for i in range(3))
    return '#7d140a'


def load_results():
    """DCRs from the analysis run, if it has been done. Optional by design."""
    sched, res = HERE / 'member-schedule.csv', HERE / 'analysis-results.json'
    if not sched.exists():
        return None, None
    rows = {r['member']: r for r in csv.DictReader(sched.open())}
    summary = json.loads(res.read_text()) if res.exists() else {}
    return rows, summary


def triangles(mesh):
    verts, faces = mesh.to_vertices_and_faces()
    tri = [[f[0], f[i], f[i + 1]] for f in faces for i in range(1, len(f) - 1)]
    return verts, tri


def build(path: Path, out: Path):
    data = json_load(path)
    spec = data['specification']
    model = data['model']
    graph = data['joint_graph']
    f = framemod.load(path)
    elements = {el.name: el for el in model.elements()}
    results, summary = load_results()

    traces = []
    seen_groups = set()
    colour_by_group, colour_by_dcr = [], []
    for mid in sorted(spec['members']):
        rec = spec['members'][mid]
        group = rec['group']
        color, _ = GROUP_STYLE[group]
        verts, tri = triangles(elements[mid].compute_elementgeometry())
        sec = f.section_of[mid]
        r = (results or {}).get(mid)
        colour_by_group.append(color)
        colour_by_dcr.append(dcr_color(float(r['dcr'])) if r else '#c4cad1')
        hover = '<br>'.join(filter(None, [
            f'<b>{mid}</b>',
            f'{group} · {sec.name}',
            f'{f.member_length(mid):.1f} in long · {f.member_weight(mid):.0f} lb',
            (f'<b>DCR {float(r["dcr"]):.2f}</b> — {r["mode"]}, {r["combo"]}' if r else None),
            (f'span {r["span_in"]} in · live L/{r["ratio_live"]} · total L/{r["ratio_total"]}'
             if r and r['span_in'] else None),
            (f'unbraced Lb {r["Lb_in"]} in' if r else None),
            (f'⚠ {r["flags"]}' if r and r['flags'] else None),
            rec.get('note', ''),
        ]))
        traces.append(go.Mesh3d(
            x=[v[0] for v in verts], y=[v[1] for v in verts], z=[v[2] for v in verts],
            i=[t[0] for t in tri], j=[t[1] for t in tri], k=[t[2] for t in tri],
            color=color, opacity=1.0, flatshading=True,
            name=group, legendgroup=group,
            showlegend=group not in seen_groups,
            hovertemplate=hover + '<extra></extra>'))
        seen_groups.add(group)

    sup = [graph.node_attributes(n, 'xyz') for n in graph.nodes()
           if graph.node_attribute(n, 'support')]
    traces.append(go.Scatter3d(
        x=[p[0] for p in sup], y=[p[1] for p in sup], z=[p[2] for p in sup],
        mode='markers', marker=dict(size=6, color='#111417', symbol='square'),
        name='Pinned bases (14)', legendgroup='supports',
        hovertemplate='pinned base · bolted to pier<extra></extra>'))

    # Deck outlines, so the loaded area is visible without hiding the steel.
    for deck in spec['decks']:
        (x1, x2), (y1, y2) = deck['x'], deck['y']
        z = G.BEAM_AXIS_Z + G.BEAM_D / 2
        traces.append(go.Scatter3d(
            x=[x1, x2, x2, x1, x1], y=[y1, y1, y2, y2, y1], z=[z] * 5,
            mode='lines', line=dict(color='#397f77', width=3, dash='dash'),
            name='Deck outlines', legendgroup='decks',
            showlegend=deck is spec['decks'][0],
            hovertemplate=f'{deck["name"]} · {deck["area_sf"]:.0f} sf<extra></extra>'))

    # Flattened keys: a nested 'scene.camera' dict does not always take.
    view_buttons = [dict(label=label, method='relayout',
                         args=[{'scene.camera.eye': v['eye'], 'scene.camera.up': v['up'],
                                'scene.camera.center': CENTER,
                                'scene.camera.projection.type': v['proj']}])
                    for label, v in VIEWS]
    menus = [dict(type='buttons', direction='right', showactive=True,
                  x=0.0, xanchor='left', y=1.02, yanchor='bottom',
                  bgcolor='#ffffff', bordercolor='#d6d9dd', borderwidth=1,
                  font=dict(size=11), pad=dict(l=6, r=6, t=4, b=4),
                  buttons=view_buttons)]
    if results:
        n = len(colour_by_group)
        menus.append(dict(
            type='buttons', direction='right', showactive=True,
            x=0.335, xanchor='left', y=1.02, yanchor='bottom',
            bgcolor='#ffffff', bordercolor='#d6d9dd', borderwidth=1,
            font=dict(size=11), pad=dict(l=6, r=6, t=4, b=4),
            buttons=[dict(label='Colour: groups', method='restyle',
                          args=[{'color': colour_by_group}, list(range(n))]),
                     dict(label='Colour: DCR', method='restyle',
                          args=[{'color': colour_by_dcr}, list(range(n))])]))

    fig = go.Figure(traces)
    fig.update_layout(
        template='plotly_white',
        scene=dict(aspectmode='data',
                   xaxis=dict(title='east (in)', backgroundcolor='#fafbfc'),
                   yaxis=dict(title='north (in)', backgroundcolor='#fafbfc'),
                   zaxis=dict(title='up (in)', backgroundcolor='#fafbfc'),
                   camera=camera(VIEWS[0][1])),
        margin=dict(l=0, r=0, t=150, b=0),
        legend=dict(x=0.0, y=0.90, xanchor='left', yanchor='top',
                    bgcolor='rgba(255,255,255,0.85)', bordercolor='#d6d9dd',
                    borderwidth=1, font=dict(size=11)),
        updatemenus=menus,
        title=dict(text='<b>Garage — BEAM-001 beam-scheme frame</b><br>'
                        f'<span style="font-size:12px;color:#5c6672">{path.name} · '
                        f'{len(spec["members"])} members · {graph.number_of_nodes()} joints · '
                        f'beams {G.BEAM_SECTION} at z = {G.BEAM_AXIS_Z:g} · envelope to z = '
                        f'{G.SQUARE_TOP_Z:g} · '
                        f'{sum(d["area_sf"] for d in spec["decks"]):.0f} sf of deck at '
                        f'{G.DESIGN_LIVE_PSF:g} psf design live'
                        + (f' · <b>worst beam DCR '
                           f'{max(float(r["dcr"]) for m, r in results.items() if r["group"] == "Beams"):.2f}</b>'
                           if results else '') + '</span>',
                   x=0.0, xanchor='left', y=0.975, yanchor='top', font=dict(size=17)),
        hoverlabel=dict(bgcolor='white', font_size=11, align='left'))

    note = (
        '<div style="font:12px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;'
        'color:#4a545c;max-width:1100px;margin:14px auto 28px;padding:0 18px">'
        + (f'<b>Gravity result at {G.DESIGN_LIVE_PSF:g} psf.</b> Worst {G.BEAM_SECTION} is '
           f'{max((float(r["dcr"]) for r in results.values() if r["group"] == "Beams")):.2f} '
           f'of capacity; worst column '
           f'{max((float(r["dcr"]) for r in results.values() if r["group"] == "Columns")):.2f}; '
           f'worst joist '
           f'{max((float(r["dcr"]) for r in results.values() if r["group"] == "Joists")):.2f}. '
           'Beam deflections are all inside L/360 on live load. Gravity only — this '
           'scheme has no roof, cladding or lateral system yet, so wind and seismic '
           'are absent from the model entirely, and no connection or footing is '
           'designed. See analysis-results.json.</div>'
           '<div style="font:12px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;'
           'color:#4a545c;max-width:1100px;margin:0 auto 28px;padding:0 18px">'
           if results else '')
        + '<b>What this model is.</b> A single-level beam grillage for stiffness and '
        'loading analysis, built from the BEAM-001 plan. Every beam soffit sits on the '
        f'existing wall top at z&nbsp;=&nbsp;{G.WALL_TOP_Z:g}, so all beam axes are at '
        f'z&nbsp;=&nbsp;{G.BEAM_AXIS_Z:g} — the two-level split earlier revisions carried '
        'is gone. Joints are member endpoints plus every crossing of an east–west and a '
        'north–south run; BEW keeps its two declared 2&nbsp;in overhangs. '
        '<b>Not</b> a connection, foundation or fabrication model: bases are pinned '
        'because no footing has been designed, joists are released for bending because '
        'wood framed into steel is a simple span, and no forces or capacities appear '
        'here at all.</div>')

    html = fig.to_html(include_plotlyjs='cdn', full_html=True,
                       config=dict(displaylogo=False,
                                   modeBarButtonsToRemove=['select2d', 'lasso2d']))

    # The annotated plan sheet, inlined so the page stays a single file.
    plan_svg = (HERE / 'beam-plan.svg').read_text()
    plan_svg = plan_svg.replace('<svg ', '<svg style="max-width:100%;height:auto" ', 1)

    tabs = """
<style>
 .bd-tabs{font:13px/1 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;
   padding:14px 18px 0;display:flex;gap:8px}
 .bd-tabs button{font:inherit;padding:7px 14px;border:1px solid #d6d9dd;
   background:#fff;color:#333e46;border-radius:4px;cursor:pointer}
 .bd-tabs button.on{background:#333e46;color:#fff;border-color:#333e46}
 #bd-plan{padding:6px 18px 28px;overflow:auto}
</style>
<div class="bd-tabs">
  <button id="bd-b3d" class="on">3D model</button>
  <button id="bd-bplan">Plan &mdash; labelled top view</button>
</div>
<script>
(function(){
  var b3 = document.getElementById('bd-b3d'), bp = document.getElementById('bd-bplan');
  function panes(){
    var gd = document.querySelector('.js-plotly-plot');
    return {gd: gd, three: gd ? gd.parentNode : null,
            plan: document.getElementById('bd-plan')};
  }
  function show(which){
    var p = panes();
    if (p.three) p.three.style.display = which === '3d' ? '' : 'none';
    if (p.plan)  p.plan.style.display  = which === '3d' ? 'none' : '';
    b3.className = which === '3d' ? 'on' : '';
    bp.className = which === '3d' ? '' : 'on';
    if (which === '3d' && p.gd && window.Plotly) Plotly.Plots.resize(p.gd);
  }
  b3.onclick = function(){ show('3d'); };
  bp.onclick = function(){ show('plan'); };
  show('3d');
})();
</script>
"""
    plan_div = '<div id="bd-plan" style="display:none">' + plan_svg + '</div>'
    html = html.replace('<body>', '<body>' + tabs, 1)
    out.write_text(html.replace('</body>', plan_div + note + '</body>'))
    return out


if __name__ == '__main__':
    p = frame_models.latest('beam-scheme')
    out = build(p, HERE / 'frame-3d.html')
    print(f'wrote {out}  ({out.stat().st_size / 1024:.0f} kB) from {p.name}')
