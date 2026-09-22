# Garage Rebuild Report

This directory is the controlled project report for the proposed garage rebuild at **1370 Wilbur Avenue, San Diego, California 92109**. It is the place where the current design, verified existing conditions, engineering basis, approvals, and issued deliverables are assembled for review by the owner, architect, engineers, builder, fabricators, and permitting authorities.

The workspace outside this directory is separated by purpose: active studies, data, visualizations, renders, source code, approved plans, and retained archive material. Nothing becomes part of the controlled report merely because it exists elsewhere in the project.

## Start here

1. Read [00-report-index.md](00-report-index.md) for the document set and current status.
2. Read [00-project-controls/document-requirements.md](00-project-controls/document-requirements.md) for the required content and acceptance criteria.
3. Check [document-manifest.csv](document-manifest.csv) before adding or relying on a document.
4. Review [00-project-controls/decision-log.md](00-project-controls/decision-log.md), [00-project-controls/assumptions-register.md](00-project-controls/assumptions-register.md), and [00-project-controls/open-items.md](00-project-controls/open-items.md).
5. Use [source-map.md](source-map.md) to locate relevant working files outside this report.

## What belongs here

A file belongs in `report/` when it does at least one of the following:

- defines the currently selected design or a design criterion;
- records a verified site or existing-building condition;
- supports a code, zoning, permit, geotechnical, structural, energy, or cost conclusion;
- is a coordinated drawing, specification, calculation, schedule, or model intended for review or issue;
- records an approval, formal review response, inspection, test, submittal, warranty, or as-built condition.

Raw photos, temporary renders, exploratory calculations, software environments, logs, and abandoned options stay in their working directories. A concise comparison of alternatives may be included when it explains a decision.

## Document states

Every controlled document has one state in `document-manifest.csv`:

| State | Meaning |
|---|---|
| `planned` | Required or useful, but not yet drafted. |
| `draft` | Work in progress; not suitable for construction or permitting. |
| `reviewed` | Coordinated internally, with unresolved items disclosed. |
| `verified` | Facts or calculations checked against an identified authoritative source. |
| `issued` | Released for a named purpose and frozen at that revision. |
| `superseded` | Retained for traceability but replaced by a later document. |

“Final,” “approved,” “engineered,” and “as-built” are not informal labels. Use them only when the manifest identifies who approved or verified the document, the date, and the purpose of issue.

## Promotion rules

Before copying a working artifact into this report:

1. Confirm that it represents the selected design or necessary evidence.
2. Give it a document ID and manifest entry.
3. Record its working source, revision date, author or generator, and review status.
4. State its assumptions, units, orientation, coordinate origin, and intended use where applicable.
5. Check that related plans, elevations, sections, schedules, calculations, and models agree.
6. Export a durable review format such as PDF, PDF/A, STEP, IFC, CSV, or a lossless image. Keep the editable native file when it is needed for future work.
7. Add it to the master index only after it can be opened and its contents have been checked.

Issued professional reports and stamped drawings are immutable. Add a new revision rather than editing them. Preserve digital signatures and seals.

## File naming and revisions

- Use a stable descriptive name, lower-case words, and hyphens: `existing-condition-survey.pdf`.
- Keep the current controlled copy at the path recorded in the manifest.
- Record revision, issue date, and status in the document itself and the manifest.
- Put obsolete controlled copies in a clearly marked `superseded/` folder within their section when retention is necessary.
- Do not use names such as `final-final`, `new`, `latest`, or unexplained version numbers.

## Facts, decisions, and assumptions

- **Verified fact:** tied to a survey, field measurement, permit record, code source, utility record, test, or signed professional report.
- **Owner-provided information:** useful project input that has not yet been independently verified; identify it as such.
- **Design decision:** an adopted choice with a date, decision maker, and affected documents.
- **Assumption:** a temporary input used to continue work; record its consequence and closure method.

Conflicts are recorded in the open-items register and resolved in the decision log. Do not silently choose between conflicting dimensions.

## Project conventions

- Address: 1370 Wilbur Avenue, San Diego, CA 92109.
- Orientation: north is the garage-door side unless a controlled survey establishes otherwise. Every plan must show a north arrow.
- Primary drawing units: feet and inches. Calculations may use consistent US customary units and must identify them.
- Structural calculations in this repository are preliminary unless signed and sealed by the responsible California-licensed engineer.
- Parcel boundaries, easements, setbacks, zoning, overlays, and utility locations remain unverified until documented in this report.

## Deliverables folder

`deliverables/` holds only coordinated, current issue packages. Native CAD files, exports, drawings, calculations, and specifications may be copied there when they form a reviewed package. The folder must never be used as an automatic build destination or scratch area.
