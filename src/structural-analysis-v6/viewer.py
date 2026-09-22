"""Interactive 3-D model of the result.

One self-contained HTML file.  Every member is a line in the model, coloured by
whichever question is being asked -- how hard it is working, what governs it,
whether it can go, whether it can be lighter -- and every member carries its own
schedule row in the hover text, so the drawing and the numbers are the same
object rather than two documents to reconcile.
"""
from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go

import frame as framemod
import visualize

MODES = [
    ('utilisation', 'How hard it is working',
     'Demand divided by capacity under the governing combination. '
     'Red is at or over the code limit; blue is barely stressed.'),
    ('action', 'What to do with it',
     'The verified recommendation: enlarge, keep, lighten, or delete.'),
    ('removal', 'What happens without it',
     'Red members leave a mechanism when deleted. Grey members overload '
     'something else. Green members can go.'),
    ('governing', 'What governs it',
     'Which family of load combinations produces the worst case: gravity, '
     'wind or seismic.'),
]

GOVERN_COLOR = {'gravity': '#4c9f70', 'wind': '#3a6ea5', 'seismic': '#e07a3f',
                'service': '#8a63a8'}


def _governing_family(combo: str) -> str:
    if combo.startswith('S'):
        return 'service'
    if '[W' in combo:
        return 'wind'
    if '[E' in combo:
        return 'seismic'
    return 'gravity'


def write(frame: framemod.Frame, result, categories: dict, down: dict,
          removal: list, summary: dict, path: Path) -> None:
    verdicts = {r.member: r for r in removal}
    proposals = down.get('sections', {}) if down.get('verified') else {}
    removed = set(summary['removal'].get('cumulative', {}).get('removed', []))

    names, traces = [], []
    colors: dict[str, list[str]] = {k: [] for k, _, _ in MODES}
    widths: list[float] = []

    for member in sorted(frame.members):
        pts = visualize.member_polyline(frame, member)
        if not pts:
            continue
        m = result.members.get(member)
        sec = frame.section_of[member]
        v = verdicts.get(member)
        p = proposals.get(member)
        dcr = m.dcr if m else 0.0

        names.append(member)
        colors['utilisation'].append(visualize.util_color(dcr))
        colors['action'].append(visualize.CATEGORY[categories.get(member, 'keep')][0])
        colors['removal'].append(
            visualize.VERDICT_COLOR.get(v.verdict, '#c4cad1') if v else '#c4cad1')
        colors['governing'].append(
            GOVERN_COLOR.get(_governing_family(m.combo), '#c4cad1') if m else '#c4cad1')
        widths.append(2.0 + 5.0 * min(max(sec.b, sec.d), 8.0) / 8.0)

        hover = '<br>'.join(filter(None, [
            f'<b>{member}</b>',
            f'{frame.group(member)} · {sec.name}'
            + (f' <i>({sec.note})</i>' if sec.note else ''),
            f'{frame.member_length(member):.1f} in long · '
            f'{frame.member_weight(member):.0f} lb',
            f'<b>DCR {dcr:.2f}</b> — {m.mode}' if m else None,
            f'governed by {m.combo}' if m else None,
            f'unbraced {m.Lb:.0f} in · KL/r {m.slenderness:.0f}' if m else None,
            f'axial {m.P:,.0f} lb · moment {m.Mz:,.0f} lb-in' if m else None,
            f'⚠ {"; ".join(m.flags)}' if m and m.flags else None,
            f'removal: <b>{v.verdict}</b> — {v.detail}' if v else None,
            f'proposed: <b>{p.name}</b> (saves '
            f'{frame.member_weight(member) * (1 - p.weight / sec.weight):.0f} lb)'
            if p else None,
            '<b>deleted in the combined proposal</b>' if member in removed else None,
        ]))

        traces.append(go.Scatter3d(
            x=[q[0] for q in pts], y=[q[1] for q in pts], z=[q[2] for q in pts],
            mode='lines',
            line=dict(color=colors['utilisation'][-1], width=widths[-1]),
            name=member, hovertemplate=hover + '<extra></extra>',
            showlegend=False))

    sup = [frame.xyz(n) for n in frame.supports]
    traces.append(go.Scatter3d(
        x=[p[0] for p in sup], y=[p[1] for p in sup], z=[p[2] for p in sup],
        mode='markers', marker=dict(size=5, color='#22262b', symbol='square'),
        name='supports', hovertemplate='pinned base<extra></extra>',
        showlegend=False))

    buttons = [dict(label=title, method='restyle',
                    args=[{'line.color': colors[key] + [None]}])
               for key, title, _ in MODES]

    fig = go.Figure(traces)
    fig.update_layout(
        template='plotly_white',
        scene=dict(aspectmode='data',
                   xaxis=dict(title='east (in)', backgroundcolor='#fafbfc'),
                   yaxis=dict(title='north (in)', backgroundcolor='#fafbfc'),
                   zaxis=dict(title='up (in)', backgroundcolor='#fafbfc'),
                   camera=dict(eye=dict(x=-1.7, y=-1.5, z=0.9))),
        margin=dict(l=0, r=0, t=168, b=0),
        updatemenus=[dict(type='buttons', direction='right', showactive=True,
                          x=0.0, xanchor='left', y=1.015, yanchor='bottom',
                          bgcolor='#ffffff', bordercolor='#d6d9dd', borderwidth=1,
                          font=dict(size=11), pad=dict(l=6, r=6, t=4, b=4),
                          buttons=buttons)],
        title=dict(text=f'<b>Garage frame — structural analysis</b><br>'
                        f'<span style="font-size:12px;color:#5c6672">'
                        f'{summary["frame_model"]} · {summary["software"].split("(")[0]}· '
                        f'loft live {summary["basis"]["loft_live"][summary["live_case"]]:.0f} psf'
                        f' · wind {summary["basis"]["wind"]["V"]:.0f} mph Exposure '
                        f'{summary["exposure"]}</span>',
                   x=0.0, xanchor='left', y=0.965, yanchor='top',
                   font=dict(size=17)),
        hoverlabel=dict(bgcolor='white', font_size=11, align='left'))

    legend = _legend_html(summary)
    html = fig.to_html(include_plotlyjs=True, full_html=True,
                       config=dict(displaylogo=False,
                                   modeBarButtonsToRemove=['select2d', 'lasso2d']))
    html = html.replace('</body>', legend + '</body>')
    html = html.replace('<head>', '<head>\n<meta name="viewport" '
                        'content="width=device-width, initial-scale=1">')
    path.write_text(html)


