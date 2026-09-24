"""Interactive 3-D model drawn at true section size.

The line-based viewer gives every member a width in screen pixels, which does
not scale with zoom and carries no information: a 1-1/2 in. brace and a 12 in.
beam differ by a couple of pixels and look the same at any distance. Here each
member is extruded as its actual cross-section, in inches, in the same
coordinate space as the frame -- so a W12X16 reads as twelve inches deep next to
a four-inch column, because it is.

Sections are drawn as what they are: a wide flange as two flanges and a web, a
double-angle tee as a flange and a stem, an HSS or a joist as its outside
rectangle. Everything is one Plotly mesh per member so the hover text still
carries the member's whole schedule row, and the colouring still switches
between utilisation, recommended action, removability and what governs.
"""
from __future__ import annotations

import base64
import json
import math
from pathlib import Path

import plotly.graph_objects as go

import existing as EX
import frame as framemod
import sections as S
import viewer
import visualize
import moment_frames as MF

# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------


def _axes(a, b):
    """Member axis plus two perpendicular axes, with the depth axis kept upright."""
    ex = [b[k] - a[k] for k in range(3)]
    n = math.sqrt(sum(c * c for c in ex)) or 1.0
    ex = [c / n for c in ex]
    up = (0.0, 0.0, 1.0)
    if abs(ex[2]) > 0.98:                      # a column: pick any level reference
        up = (1.0, 0.0, 0.0)
    ey = _cross(up, ex)
    m = math.sqrt(sum(c * c for c in ey)) or 1.0
    ey = [c / m for c in ey]
    ez = _cross(ex, ey)
    return ex, ey, ez


def _cross(u, v):
    return [u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]]


def _box(a, b, ey, ez, width, depth, off_y=0.0, off_z=0.0):
    """Vertices and triangles of one rectangular prism from a to b."""
    hw, hd = width / 2.0, depth / 2.0
    verts = []
    for end in (a, b):
        for sy, sz in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)):
            verts.append([end[k] + (sy + off_y) * ey[k] + (sz + off_z) * ez[k]
                          for k in range(3)])
    faces = [(0, 1, 2), (0, 2, 3),            # start cap
             (4, 6, 5), (4, 7, 6),            # end cap
             (0, 4, 5), (0, 5, 1),
             (1, 5, 6), (1, 6, 2),
             (2, 6, 7), (2, 7, 3),
             (3, 7, 4), (3, 4, 0)]
    return verts, faces


def _member_mesh(a, b, sec: S.Section):
    """Every prism making up one member's cross-section, as one vertex soup."""
    ex, ey, ez = _axes(a, b)
    parts = []
    if sec.family == 'W':
        tf = sec.t or 0.3
        tw = {'W12X16': 0.220, 'W14X22': 0.230,
              'W8X24': 0.245, 'W6X8.5': 0.170}.get(sec.name, 0.25)
        bf, d = sec.b, sec.d
        parts.append((bf, tf, 0.0, (d - tf) / 2.0))      # top flange
        parts.append((bf, tf, 0.0, -(d - tf) / 2.0))     # bottom flange
        parts.append((tw, d - 2 * tf, 0.0, 0.0))         # web
    elif sec.family == 'tee':
        flange, stem = sec.t or 0.25, sec.b
        parts.append((sec.d, flange, 0.0, (stem - flange) / 2.0))
        parts.append((2 * flange, stem - flange, 0.0, -flange / 2.0))
    else:
        parts.append((sec.b, sec.d, 0.0, 0.0))

    verts, faces = [], []
    for w, h, oy, oz in parts:
        v, f = _box(a, b, ey, ez, max(w, 0.2), max(h, 0.2), oy, oz)
        base = len(verts)
        verts += v
        faces += [(i + base, j + base, k + base) for i, j, k in f]
    return verts, faces


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------

#: Of the four colourings ``viewer.MODES`` defines, this view offers two. The
#: other two -- what to do with a member, and what happens without it -- speak
#: to the cost-reduction study rather than to the room, and the owner uses this
#: page to lay the room out.
SOLID_MODES = ('utilisation', 'governing', 'connection')
CONNECTION_MODE = ('connection', 'What are the moment frames?',
                   'Red: designated moment-frame beams and columns. Green: '
                   'braced-frame members. Blue: simple/pinned framing. Amber: '
                   'the solver transfers moment, but no lateral role is assigned.')

