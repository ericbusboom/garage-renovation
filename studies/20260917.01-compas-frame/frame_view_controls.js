// Camera and display controls operate on one embedded COMPAS-derived scene.
function initializeFrameReview() {
  const plot = document.getElementById('frame-plot');
  const config = window.frameReview;
  const copy = value => JSON.parse(JSON.stringify(value));
  const home = {eye:{x:-1.35,y:-1.43,z:.87},center:{x:0,y:0,z:0},up:{x:0,y:0,z:1},projection:{type:'perspective'}};
  const views = {
    north:{eye:{x:0,y:1.15,z:0},label:'North elevation',direction:'Looking south · East ← → West'},
    south:{eye:{x:0,y:-1.15,z:0},label:'South elevation',direction:'Looking north · West ← → East'},
    east:{eye:{x:1.15,y:0,z:0},label:'East elevation',direction:'Looking west · South ← → North'},
    west:{eye:{x:-1.15,y:0,z:0},label:'West elevation',direction:'Looking east · North ← → South'},
    top:{eye:{x:0,y:0,z:1.35},label:'Top view',direction:'North ↑ · East →'}
  };
  let view = '3d', theme = 'cream', savedCamera = copy(home), updating = false;
  let queue = Promise.resolve();
  function run(action) {
    queue = queue.then(async () => { updating = true; try { await action(); } finally { updating = false; } })
      .catch(error => { document.getElementById('view-hint').textContent = 'Could not update the view. Please reload.'; console.error(error); });
  }
  function pressed(selector, key, value) {
    document.querySelectorAll(selector).forEach(button => button.setAttribute('aria-pressed',String(button.dataset[key] === value)));
  }
  async function setView(next, reset = false) {
    view = next;
    if (next === '3d' && reset) savedCamera = copy(home);
    const scale = next === 'top' ? 1.7 : 1.9;
    const camera = next === '3d' ? copy(reset ? home : savedCamera) : {
      eye:views[next].eye,center:{x:0,y:0,z:0},up:next === 'top' ? {x:0,y:1,z:0} : {x:0,y:0,z:1},projection:{type:'orthographic'}
    };
    if (next === '3d') camera.up = {x:0,y:0,z:1};
    await Plotly.relayout(plot, {'scene.camera':camera,'scene.dragmode':next === '3d' ? 'turntable' : 'pan',
      'scene.aspectmode':next === '3d' ? 'data' : 'manual',
      'scene.aspectratio':{x:scale,y:scale*360/330,z:scale*270/330}});
    await setTheme(theme);
    pressed('[data-view]','view',next);
    document.getElementById('view-title').textContent = next === '3d' ? '3D frame' : views[next].label;
    document.getElementById('orientation').textContent = next === '3d' ? 'Turntable · Upright' : views[next].direction;
    document.getElementById('view-hint').textContent = next === '3d' ? 'Drag to turn · Scroll to zoom · Click a member' : 'Drag to pan · Scroll to zoom · Click a member';
  }
  const monoColors = {'Solar panels and clerestory':'#788b8d','Roof, fascia and soffits':'#bdbdb1','Existing garage':'#e3ddca','Wall cladding and infill':'#e3ddca','Floor and secondary context':'#d1c6ad','Loft joists':'#c8bda5'};
  async function setTheme(next) {
    theme = next;
    const indices = config.meshIndices;
    await Plotly.restyle(plot,{color:indices.map(i => view !== '3d' && view !== 'top' && document.getElementById('layers').value !== 'exterior' && !config.elevationFaces[i].includes(view) ? '#ecece4' : theme === 'colors' ? config.colors[i] : (monoColors[config.names[i]] || '#343631'))},indices);
    pressed('[data-theme]','theme',theme);
    document.getElementById('palette-key').hidden = theme !== 'colors';
  }
  async function setLayers() {
    const layer = document.getElementById('layers').value;
    document.getElementById('member-detail').textContent = layer === 'exterior' ? 'Roof and walls use the earlier envelope study.' : 'Select a member to identify it.';
    const ghost = document.getElementById('ghost').checked;
    const joints = document.getElementById('joints').checked;
    const visibility = config.names.map((name,i) => name === 'Shared joints' ? joints : name === config.ghostName ? ghost : config.presets[layer][i] === true);
    // The ghost replaces the solid existing shell when requested.
    config.names.forEach((name,i) => { if (name === 'Existing garage' && ghost) visibility[i] = false; });
    await Plotly.restyle(plot,{visible:visibility});
    await setTheme(theme);
  }
  plot.on('plotly_relayout', event => {
    if (!updating && view === '3d' && event['scene.camera']) {
      savedCamera = copy(event['scene.camera']);
      document.getElementById('orientation').textContent = 'Turntable · Upright';
    }
  });
  plot.on('plotly_click', event => {
    const point = event.points && event.points[0];
    if (point && point.text) document.getElementById('member-detail').textContent = point.text.replace(/<br\s*\/?>/g,' · ');
  });
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click',() => run(() => setView(button.dataset.view))));
  document.querySelectorAll('[data-theme]').forEach(button => button.addEventListener('click',() => run(() => setTheme(button.dataset.theme))));
  ['layers','ghost','joints'].forEach(id => document.getElementById(id).addEventListener('change',() => run(setLayers)));
  document.getElementById('fit-view').addEventListener('click',() => run(() => setView(view,true)));
  new ResizeObserver(() => Plotly.Plots.resize(plot)).observe(document.getElementById('model-canvas'));
  run(async () => { await setLayers(); await setTheme(theme); await setView(view); });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializeFrameReview, {once:true});
else initializeFrameReview();