def _legend_html(summary: dict) -> str:
    cats = ''.join(
        f'<li><span style="background:{c}"></span>{lab}</li>'
        for c, lab in visualize.CATEGORY.values())
    t = summary['totals']
    cum = summary['removal'].get('cumulative', {})
    return f"""
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
          Arial, sans-serif; margin: 0; background: #ffffff; color: #22262b; }}
  .notes {{ max-width: 1040px; margin: 8px auto 40px; padding: 0 20px;
            font-size: 13.5px; line-height: 1.65; }}
  .notes h2 {{ font-size: 15px; margin: 26px 0 8px; letter-spacing: .01em; }}
  .notes ul {{ list-style: none; padding: 0; margin: 0; }}
  .notes li {{ margin: 5px 0; }}
  .notes li span {{ display: inline-block; width: 26px; height: 10px;
                    border-radius: 2px; margin-right: 10px;
                    vertical-align: middle; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px,1fr));
           gap: 14px; margin: 12px 0 0; }}
  .card {{ border: 1px solid #e4e7ea; border-radius: 8px; padding: 12px 14px; }}
  .card b {{ display: block; font-size: 21px; font-weight: 600; }}
  .card small {{ color: #5c6672; font-size: 12px; }}
  .warn {{ border-left: 3px solid #c1292e; padding: 8px 14px; background: #fdf6f6;
           border-radius: 0 6px 6px 0; margin-top: 14px; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #14171a; color: #e8eaec; }}
    .card {{ border-color: #2c3136; }}
    .warn {{ background: #241a1b; }}
    .card small, .notes li {{ color: inherit; }}
  }}
</style>
<div class="notes">
  <div class="grid">
    <div class="card"><b>{t['baseline_lb']:,.0f} lb</b>
      <small>completed frame, members only</small></div>
    <div class="card"><b>{t['saved_lb']:,.0f} lb</b>
      <small>removable, {t['saved_pct']:.0f}% of the frame</small></div>
    <div class="card"><b>{len(cum.get('removed', []))}</b>
      <small>members deleted together and re-verified</small></div>
    <div class="card"><b>{len(summary['sizing'].get('lighter') or [])}</b>
      <small>sections verified one or more sizes lighter</small></div>
  </div>
  <h2>Colours in “what to do with it”</h2>
  <ul>{cats}</ul>
  <div class="warn"><b>This is an engineering study, not a construction
  document.</b> Connections, base plates, anchorage and foundations are not
  designed or checked. Section sizes for members the geometry model records only
  as a “concept envelope” are assumed at the lightest standard wall. Nothing here
  may be built from until a California-licensed structural engineer has reviewed,
  signed and sealed the design.</div>
</div>
"""