#: The plot div's id, so the checkboxes below it can find the graph.
PLOT_ID = 'frameplot'


def _header_html(summary: dict) -> str:
    """The page title, as HTML above the controls rather than inside the plot."""
    live = summary['basis']['loft_live'][summary['live_case']]
    return f"""
<div id="viewhead">
  <h1>Garage frame &mdash; members at true section size</h1>
  <p>{summary['frame_model']} &middot; every member extruded as its actual
  cross-section, in inches &middot; loft live {live:.0f} psf &middot; wind
  {summary['basis']['wind']['V']:.0f} mph Exposure {summary['exposure']}<br>
  Existing garage shown ghosted; the roof is red where a new member passes
  through it</p>
</div>
<style>
  #viewhead {{ font: 13px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI",
               Helvetica, Arial, sans-serif; padding-top: 4px; }}
  #viewhead h1 {{ font-size: 16px; margin: 0 0 4px; color: #22262b; }}
  #viewhead p {{ margin: 0; font-size: 12px; color: #5c6672; }}
  @media (prefers-color-scheme: dark) {{
    #viewhead h1 {{ color: #e8eaec; }}
    #viewhead p {{ color: #9aa3ab; }}
  }}
</style>
"""


def _controls_html(n_traces: int, n_frame: int, wall_i, roof_i,
                   stage, extra_range) -> str:
    """A row of real checkboxes that drive trace visibility.

    These were Plotly ``updatemenus`` buttons with ``args``/``args2``, which is
    a toggle that remembers nothing: each button wrote a whole ``visible`` list,
    so pressing a second one undid the first, and the camera presets wrote a
    camera into the same call and left the scene somewhere the other buttons
    could not recover from. Checkboxes hold their own state, and one function
    recomputes visibility for every trace from all of them together, so they
    compose in any order and nothing is ever left stranded.

    The room-layout checkbox uses one elevated plan camera so the new ground
    floor and wall equipment are legible. Its previous camera is restored when
    the layout is turned off; all other controls leave the camera alone.
    """
    groups = dict(n=n_traces, frame=n_frame,
                  wall=wall_i, roof=roof_i,
                  stage=list(stage) if stage else None,
                  extra=list(extra_range) if extra_range else None)
    boxes = []
    if wall_i is not None:
        boxes.append(('walls', 'Hide existing walls', False))
        # Ticked by default: the existing roof sits between the new floor and
        # the new roof, so leaving it on hides most of what the page is for.
        boxes.append(('roof', 'Hide existing roof', True))
        boxes.append(('frame', 'Hide new frame', False))
    if stage:
        boxes.append(('stage', 'Pre-demo frame', False))
    if extra_range:
        boxes.append(('extra', 'Cabinet layout', False))
    if not boxes:
        return ''
    items = ''.join(
        f'<label class="cbx"><input type="checkbox" id="cb_{key}"'
        f'{" checked" if on else ""} onchange="'
        f'{"toggleStage()" if key == "stage" else "toggleExtra()" if key == "extra" else "applyVis()"}"> {label}</label>'
        for key, label, on in boxes)
    stage_hint = (f'<span class="phasehint"><b>Pre-demo frame</b> shows the '
                  f'members that can be erected before the existing roof is removed.</span>'
                  if stage else '')
    return f"""
<div id="viewbar">{items}
  {stage_hint}
  <span class="hint">Cabinet layout puts in the loft deck, the first-floor
  built-ins, laundry console and workbenches, the new ground-floor plan and infill walls, both electrical
  panels, the concrete shed equipment, and everything stored on the loft; tick
  <b>Hide existing roof</b> with it to see down into the loft.</span>
</div>
<style>
  #viewbar {{ font: 13px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI",
              Helvetica, Arial, sans-serif; color: #22262b;
              display: flex; flex-wrap: wrap; align-items: center; gap: 4px 18px;
              padding: 10px 0 12px; }}
  #viewbar .cbx {{ display: inline-flex; align-items: center; gap: 6px;
                   cursor: pointer; user-select: none; white-space: nowrap; }}
  #viewbar input {{ width: 15px; height: 15px; cursor: pointer; margin: 0; }}
  #viewbar .hint {{ color: #5c6672; font-size: 12px; flex: 1 1 260px;
                    min-width: 220px; }}
  #viewbar .phasehint {{ color: #5c6672; font-size: 12px; flex: 1 1 260px;
                         min-width: 220px; }}
  @media (prefers-color-scheme: dark) {{
    #viewbar {{ color: #e8eaec; }}
    #viewbar .hint, #viewbar .phasehint {{ color: #9aa3ab; }}
  }}
</style>
<script>
  var VIS = {json.dumps(groups)};
  var roomCamera = null;
  function toggleExtra() {{
    var gd = document.getElementById('{PLOT_ID}');
    var extra = document.getElementById('cb_extra');
    if (!gd || !extra || typeof Plotly === 'undefined') return;
    if (extra.checked) {{
      roomCamera = JSON.parse(JSON.stringify(gd._fullLayout.scene.camera));
      applyVis();
      Plotly.relayout(gd, {{'scene.camera': {{
        eye: {{x: -0.9, y: -1.35, z: 2.0}},
        up: {{x: 0, y: 0, z: 1}}, center: {{x: 0, y: 0, z: -0.08}}
      }}}});
    }} else {{
      applyVis();
      if (roomCamera) Plotly.relayout(gd, {{'scene.camera': roomCamera}});
      roomCamera = null;
    }}
  }}
  function toggleStage() {{
    var stage = document.getElementById('cb_stage');
    if (stage && stage.checked) {{
      // The roof is the reference that explains the phase. Put it back when
      // this view is selected, and remove room-layout overlays from the way.
      var roof = document.getElementById('cb_roof');
      var extra = document.getElementById('cb_extra');
      if (roof) roof.checked = false;
      if (extra) extra.checked = false;
    }}
    applyVis();
  }}
  function applyVis() {{
    var gd = document.getElementById('{PLOT_ID}');
    if (!gd || !gd.data || typeof Plotly === 'undefined') return;
    var on = function (k) {{
      var el = document.getElementById('cb_' + k);
      return el ? el.checked : false;
    }};
    var vis = new Array(VIS.n).fill(true);
    // Order matters only in that hiding wins: a trace hidden by any rule stays
    // hidden. Everything is recomputed from scratch on every change.
    if (VIS.stage && on('stage')) {{
      for (var i = 0; i < VIS.stage.length && i < VIS.n; i++) {{
        if (!VIS.stage[i]) vis[i] = false;
      }}
    }}
    if (on('frame')) {{
      for (var i = 0; i < VIS.frame; i++) vis[i] = false;
    }}
    if (VIS.wall && on('walls')) {{
      for (var w = 0; w < VIS.wall.length; w++) vis[VIS.wall[w]] = false;
    }}
    if (VIS.roof !== null && on('roof')) vis[VIS.roof] = false;
    if (VIS.extra) {{
      var show = on('extra');
      for (var i = VIS.extra[0]; i < VIS.extra[1]; i++) vis[i] = show;
    }}
    var idx = [];
    for (var i = 0; i < VIS.n; i++) idx.push(i);
    Plotly.restyle(gd, {{visible: vis}}, idx);
  }}
  document.addEventListener('DOMContentLoaded', applyVis);
  if (document.readyState !== 'loading') setTimeout(applyVis, 0);
</script>
"""


