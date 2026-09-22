# ChatGPT map asset workspace (ISOLATED / WIP)

Owner: ChatGPT. Tracking: issue #232. Branch: `chatgpt/map-assets-isolated-20260922`.

## Non-interference contract

1. **Never write to `main`, Claude's branches, `game/`, `reference_sim/`, `docs/`, `CLAUDE.md`, or `PROJECT_MEMORY.md`.** Claude-owned sources are read-only references.
2. All commits by this effort go exclusively to `chatgpt/map-assets-isolated-20260922`, with changed paths exclusively under `chatgpt_map_assets/`. Never merge, deploy, or edit game resource paths without a separate explicit request.
3. Never overwrite existing PNGs. Preserve the input filename, SHA-256, and crop rectangle in a LOCAL/private manifest for any extracted tile. Do not publish opaque conversation file IDs to this public repo. Existing homes of the same category can be registered as variants and are never discarded automatically.
4. Generated sheets, raw clips, and illustrative contact sheets are **not** implementation-ready assets. Accept each sprite only after individual PNG inspection, verified footprint, alignment and adjacency tests. Do not claim fidelity to the original game where source comparison is unavailable.
5. No guessed town tile pixel size: `tile_px` remains null until verified against town-map renderer code and source evidence. Indoor subtile dimensions are not a proxy for the town map.

## Structure and status

- `source_inventory.json`: a partial, non-sensitive index of conversation-generated sheet **filenames** and categories. These references are NOT source image bytes. If required, recover the exact original image locally and keep private file identifiers outside Git.
- `tools/extract_crops.py`: Pillow-based offline extraction of explicit, reviewed source-pixel rectangles to new, independent PNGs in a designated **disjoint** folder. Rejects output collisions and writes hash/size provenance. No automatic upscaling or background removal.
- `crop_plan.example.json`: schema with **no invented crop rectangles**. Actual crop coordinates require examining exact source pixels and human/visual validation.
- `tile_acceptance.md`: acceptance gates; no source sheets or enlarged low-resolution images count as completed sprites.

**Current state: partial source indexing and an unexecuted extraction tool only. No independent sprite extraction or map adjacency test has passed.** Original generated images and Claude's game sources are unchanged by these commits.

Execution: retrieve exact source PNGs into a local read-only folder, create reviewed crop coordinates in a private crop plan, run the extractor with a new, separate output directory, inspect/validate each output before promoting it to production assets. Never modify source images in-place.