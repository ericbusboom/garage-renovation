# sandbox

Scratch COMPAS work. Not authoritative, not versioned, never read by a build script.

Try things here freely — name files whatever you want. The naming rule and the
resolver in `../README.md` apply to the parent directory only.

Two things to keep true:

- Nothing outside `sandbox/` may read a file in `sandbox/`.
- When scratch work becomes real, regenerate it through its build script so it
  gets a proper `frame-<YYYYMMDD>.<NN>-<description>.compas.json` version in the
  parent directory. Don't promote it by renaming.
