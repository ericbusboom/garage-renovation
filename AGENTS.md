# Project agent guidance

Work from the organized project areas: `report/`, `studies/`, `data/`, `viz/`, `render/`, `plans/`, `src/`, `public/`, and `archive/`. Read any more specific `AGENTS.md` before changing files below it; in particular, `report/AGENTS.md` controls the report.

Keep the repository checked in during substantial work. At coherent, tested checkpoints, review the staged changes, make a descriptive commit, and push the current branch to its configured remote unless the user has asked to keep the work local. Do this periodically during long tasks and once more when the requested work is complete. Never commit credentials, local virtual environments, caches, nested repository metadata, or unrelated machine state.

`public/` is the deployable static site for `garage.busboom.org`. Keep links relative, include `public/CNAME`, and verify the site locally before publishing changes. Generated structural visualizations belong in `viz/`; only copy a reviewed public-facing artifact into `public/` intentionally.
