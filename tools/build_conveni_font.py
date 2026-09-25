"""Rebuild game/fonts/ConveniJP.ttf, the bundled Noto Sans JP subset.

The bundled font only contains the glyphs the game actually displays, so any
new Japanese UI/data text needs this rerun or it renders as missing glyphs.

Source font (SIL OFL, not committed): Noto Sans JP variable font from
google/fonts, e.g.
  https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf

Usage:
  pip install fonttools
  python tools/build_conveni_font.py /path/to/NotoSansJP[wght].ttf
"""

from __future__ import annotations

import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "game" / "fonts" / "ConveniJP.ttf"
TEXT_SOURCES = (
    [REPO_ROOT / "game" / "locale" / "ja.po", REPO_ROOT / "game" / "data" / "vertical_slice.json"]
    + sorted((REPO_ROOT / "game" / "scripts").rglob("*.gd"))
    + sorted((REPO_ROOT / "game" / "scenes").glob("*.tscn"))
)
BASE_RANGES = (
    range(0x0020, 0x007F),  # ASCII
    range(0x3000, 0x3040),  # CJK symbols and punctuation
    range(0x3040, 0x30A0),  # hiragana
    range(0x30A0, 0x3100),  # katakana
    range(0xFF00, 0xFFF0),  # half-/full-width forms
)


def wanted_codepoints() -> set[int]:
    codepoints = {cp for block in BASE_RANGES for cp in block}
    if OUTPUT.exists():
        # Never drop a glyph an earlier build already shipped.
        codepoints |= set(TTFont(OUTPUT).getBestCmap())
    for path in TEXT_SOURCES:
        codepoints |= {ord(ch) for ch in path.read_text(encoding="utf-8") if ord(ch) >= 0x20}
    return codepoints


def main(source_path: str) -> None:
    font = TTFont(source_path)
    font = instancer.instantiateVariableFont(font, {"wght": 400})
    available = set(font.getBestCmap())
    codepoints = wanted_codepoints() & available
    # Default options keep only the common layout features (ccmp/liga/locl/
    # vert/vrt2), matching the original build; "*" would pull in every
    # jp78/jp83/aalt variant glyph and grow the file ~60%.
    subsetter = subset.Subsetter(subset.Options())
    subsetter.populate(unicodes=sorted(codepoints))
    subsetter.subset(font)
    font.save(OUTPUT)
    print(f"wrote {OUTPUT} with {len(font.getBestCmap())} codepoints")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
