#!/bin/bash
# sync-to-repo.sh — copy source files from gala + buzzkill into the git repo
# Excludes: renders, backups, venvs, caches, generated meshes, logs
set -euo pipefail

REPO="${1:-/Volumes/Proj/garage-renovation}"
GALA="/Volumes/Proj/proj/CAD/garage"
BUZZKILL="buzzkill:/proj/garage"

echo "=== Syncing to $REPO ==="

RSYNC="rsync -a --delete"

# ── Common exclude patterns for rsync ────────────────────────────────────
EXCLUDES=(
  --exclude='*.png'
  --exclude='*.jpg'
  --exclude='*.gif'
  --exclude='*.bmp'
  --exclude='*.exr'
  --exclude='*.blend1'
  --exclude='*.blend2'
  --exclude='*.FCBak'
  --exclude='*.FCBak1'
  --exclude='*.bak'
  --exclude='__pycache__/'
  --exclude='*.pyc'
  --exclude='*.pyo'
  --exclude='.DS_Store'
  --exclude='._*'
  --exclude='*.zip'
  --exclude='*.tar.gz'
  --exclude='*.log'
  --exclude='*progress.txt'
  --exclude='*agent-result.json'
  --exclude='*-interactive.html'
  --exclude='ALL-interactive.html'
  --exclude='*complete.network.json'
  --exclude='*roof_first.network.json'
  --exclude='wiki-publish/'
)

# ── GALA: copy core project directories ──────────────────────────────────
GALA_DIRS=(
  optimization
  backyard-blender
  backyard-proposal
  existing-site
  model
  cabinet-study
  combined-study
  construction-sequence-study
  loading-door-study
  outbuilding-study
  roof-first-feasibility
  roof-studies
  structural-analysis-v2
  structural-analysis-v3
  structural-analysis-v4
  structural-analysis-v5
  structural-study
  workstation-setup
)

echo "--- Syncing from gala ($GALA) ---"
for d in "${GALA_DIRS[@]}"; do
  src="$GALA/$d"
  if [ -d "$src" ]; then
    echo "  $d"
    $RSYNC "${EXCLUDES[@]}" \
      --exclude='venv*/' --exclude='.venv*/' \
      --exclude='*-cad-mesh.json' --exclude='*-mesh.json' \
      --exclude='visible-mesh*.json' \
      --exclude='wiki-publish/' \
      --exclude='site-packages/' \
      --exclude='public/' \
      "$src/" "$REPO/source/$d/"
  fi
done

# Also copy the blender-render source scripts/structure (exclude renders/blends)
if [ -d "$GALA/blender-render" ]; then
  echo "  blender-render"
  mkdir -p "$REPO/source/blender-render"
  $RSYNC "${EXCLUDES[@]}" \
    --exclude='*.blend' \
    --exclude='*.gltf' \
    "$GALA/blender-render/" "$REPO/source/blender-render/"
fi

# ── BUZZKILL: copy top-level source files ────────────────────────────────
echo "--- Syncing top-level files from buzzkill ---"
mkdir -p "$REPO/buzzkill"

# Use rsync over SSH for Buzzkill top-level
scp buzzkill:/proj/garage/Existing-Garage.FCStd "$REPO/buzzkill/" 2>/dev/null || echo "  (Existing-Garage.FCStd skipped)"
scp buzzkill:/proj/garage/Existing-Garage.step "$REPO/buzzkill/" 2>/dev/null || echo "  (step skipped)"
scp buzzkill:/proj/garage/Proposed-Garage.FCStd "$REPO/buzzkill/" 2>/dev/null || echo "  (Proposed-Garage.FCStd skipped)"
scp buzzkill:/proj/garage/Proposed-Garage-overlay.step "$REPO/buzzkill/" 2>/dev/null || echo "  (overlay step skipped)"

# Buzzkill top-level scripts and data
rsync -a "${EXCLUDES[@]}" \
  --include='*.py' --include='*.json' --include='*.csv' --include='*.md' \
  --include='*.step' --include='*.pdf' --include='*.svg' --include='*.txt' \
  --exclude='*' \
  buzzkill:/proj/garage/ "$REPO/buzzkill/" 2>/dev/null || echo "  (buzzkill rsync partial — some files may not have transferred)"

# Also grab the READMEs
rsync -a --include='*.md' --exclude='*' buzzkill:/proj/garage/ "$REPO/buzzkill/" 2>/dev/null

echo "=== Sync complete ==="
echo "Repo size: $(du -sh "$REPO" | cut -f1)"
echo "File count: $(find "$REPO" -type f ! -path '*/.git/*' | wc -l)"