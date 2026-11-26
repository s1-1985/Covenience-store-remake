"""Turns the PS1 disc's MSG00.OBJ / STAFF.OBJ records (already split into
glyph codes by the ChatGPT disc analysis, assets/raw/ps1_disc_analysis_v1/
*-messages.json) into text, using the PSMOJI0/1 glyph table in psmoji.py.

Control codes (0x4000 and up) are kept as {XXXX}: 0x4002 is a line break,
0x4003/0x4004/0x4009/0x400A/0x400C insert a number, a name or stars at run
time (inference from where they appear, not decoded from the program).

    python3 tools/ps1/decode_message_text.py
writes assets/raw/ps1_disc_analysis_v1/text/MSG00.txt and STAFF.txt.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import psmoji  # noqa: E402

ROOT = Path(__file__).resolve().parents[2] / "assets" / "raw" / "ps1_disc_analysis_v1"


def main():
    out_dir = ROOT / "text"
    out_dir.mkdir(exist_ok=True)
    for name in ("MSG00", "STAFF"):
        records = json.loads((ROOT / (name + "-messages.json")).read_text(encoding="utf-8"))
        lines = ["%3d %s" % (record["id"], psmoji.decode(record["codes"])) for record in records]
        (out_dir / (name + ".txt")).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("%s: %d records" % (name, len(lines)))


if __name__ == "__main__":
    main()
