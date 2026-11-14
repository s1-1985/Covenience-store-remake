# Issue #232 — isolated individual cross-type PNG candidates (2026-11-14)

These **12 actual independent PNG files** are byte-identical Git-blob copies of the existing `main:assets/raw/conveni_map_assets_v2/terrain/tiles_64/` assets. They are placed only under `chatgpt_map_assets/individual_cross_type_2026-11-14/` on the ChatGPT-isolated branch. No rescaling, cropping, or image-generation has been applied.

Each original source SHA was checked against the live GitHub directory listing before this commit. The actual PNG bytes were read via the GitHub file API; all 12 passed PNG signature, IHDR (64x64, 8-bit RGBA), every PNG chunk CRC, and IEND/trailing-data validation. This **does not** prove zlib/pixel decoding, seam quality, PS1 fidelity, or Godot rendering.

See `manifest.json` for per-file source IDs, exact Git Blob SHAs, source paths, and outstanding acceptance checks. These are **candidate-only**, not production-approved. The previously identified crossing topology and pond-channel direction concerns remain unresolved. No production game files were changed.
