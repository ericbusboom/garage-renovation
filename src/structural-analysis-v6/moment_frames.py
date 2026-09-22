"""Explicit lateral-system classification for the current frame viewer.

The solver treats every unreleased member end as moment-continuous.  That is not
the same as designating a seismic/wind moment frame.  This registry makes the
distinction visible and deliberately leaves the upper roof/clerestory system
unassigned until a released-joint model verifies the final lateral scheme.
"""
from __future__ import annotations

COLORS = {
    'moment': '#c83e4d',
    'braced': '#6b8e23',
    'simple': '#377eb8',
    'unassigned': '#d89028',
}

# Two ground-to-floor longitudinal moment frames. These are the only current
# intentional moment frames; the names include both beams and their columns.
MOMENT_FRAMES = {
    'west longitudinal — BW line': {'BW', 'SW0', 'W1', 'W2', 'W3', 'W4'},
    'east longitudinal — BE line': {'BE', 'E-S2', 'E-S3', 'E-N2'},
}
MOMENT_MEMBERS = set().union(*MOMENT_FRAMES.values())

# Diagonal lateral members. Their physical intent should be a gusseted axial
# connection even where an older group label currently leaves a rigid end in
# the solver; the connection audit calls that mismatch out for reanalysis.
BRACED_MEMBERS = {
    'BR-N-1', 'BR-N-2', 'BR-NU-1', 'BR-S-1', 'BR-S-2', 'BR-W-2',
    'CT.diag.E', 'CT.diag.W', 'W.rear.brace',
}

# Members deliberately modeled as simple/pinned by group or explicit release.
EXPLICIT_SIMPLE_MEMBERS = {'BE.upper', 'DOOR-E', 'DOOR-W'}


def classify(frame, member: str) -> str:
    if member in MOMENT_MEMBERS:
        return 'moment'
    if member in BRACED_MEMBERS:
        return 'braced'
    if frame.group(member) in {'Joists', 'Rafters', 'Bracing'}:
        return 'simple'
    if member in EXPLICIT_SIMPLE_MEMBERS:
        return 'simple'
    # Amber means exactly what it says: the solver transfers moment here but
    # the member has not been assigned to a deliberate moment frame.
    return 'unassigned'


def audit(frame) -> dict:
    classes = {m: classify(frame, m) for m in frame.members}
    return {
        'classes': classes,
        'counts': {k: sum(v == k for v in classes.values()) for k in COLORS},
        'moment_frames': {k: sorted(v & set(frame.members))
                          for k, v in MOMENT_FRAMES.items()},
        'unassigned': sorted(m for m, v in classes.items() if v == 'unassigned'),
    }
