"""Run Godot regressions and the actual recovered-app paths; Godot 4.3 required."""
from pathlib import Path
import os, subprocess, sys
root = Path(__file__).resolve().parents[1]
godot = str(Path(sys.argv[1]).resolve())
for script, args in [
    ('headless_smoke.gd', []),
    ('source_geometry_smoke.gd', []),
    ('source_people_smoke.gd', []),
    ('source_notifications_smoke.gd', []),
    ('source_notifications_ui_smoke.gd', ['--', '--android-preview']),
    ('source_progression_smoke.gd', []),
    ('source_ending_ui_smoke.gd', ['--', '--android-preview']),
    ('operating_statement_smoke.gd', []),
    ('android_preview_smoke.gd', ['--', '--android-preview']),
    ('recovered_runtime_smoke.gd', []),
    ('recovered_game_smoke.gd', []),
    ('recovered_ui_smoke.gd', ['--', '--android-preview']),
    ('source_interior_smoke.gd', []),
    ('analysis_integration_smoke.gd', []),
    ('source_operations_smoke.gd', []),
    ('source_operations_ui_smoke.gd', ['--', '--android-preview']),
]:
    result = subprocess.run([godot, '--headless', '--quit-after', '600', '--path', str(root / 'game'), '--script', 'res://scripts/' + script, *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    output = result.stdout
    completed = any(marker in output.lower() for marker in ('passed', '_pass ', 'failures: 0'))
    success = result.returncode == 0 and 'ERROR:' not in output and completed
    print(script, 'PASS' if success else 'FAIL', flush=True)
    print(output.strip(), flush=True)
    if not success:
        raise SystemExit(1)
