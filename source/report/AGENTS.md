# Instructions for agents working in `report/`

These instructions apply to this directory and all descendants.

## Required read order

Before editing the report, read:

1. `README.md`
2. `00-report-index.md`
3. `document-manifest.csv`
4. the decision, assumption, and open-item registers in `00-project-controls/`
5. the relevant section README and `source-map.md`

## Control rules

- Treat the report as a curated deliverable set, not a mirror of the workspace.
- Do not promote a concept as selected merely because it is the newest file by timestamp.
- Keep owner statements, verified facts, design decisions, and assumptions distinct.
- Do not assert parcel boundaries, zoning, overlays, setbacks, height limits, utility clearances, soil capacity, or structural adequacy without recording the supporting source.
- Do not call preliminary calculations construction-ready. Structural drawings and calculations require review and sealing by the responsible California-licensed design professional.
- Do not edit a signed, sealed, issued, or third-party report. Add a new revision or addendum.
- When adding, replacing, or superseding a controlled artifact, update the manifest, master index, and relevant register in the same change.
- Preserve source provenance. A generated PDF or image must identify its editable source or generating program in the manifest.
- Check that every added file opens and that dimensions and labels are legible.
- Use official City, State, utility, manufacturer, and professional sources for regulatory or technical requirements. Record the access date because requirements change.
- Do not duplicate raw photo libraries, caches, virtual environments, logs, or intermediate renders in this directory.
- Do not copy sensitive property or personal information into an external issue package unless it is needed for that issue.

## CAD and drawing rules

- Maintain a common coordinate system, orientation, datum, and unit convention across CAD models.
- Keep existing construction, proposed construction, demolition, and temporary works distinguishable and independently hideable.
- A drawing must show its title, document ID, revision, date, status, scale or “not to scale,” units, and north arrow where relevant.
- A model exported for exchange should include a neutral format such as STEP or IFC alongside the native editable file when practical.
- A render is explanatory evidence, not a dimensional drawing or structural calculation.

## Analysis rules

- State load cases, combinations, boundary conditions, material grades, section properties, connection assumptions, deflection limits, and software/version.
- Include equilibrium and reasonableness checks and disclose excluded behavior.
- Keep reproducible source data and code in the working analysis directory. Put the reviewed calculation package and its input summary in the report.
- Flag any result that depends on unknown foundations, existing-wall capacity, field dimensions, corrosion, weld quality, or connection stiffness.

## Status language

Use only the controlled states `planned`, `draft`, `reviewed`, `verified`, `issued`, and `superseded`. If evidence is incomplete, leave the item open rather than strengthening the wording.

