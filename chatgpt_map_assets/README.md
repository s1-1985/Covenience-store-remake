# ChatGPT map asset workspace (ISOLATED / WIP)

Owner: ChatGPT. Tracking: issue #232. Branch: `chatgpt/map-assets-isolated-20260922`.

## Non-interference contract

1. **Never write to `main`, Claude's branches, `game/`, `reference_sim/`, `docs/`, `CLAUDE.md`, or `PROJECT_MEMORY.md`.** Claude-owned sources are read-only references.
2. All commits by this effort go exclusively to `chatgpt/map-assets-isolated-20260922`, with changed paths exclusively under `chatgpt_map_assets/`. Never merge or open an automatically mergeable PR, deploy, or edit game resource paths.
3. Never overwrite existing PNGs. Preserve the input file ID, hash and crop rectangle for any extracted tile. Existing homes of the same category can be registered as variants, never discarded automatically.
4. Generated sheets, raw clips and illustrative contact sheets are **not** implementation-ready assets. A tile is accepted only after checking the independent PNG, documented footprint, alignment and adjacent-edge tests. Do not claim fidelity to source when reference is unverified.
5. No guessed town tile pixel size: keep `tile_px` unset until verified against map renderer code and game evidence. Indoor subtile dimensions are not a proxy for the town map.

## Structure and status

- `source_inventory.json`: a verifiable, partial index of conversation-generated sources, with original opaque file IDs. These are references only, **not** image blobs uploaded into Git. Missing original source bytes must be recovered before extraction.
- `tools/extract_crops.py`: optional Pillow-based **offline** extraction of explicit pixel rectangles into independent PNGs. Creates output in a designated separate directory; rejects collisions and records SHA-256 and dimensions. Explicit rectangles prevent the white margins/labels from being mistaken for in-game tiles.
- `crop_plan.example.json`: sample schema with no made-up bounding boxes. Each real crop rectangle needs inspection of the corresponding source and review before marking usable.
- `tile_acceptance.md`: criteria; no source sheets or guessed upscaled graphics count as passed.

**Current state: tooling and partial source index only; no individual PNG extraction or map adjacency test has passed.** The original generated images and game sources have not been modified.

To work with the images: retrieve the original conversation file by exact file ID, place it in a local READ-ONLY source directory, write reviewed bounding boxes into a crop plan, run the extractor with a separate output directory, and inspect/log results. No input files are rewritten.