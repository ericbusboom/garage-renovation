# Buzzkill remote agent workflow

Verified 2026-09-09. Apps: FreeCAD 1.1.3, ChatGPT desktop, Chrome.

- Worker task: `01a087ee-c294-7612-94f6-e48ce0a46601`, title `Check if system works`.
- App host ID: `remote-control:env_b_6aa1c32ca16c83239f4d49aa2acb8321`.
- Send work with app `send_message_to_thread`; wait with `wait_threads`.
- App reads currently report completed turns with empty items and no assistant text. Reverse messages cannot discover the Mac task. Cause unresolved.
- Worker executes locally and writes result JSON with a unique request ID, status, verified checks, errors, timestamp, and artifact paths.
- Fetch result files with SSH to `ros@buzzkill`; verify request ID and checks before accepting completion. This is a tested fallback, not an app fix.
- Worker protocol: `/home/ros/Documents/Codex/2026-09-09/oh/REMOTE-RESULTS.md`.
- Test result: `/home/ros/Documents/Codex/2026-09-09/oh/garage-agent-result.json`.

Verified round trip GARAGE-REMOTE-PROBE-002: remote FreeCAD created an in-memory 25.4 × 50.8 × 76.2 mm box; isValid true; volume 98,322.384 mm³, matching the dimensional product. No garage model changed.

Runtime: `/opt/freecad-1.1.3/AppRun python`; add `/opt/freecad-1.1.3/usr/lib` to Python sys.path to import FreeCAD and Part. GUI launcher: `/usr/local/bin/freecad`. CLI version: `/opt/freecad-1.1.3/AppRun freecadcmd --version`.
