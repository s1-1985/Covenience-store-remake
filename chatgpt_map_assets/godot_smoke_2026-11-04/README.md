# Issue #232: isolated Godot 4 render smoke test (2026-11-04)

This is a **new, self-contained test project**, not a patch to the game. It reads the existing 45-candidate registry, its 3 topology fixtures, and all 45 source PNGs from a local checkout of branch \`chatgpt/map-assets-isolated-20260922\`. It never changes the input files, \`main\`, Claude branches, or the game's renderer.

## Run

From any shell with Godot 4 installed, using a local checkout of the isolated branch:

\`\`\`sh
godot --headless --path "/absolute/path/to/repo/chatgpt_map_assets/godot_smoke_2026-11-04" \
  --script res://smoke.gd -- \
  --repo-root "/absolute/path/to/repo" --output-name output_first_run
\`\`\`

The script checks all 45 IDs, 15 direction masks per kind, PNG loading and 64×64 dimensions, and the 3×24-tile reciprocal-edge fixtures. It then uses **Godot SubViewport + Sprite2D + nearest-neighbor 64→24px scaling** to render separate 120×120 PNGs for road, rail and river. The report and PNGs are written to a **new** \`output_first_run/\` directory *under this test project*. Existing output directories cause a hard failure. Change the output name on every run.

The test project is nested inside the isolated directory; it uses an explicit \`--repo-root\` and read-only absolute PNG paths because \`res://\` cannot refer to parent directories. The script validates that the project directory corresponds to the requested checkout before creating output.

## Important limitations

- **NOT RUN on 2026-11-04**: Godot is not installed in the current execution environment. Do not claim a Godot PASS until someone runs it and reviews its generated \`report.json\` and PNGs.
- A successful smoke test means the candidate PNGs load and a real Godot viewport produces nonblank images. It **does not** prove seams, original-game fidelity, building correctness, bridge behavior, integration into \`game/scripts/town_view.gd\`, or regression safety.
- The isolated registry is **candidate-only**. River-curve warp candidates from 2026-11-01 are not promoted. The test uses the unchanged 2026-10-30 registry.
- If running headless on a system without a usable rendering backend, rerun in a compatible Godot 4 environment; do not mark the issue complete based on a failed or blank viewport.
