# Concept drawing set

This study assembles the current structural frame and equipment layout into one
large-format, multipage PDF for coordination and discussion. It is explicitly a
concept set, not a permit, fabrication, or construction package.

The sheets include:

- isometric, north, east, and south structural views;
- loft and ground-floor equipment plans;
- conceptual electrical distribution;
- conceptual Ethernet home runs; and
- conceptual dust collection and compressed-air distribution.

Regenerate from the repository root with:

```sh
archive/.venv/bin/python src/structural-analysis-v6/drawing_set.py \
  studies/20260924.02-concept-drawing-set/garage-concept-drawing-set.pdf
```

The MEP routes record proposed endpoints and zones. Final circuiting, conductor,
cable, pipe and duct sizing, clearances, supports, and code compliance remain to
be designed and verified.