def write(frame: framemod.Frame, result, categories: dict, down: dict,
          removal: list, summary: dict, path: Path,
          show_existing: bool = True, before_demo: set | None = None,
          lean_to: dict | None = None, plan_png: Path | None = None,
          cabinets: bool = True, report_html: str | None = None,
          proposed_seats: list | None = None) -> None:
    verdicts = {r.member: r for r in removal}
    proposals = down.get('sections', {}) if down.get('verified') else {}
    removed = set(summary['removal'].get('cumulative', {}).get('removed', []))

    before_demo = before_demo or set()
    stage_visible: list = []
    traces, colors = [], {k: [] for k, _, _ in viewer.MODES + [CONNECTION_MODE]}
    for member in sorted(frame.members):
        segs = framemod._ordered(frame, [(i, j) for m, i, j in frame.segments
                                         if m == member])
        if not segs:
            continue
        a, b = frame.xyz(segs[0][0]), frame.xyz(segs[-1][1])
        sec = proposals.get(member, frame.section_of[member])
        m = result.members.get(member)
        v = verdicts.get(member)
        dcr = m.dcr if m else 0.0

        colors['utilisation'].append(visualize.util_color(dcr))
        colors['action'].append(visualize.CATEGORY[categories.get(member, 'keep')][0])
        colors['removal'].append(
            visualize.VERDICT_COLOR.get(v.verdict, '#c4cad1') if v else '#c4cad1')
        colors['governing'].append(
            viewer.GOVERN_COLOR.get(viewer._governing_family(m.combo), '#c4cad1')
            if m else '#c4cad1')
        connection_class = MF.classify(frame, member)
        colors['connection'].append(MF.COLORS[connection_class])

        verts, faces = _member_mesh(a, b, sec)
        verts = [[round(c, 2) for c in v] for v in verts]
        hover = '<br>'.join(filter(None, [
            f'<b>{member}</b>',
            f'{frame.group(member)} · <b>{sec.name}</b>'
            + (f' (was {frame.section_of[member].name})'
               if sec.name != frame.section_of[member].name else ''),
            f'{sec.b:g} × {sec.d:g} in. · {sec.weight:.1f} lb/ft',
            f'{frame.member_length(member):.1f} in. long · '
            f'{frame.member_weight(member):.0f} lb',
            f'<b>DCR {dcr:.2f}</b> — {m.mode}' if m else None,
            f'governed by {m.combo}' if m else None,
            f'unbraced {m.Lb:.0f} in · KL/r {m.slenderness:.0f}' if m else None,
            f'removal: <b>{v.verdict}</b> — {v.detail}' if v else None,
            '<b>REMOVED in the recommended package</b>' if member in removed else None,
            f'connection role: <b>{connection_class}</b>',
        ]))
        stage_visible.append(True if not before_demo or member in before_demo
                             else False)
        traces.append(go.Mesh3d(
            x=[p[0] for p in verts], y=[p[1] for p in verts], z=[p[2] for p in verts],
            i=[f[0] for f in faces], j=[f[1] for f in faces], k=[f[2] for f in faces],
            color=colors['utilisation'][-1], opacity=1.0, flatshading=True,
            lighting=dict(ambient=0.62, diffuse=0.85, specular=0.12, roughness=0.9),
            lightposition=dict(x=-8000, y=-12000, z=16000),
            name=member, hovertemplate=hover + '<extra></extra>', showlegend=False))

    sup = [frame.xyz(n) for n in frame.supports]
    traces.append(go.Scatter3d(
        x=[p[0] for p in sup], y=[p[1] for p in sup], z=[p[2] for p in sup],
        mode='markers', marker=dict(size=6, color='#22262b', symbol='square'),
        name='supports', hovertemplate='pinned base<extra></extra>', showlegend=False))
    for key in colors:                 # keep the colour lists aligned with the traces
        colors[key].append(None)
    stage_visible.append(True)

    # The east lean-to is drawn but is not part of this analysis: it spans the
    # existing wall to BE.upper and is checked on its own, so it appears in its
    # own colour and says so on hover.
    WOOD = '#b08a54'
    if lean_to and lean_to.get('geometry'):
        d = lean_to.get('rafter_depth', 9.25)
        sec = S.sawn_lumber('2x10 DF-L No.2', 1.5, d)
        pieces = [(a, b, 'rafter') for a, b in lean_to['geometry']]
        if lean_to.get('ledger'):
            pieces.append((*lean_to['ledger'], 'ledger'))
        for k, (a, b, kind) in enumerate(pieces):
            verts, faces = _member_mesh(a, b, sec)
            verts = [[round(c, 2) for c in v] for v in verts]
            traces.append(go.Mesh3d(
                x=[p[0] for p in verts], y=[p[1] for p in verts],
                z=[p[2] for p in verts],
                i=[f[0] for f in faces], j=[f[1] for f in faces],
                k=[f[2] for f in faces],
                color=WOOD, opacity=0.95, flatshading=True,
                lighting=dict(ambient=0.62, diffuse=0.85, specular=0.1, roughness=0.9),
                name=f'east lean-to {kind} {k + 1}',
                hovertemplate=f'<b>East lean-to {kind}</b><br>{sec.name}<br>'
                              f'bears on the existing east wall top<br>'
                              f'<i>after the demolition -- the old roof sits on '
                              f'that wall top</i><br>'
                              f'<i>analysed separately; not part of the steel '
                              f'frame model</i><extra></extra>',
                showlegend=False))
            for key in colors:
                colors[key].append(WOOD)
            # Not in the pre-demolition stage. Every piece of the lean-to bears
            # on the existing east wall top -- the rafters on it and the ledger
            # along it -- and that is precisely where the old roof's own rafters
            # and wall plate still are. The lean-to goes on after the demolition,
            # not before it.
            stage_visible.append(False)

    # Neutral connection envelopes: geometry only, never assigned a passing DCR.
    for seat in proposed_seats or []:
        a,b=seat['a'],seat['b']
        _,ey,ez=_axes(a,b)
        verts,faces=_box(a,b,ey,ez,seat['width'],seat['depth'])
        traces.append(go.Mesh3d(
            x=[p[0] for p in verts],y=[p[1] for p in verts],z=[p[2] for p in verts],
            i=[v[0] for v in faces],j=[v[1] for v in faces],k=[v[2] for v in faces],
            color='#87919d',name=seat['name'],flatshading=True,showlegend=False,
            hovertemplate='<b>'+seat['name']+'</b><br>Proposed seat envelope only; plates, bolts and welds not sized.<extra></extra>'))
        for key in colors:colors[key].append('#87919d')
        stage_visible.append(True)

    n_frame = len(traces)                      # frame meshes + the support markers
    wall_i = roof_i = None
    if show_existing:
        wv, wf = EX.wall_mesh()
        traces.append(go.Mesh3d(
            x=[v[0] for v in wv], y=[v[1] for v in wv], z=[v[2] for v in wv],
            i=[f[0] for f in wf], j=[f[1] for f in wf], k=[f[2] for f in wf],
            color=EX.GREY, opacity=0.28, flatshading=True, hoverinfo='skip',
            name='existing walls', showlegend=False))
        # The doors and windows recorded in the existing-conditions model are
        # cut out of the wall above; each gets a thin leaf here so the opening
        # reads as a door or a window rather than as a hole in the ghost.
        ov, of_ = EX.opening_mesh()
        traces.append(go.Mesh3d(
            x=[v[0] for v in ov], y=[v[1] for v in ov], z=[v[2] for v in ov],
            i=[f[0] for f in of_], j=[f[1] for f in of_], k=[f[2] for f in of_],
            color=EX.GLASS, opacity=0.38, flatshading=True,
            hovertemplate='existing door / window<extra></extra>',
            name='existing openings', showlegend=False))
        rv, rf, rc, clashing, frac = EX.roof_mesh(frame)
        traces.append(go.Mesh3d(
            x=[v[0] for v in rv], y=[v[1] for v in rv], z=[v[2] for v in rv],
            i=[f[0] for f in rf], j=[f[1] for f in rf], k=[f[2] for f in rf],
            facecolor=rc, opacity=0.42, flatshading=True,
            hovertemplate='existing roof<extra></extra>',
            name='existing roof', showlegend=False))
        wall_i, roof_i = [n_frame, n_frame + 1], n_frame + 2
        summary.setdefault('existing', {}).update(
            clashing_members=clashing,
            roof_area_disturbed_pct=round(100.0 * frac, 1))

    # The storage cabinets, the deck they stand on and the east wall behind
    # them. Hidden until asked for: one button puts the floor and the wall in,
    # takes the existing roof off, and shows the five units with their numbers.
    cabinet_rows: list = []
    extra_range = None
    if cabinets:
        import cabinets as CB
        cab_traces, cabinet_rows = CB.item_traces(frame)
        walk_traces, walk_rows = CB.walkway_traces(frame)
        extra_traces = (CB.floor_traces(frame) + CB.ground_floor_layout_traces(frame)
                        + CB.first_floor_cabinet_traces(frame)
                        + CB.laundry_console_traces(frame)
                        + CB.bench_traces(frame)
                        + CB.east_wall_traces(frame) + CB.new_wall_traces(frame)
                        + CB.shed_traces(frame) + walk_traces + cab_traces)
        first = len(traces)
        traces += extra_traces
        extra_range = (first, len(traces))
        summary['cabinets'] = cabinet_rows

    # Restyling 'color' with a null resets that trace to Plotly's default, so
    # every trace past the members carries its own colour into each mode.
    def own_color(t):
        return getattr(t, 'color', None)
    buttons = [dict(label=title, method='restyle',
                    args=[{'color': [c if c is not None else own_color(t)
                                     for c, t in zip(colors[key], traces)]
                           + [own_color(t) for t in traces[len(colors[key]):]]}],
                    args2=None)
               for key, title, _ in viewer.MODES + [CONNECTION_MODE]
               if key in SOLID_MODES]

    fig = go.Figure(traces)
    fig.update_layout(
        template='plotly_white',
        scene=dict(aspectmode='data',
                   xaxis=dict(title='east (in)', backgroundcolor='#fafbfc'),
                   yaxis=dict(title='north (in)', backgroundcolor='#fafbfc'),
                   zaxis=dict(title='up (in)', backgroundcolor='#fafbfc'),
                   camera=dict(eye=dict(x=-1.6, y=-1.45, z=0.75))),
        margin=dict(l=0, r=0, t=62, b=0),
        updatemenus=[dict(type='buttons', direction='right', showactive=True,
                          x=0.0, xanchor='left', y=1.02, yanchor='bottom',
                          bgcolor='#ffffff', bordercolor='#d6d9dd', borderwidth=1,
                          font=dict(size=11), pad=dict(l=6, r=6, t=4, b=4),
                          buttons=buttons)],
        hoverlabel=dict(bgcolor='white', font_size=11, align='left'))

    # Plotly is embedded, not pulled from a CDN. This file gets opened from
    # disk, from a file-preview sandbox and from the published site, and the
    # first two block the external script: Plotly never defines itself, the
    # scene never draws, and the checkbox handler throws. Inlining costs about
    # 3.5 MB and removes the dependency entirely.
    html = fig.to_html(include_plotlyjs=True, full_html=True, div_id=PLOT_ID,
                       config=dict(displaylogo=False,
                                   modeBarButtonsToRemove=['select2d', 'lasso2d']))
    # The title used to be a Plotly layout title, which put it inside the plot
    # div and therefore below the checkbox bar. It is plain HTML now, so the
    # page reads title, controls, model.
    html = html.replace(f'<div id="{PLOT_ID}"',
                        _header_html(summary)
                        + _controls_html(len(traces), n_frame, wall_i, roof_i,
                                         stage_visible if before_demo else None,
                                         extra_range)
                        + f'<div id="{PLOT_ID}"', 1)
    extra = report_html if report_html is not None else viewer._legend_html(summary)
    if cabinet_rows:
        import cabinets as CB
        extra += (CB.legend_html(cabinet_rows) + CB.first_floor_cabinets_html()
                  + CB.laundry_console_html(frame)
                  + CB.benches_html(frame)
                  + CB.new_walls_html(frame)
                  + CB.shed_html(frame)
                  + CB.walkway_html(walk_rows)
                  + CB.loads_html(frame, cabinet_rows))
    if plan_png and Path(plan_png).exists():
        b64 = base64.b64encode(Path(plan_png).read_bytes()).decode()
        extra += f'''
<div class="notes">
  <button id="planbtn" onclick="var p=document.getElementById('planwrap');
      var open = p.style.display !== 'block';
      p.style.display = open ? 'block' : 'none';
      this.textContent = open ? 'Hide the plan drawing'
                              : 'Show the plan drawing — every member named and dimensioned';
      if (open) p.scrollIntoView({{behavior:'smooth', block:'start'}});">
    Show the plan drawing — every member named and dimensioned
  </button>
  <div id="planwrap" style="display:none">
    <img src="data:image/png;base64,{b64}" alt="Frame plan">
    <p class="cap">Plan drawn from the same frame as the model above. Open the
    image in a new tab to zoom.</p>
  </div>
</div>
<style>
  #planbtn {{ font: 500 13.5px/1.4 inherit; color: #22262b; background: #f3f5f7;
              border: 1px solid #d6d9dd; border-radius: 8px; padding: 9px 14px;
              cursor: pointer; }}
  #planbtn:hover {{ background: #e9edf0; }}
  #planwrap img {{ width: 100%; height: auto; margin-top: 14px;
                   border: 1px solid #e4e7ea; border-radius: 8px; }}
  #planwrap .cap {{ font-size: 12px; color: #5c6672; margin: 8px 0 0; }}
  @media (prefers-color-scheme: dark) {{
    #planbtn {{ background: #1d2125; color: #e8eaec; border-color: #2c3136; }}
    #planbtn:hover {{ background: #262b30; }}
    #planwrap img {{ border-color: #2c3136; background: white; }}
  }}
</style>'''
    html = html.replace('</body>', extra + '</body>')
    html = html.replace('<head>', '<head>\n<meta name="viewport" '
                        'content="width=device-width, initial-scale=1">')
    path.write_text(html)
