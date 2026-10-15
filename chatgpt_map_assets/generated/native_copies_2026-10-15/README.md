# Native source PNG staging — 2026-10-15

This directory contains **16 real, independent PNG paths**, staged by reusing their existing immutable Git blob objects (no re-encoding, no scaling, no modification to original source paths). 6 road, 5 rail, 5 river. Original source blobs were checked via read-only GitHub fetch_file at `688876a4763c5dd006da8cfc36c7e7960d862e28`; all 16 Git blob SHA values matched.

These are **byte-identical native source copies**, NOT 29 rotated direction-specific outputs and NOT a claim of complete direction coverage or seamless edges. All visual/renderer acceptance flags remain false.

`manifest.json` records the source paths, original source image IDs, Git blob SHA, intended direction masks and isolated destination paths. The companion read-only script `chatgpt_map_assets/tools/verify_native_copies_2026_10_15.py` checks source/copy byte equality, Git blob SHA and PNG IHDR.

The task #232 checklist remains unchanged. No source files, main, Claude branches or pre-existing paths were modified.
