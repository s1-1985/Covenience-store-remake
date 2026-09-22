# Acceptance gates (not a generated gallery)

**Producer: ChatGPT; location: isolated `chatgpt_map_assets/` branch only.** Issue #232 is open until all mandatory gates pass.

## A. One sprite, one verified source

- Each accepted ID has its own lossless PNG, source-sheet filename + SHA-256, exact native-pixel crop rectangle, output SHA-256, and visual inspection log.
- Text labels, white sheet gutters and unrelated neighboring buildings are excluded by inspected crop boxes; eliminate stray colored pixels only after reviewing them.
- No enlarging a low-resolution sheet and claiming newly recovered detail. No global conversion of black/white to transparent: it could erase legitimate roof, road or water pixels.
- Keep existing residential image variants under independent IDs, without replacing or discarding earlier candidates.

## B. World/map geometry

- Confirm `town_tile_px` from **town map code**, not indoor display subtile size. Check both footprint axes independently: 3 rows x 2 columns must not turn into 2 x 3 or an arbitrary square.
- Every building's image includes the correct plot boundary; label/image proportions are not treated as footprint evidence. Buildings have a separate footprint metadata field taken from `_sg_building`.
- Confirm overhead orientation: no visible side facade, no isometric diamond, no tilted perspective. Reject incompatible candidate sheets rather than silently accepting them.
- Trees/grass/soil candidate variants should not embed hard fences, waterbanks, sidewalks or other edge-limited structures unless tagged as a transition tile.

## C. Seam/ports verification

- All road, railway, and river tiles must have declared N/E/S/W connection bits (N=1, E=2, S=4, W=8). Endpoints, straight, bends, T, and cross: every requested orientation must be represented.
- For each adjacent pair, the two facing edges must declare mutually consistent connectivity, use a common centerline/track gauge/river width, and have compatible pixels at the boundary. Pixel-edge comparison alone is not enough when grass variation is present: compare the connected object's edge location and expected ground/water mask as well.
- Road/rail crossings, road bridges, railway bridges, river mouths/lake inlets must be tested as multi-layer joins. Mark any unsupported topology as not implemented; do not substitute arbitrary scenery.
- Fixed-size test maps: a 3x3 cross and T junction; a 5x5 set of every bend; road across water; rail across water; rail across road; estuary/coast joins; building plot next to road. Save exact input tile IDs and rendered output for repeatability.

## D. Final deliverables

- Machine-readable manifest, independent PNG files, deterministic crop plan, covered-building-ID report (52 target building categories, 7 tile/infrastructure classes tracked separately), sample maps and test output; all under this isolated namespace, without changes to Claude's game, scripts, or resources.
- A check is checked only after files exist and the actual test was executed. A note or illustrative sheet cannot satisfy a gate.

## Current execution status

- Isolated branch, partial sheet index and non-destructive crop extraction source: created.
- Individual PNG crops, native source-image recoverability, verified map tile pixel size, seam tests and game draw tests: **not completed**. The working image-processing runtime timed out during this session, so no extraction/test pass is claimed.
