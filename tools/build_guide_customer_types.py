"""Writes vertical_slice.json's "guide_customer_types" block: the 21 customer types
and their 143 visit rows from the strategy guide's 顧客データ (book pages 134-143),
as already transcribed in reference_sim/conveni_sim/baseline_data.py
(CUSTOMER_ARCHETYPES, CUSTOMER_VISIT_SCHEDULE; CONFIRMED_OFFICIAL).

Each visit row: when the visit window starts and how long it lasts, how the
customer comes, the ten printed stats (ス スタミナ, 素 素早さ, マ マナー, 集 集中力,
買 買物重要度, 価 価格重視度, 距 距離重視度, サ サービス重視度, 平/休 平日/休日来店割合),
所持金, the product they come for and up to three more they may also buy.

The walking sprites customer_01..customer_21 are drawn one per type, in the
same order (assets/raw/customer_v2/customer/manifest.json name_ja).

The "rules" are how the game uses the rows; see docs/decisions/0190-customer-
types.md and the evidence_note below.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference_sim"))
from conveni_sim.baseline_data import CUSTOMER_ARCHETYPES, CUSTOMER_VISIT_SCHEDULE  # noqa: E402

CONFIG = ROOT / "game" / "data" / "vertical_slice.json"
MANIFEST = ROOT / "assets" / "raw" / "customer_v2" / "customer" / "manifest.json"
STAT_NAMES = [
    "stamina", "quickness", "manners", "focus", "shopping_importance",
    "price_sensitivity", "distance_sensitivity", "service_sensitivity",
    "weekday_share", "holiday_share",
]

RULES = {
    # One category from the customer's home building's DATA4 wanted list is
    # also a purpose of the visit, besides the type's own.
    "building_wants_per_visit": 1,
    # Add-on buying: after each item, the chance to go for one more is
    # add_on_base_chance x (100 - 集中力) / 100 x the fixture's 注目度, for the
    # row's listed extras, and impulse_weight of that for anything else on a
    # fixture within impulse_radius_subcells.
    "add_on_base_chance": 0.6,
    "impulse_weight": 0.3,
    "impulse_radius_subcells": 4,
    "max_add_ons": 3,
    # Price: a raise of P% makes a customer skip an item with chance
    # 価格重視度/100 x P/50; a cut of P% raises add-on chances by the same share.
    "price_skip_per_percent_at_full_sensitivity": 0.02,
    # 素早さ: time at a shelf x 100 / (50 + 素早さ).
    "quickness_offset": 50,
    # スタミナ: patience at the register x スタミナ / 70 (about the average),
    # kept between 0.25 and 1.5.
    "patience_reference_stamina": 70,
    "patience_min": 0.25,
    "patience_max": 1.5,
}

EVIDENCE_NOTE = (
    "Task #120. CONFIRMED_OFFICIAL (strategy guide 顧客データ, book pages 134-143, transcribed in "
    "reference_sim/conveni_sim/baseline_data.py): the 21 customer types, and per visit row the window, "
    "the ten stats, 所持金, the product the customer comes for and the others they may also buy. "
    "They agree with the first-title wiki's observations (docs/research/customer-purchase-role-"
    "merchandising-2026-09-05.md): oden, steamed buns, hot drinks, frozen food and seasonings are only "
    "ever extras, bento never is; and ス is lowest for おじいさん and おじさん, whom the guide (p.35) calls "
    "quickest to anger. The sprites customer_01..21 are the 21 types in this order. "
    "REMAKE_BALANCED_DEFAULT (how the game uses them; no formula is printed): which row a customer "
    "is (among the rows whose window holds the hour, in proportion to 平日来店割合, capped at 100 for "
    "the one misprinted 700); one wanted category of their building is also a purpose; 所持金 is a hard "
    "limit; the add-on chance add_on_base_chance x (100-集中力)/100 x 注目度, with impulse_weight for "
    "unlisted goods nearby; a price raise makes a price-sensitive customer skip items; 素早さ shortens "
    "the time at a shelf; ス scales the patience at the register. This client has no weekday/holiday "
    "calendar, so 休日来店割合 is kept but not used."
)


def sprite_for(name_ja, manifest):
    for sprite in manifest["sprites"]:
        if sprite["name_ja"] == name_ja:
            return sprite["id"]
    raise SystemExit("no sprite for " + name_ja)


def minutes(text):
    hours, mins = text.split(":")
    return int(hours) * 60 + int(mins)


def build():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    types = []
    for archetype in CUSTOMER_ARCHETYPES:
        types.append({
            "id": archetype.id,
            "name": archetype.display_name.value,
            "ages": archetype.visual_archetype.value,
            "sprite": sprite_for(archetype.display_name.value, manifest),
        })
    visits = []
    for row in CUSTOMER_VISIT_SCHEDULE:
        stats = dict(zip(STAT_NAMES, row.behavior_stats_raw.value))
        visits.append({
            "type": row.archetype_id,
            "start_minute": minutes(row.visit_start_time.value),
            "duration_minutes": row.visit_duration_minutes.value,
            "arrival": row.arrival_method.value,
            **stats,
            "budget_yen": row.budget_yen.value,
            "primary": row.primary_wanted_product.value if row.primary_wanted_product else "",
            "extras": list(row.secondary_wanted_products.value),
        })
    return {"evidence_note": EVIDENCE_NOTE, "rules": RULES, "types": types, "visits": visits}


def main():
    text = CONFIG.read_text(encoding="utf-8")
    block = build()
    start = text.find('\n  "guide_customer_types": ')
    if start != -1:
        following = re.search(r'\n  "[^"]+": ', text[start + 1:])
        if following is None:
            text = text[:start].rstrip().rstrip(",") + "\n}\n"
        else:
            text = text[:start] + text[start + 1 + following.start():]
    body = json.dumps(block, ensure_ascii=False, indent=2)
    # One visit row per line keeps the block readable next to the guide page.
    body = re.sub(r"\{\n\s+\"type\"(.*?)\n\s+\}", lambda m: "{\"type\"" + re.sub(r"\s*\n\s*", " ", m.group(1)) + "}", body, flags=re.S)
    body = "\n".join("  " + line for line in body.splitlines()).lstrip()
    head = text.rstrip()
    assert head.endswith("}")
    text = head[:-1].rstrip() + ',\n  "guide_customer_types": ' + body + "\n}\n"
    assert json.loads(text)["guide_customer_types"] == json.loads(json.dumps(block))
    CONFIG.write_text(text, encoding="utf-8")
    print("wrote %d types, %d visit rows" % (len(block["types"]), len(block["visits"])))


if __name__ == "__main__":
    sys.exit(main())
