"""Reads the customer tables out of the PS program (SLPS_007.82) and writes
them into game/data/vertical_slice.json as `ps1_program_tables` (task #130).

Every number comes from the program's own data (CONFIRMED_BINARY, see
docs/research/ps1-executable-formulas-2026-09-26.md); the addresses are
listed next to each table below. What this project decides on top of them
(REMAKE_BALANCED_DEFAULT) is in the block's evidence_note.

    python3 tools/ps1/extract_program_tables.py
"""
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "assets" / "raw" / "ps1_disc_analysis_v1" / "files" / "SLPS_007.82"
CONFIG = ROOT / "game" / "data" / "vertical_slice.json"

# The program's product order (msg 71-96) as this project's catalog ids.
PRODUCTS = [
    "cold_drink", "hot_drink", "alcohol", "bento", "bread", "instant_food", "snacks", "books", "tobacco",
    "ice_cream", "stationery", "electronics", "vegetables", "fish", "meat", "retort_food", "seasoning",
    "frozen_food", "oden", "daily_goods", "copy_paper", "parcel_delivery_form", "medicine", "underwear",
    "event_goods", "chinese_steamed_bun",
]
ARRIVALS = ["徒歩", "自転車", "バイク", "自動車"]
STAT_KEYS = [
    "shopping_importance", "price_sensitivity", "distance_sensitivity", "service_sensitivity", "stamina",
    "quickness", "manners", "focus", "weekday_share", "holiday_share",
]
# A visit row's look (msg 315-352) as this project's customer types
# (guide_customer_types.types). By name; ベビーカーの女性 has no type of its
# own in the guide's 21 and is filed under 子供連れのおばさん, as the guide's
# rows for the same visits are (REMAKE_BALANCED_DEFAULT).
SPRITE_TYPES = (
    ["female_college_student"] * 3 + ["college_student"] * 3 + ["salaryman"] * 4 + ["ol"] * 4
    + ["middle_aged_man"] * 2 + ["boy_middle_school_student", "boy_high_school_student",
    "girl_middle_school_student", "girl_high_school_student", "boy_elementary_student",
    "girl_elementary_student", "boy_kindergartner", "girl_kindergartner"] + ["elderly_man"] * 2
    + ["elderly_woman"] * 2 + ["middle_aged_woman"] * 4 + ["man_with_child", "woman_carrying_infant",
    "woman_with_child", "woman_with_child", "man_in_wheelchair", "man_on_crutches"]
)
# This project's town buildings (guide_town_map.building_catalog) as the
# program's building types (0x8009DA10, 56 bytes each). By name and size;
# the guide's A/B/C variants follow the program's records of the same name
# in order.
BUILDING_TYPES = {
    "police_box_building": 5, "fire_station_building": 6, "station_small": 7, "village_office": 9,
    "prefectural_office": 10, "metropolitan_government_office": 11, "kindergarten_building": 12,
    "elementary_school_building": 13, "middle_school_building": 14, "high_school_building": 15,
    "university_building": 16, "vocational_school_building": 17, "amusement_park_building": 18,
    "aquarium_building": 19, "zoo_building": 20, "large_park_building": 22, "game_center": 23,
    "company_small_a": 25, "company_small_b": 26, "company_small_c": 27, "company_large_a": 28,
    "house_small_a": 30, "house_small_b": 31, "house_small_c": 32, "house_medium_a": 34,
    "house_medium_b": 35, "house_large_c": 36, "gym_building": 38, "athletic_field_building": 39,
    "pool_building": 40, "event_hall_building": 41, "fast_food_a": 46, "fast_food_b": 47,
    "ramen_shop": 48, "soba_shop": 49, "izakaya_a": 50, "izakaya_b": 51, "izakaya_c": 52,
    "bookstore": 53, "toy_store": 54, "clothing_store": 55, "electronics_store": 56,
}
SEASONS = {0: "", 1: "summer", 2: "winter"}


def build_block(config):
    exe = EXE.read_bytes()

    def at(ram, size):
        start = ram - 0x80010000 + 0x800
        return exe[start:start + size]

    rows = []
    for index in range(144):
        raw = at(0x800A09D0 + 24 * index, 24)
        sprite, start, stay, money = struct.unpack("<4h", raw[:8])
        row = {
            "type": SPRITE_TYPES[sprite],
            "sprite_index": sprite,
            "start_hour": start,
            "start_minute": start * 60,
            "duration_minutes": stay,
            "budget_yen": money,
            "primary": PRODUCTS[raw[8]],
            "extras": [PRODUCTS[p] for p in raw[9:12] if p != 255],
            "arrival": ARRIVALS[raw[12]],
        }
        row.update(dict(zip(STAT_KEYS, struct.unpack("<10b", raw[13:23]))))
        rows.append(row)

    types = {}
    used_mixes = set()
    for catalog_id, type_index in BUILDING_TYPES.items():
        raw = at(0x8009DA10 + 56 * type_index, 56)
        width, height = struct.unpack("<2i", raw[24:32])
        mixes = list(struct.unpack("<5h", raw[42:52]))
        used_mixes.update(mixes)
        types[catalog_id] = {
            "program_type": type_index,
            "program_name": raw[:24].split(b"\0")[0].decode("shift_jis"),
            "size": [width, height],
            "mix_candidates": mixes,
        }
    mixes = []
    for mix_id in range(max(used_mixes) + 1):
        values = struct.unpack("<10h", at(0x8009FF1C + 20 * mix_id, 20))
        # Mix 136 (電気屋) also names row 144, one past the table's end
        # (the program would read whatever follows it); left out.
        mixes.append([
            [values[2 * k], values[2 * k + 1]] for k in range(5)
            if 0 <= values[2 * k] < len(rows) and values[2 * k + 1] > 0
        ])

    def hour_table(holiday):
        return [list(at(0x800A1BF4 + holiday * 576 + hour * 24, 24)) for hour in range(24)]

    holidays = [list(at(0x80099D84 + 4 * month, 4)) for month in range(1, 13)]
    thresholds = [list(struct.unpack("<4i", at(0x800994B0 + 16 * month, 16))) for month in range(12)]
    reach = list(struct.unpack("<4i", at(0x80099570, 16)))
    max_customers = list(struct.unpack("<6i", at(0x80099DB8, 24)))
    seasons = {}
    for index, product in enumerate(PRODUCTS):
        season = SEASONS[struct.unpack("<i", at(0x8009CE0C + 88 * index + 0x38, 4))[0]]
        if season:
            seasons[product] = season

    # The staff candidates (CONFIRMED_BINARY): DAT/TOWN0001.BIN after the
    # 17-byte header and the 60x50 town (8 bytes a square) holds 35 records of
    # 54 bytes (the same in all four towns). +2 name (msg 150+), +3 age, +4
    # female, +9 hourly wage (u16); +21.. the program's staff bytes +0x10..:
    # 体力 max/now, 教育, 機敏さ, 社交性, 学歴, then レジ/補充/接客/清掃/警備 and
    # their growth ceilings in the same order. The hire screen shows 体力, 学歴
    # (+0x15), 機敏さ, 社交性 (0x800703E4); the staff screen 教育 (+0x12) with
    # the five skills (0x8004A494).
    names = {int(line[:3]): line[4:].strip() for line in (ROOT / "assets" / "raw" / "ps1_disc_analysis_v1" / "text" / "MSG00.txt").read_text(encoding="utf-8").splitlines() if line[:3].isdigit()}
    by_name = {c["display_name"]: c["candidate_id"] for c in config["staff_candidates"]}
    # The guide transcription's two misread names (docs/research/ps1-disc-
    # analysis-crosscheck-2026-09-26.md).
    by_name["浜田裕子"] = by_name["浜田夕子"]
    by_name["杉村真智子"] = by_name["杉村真知子"]
    town = (ROOT / "assets" / "raw" / "ps1_disc_analysis_v1" / "files" / "DAT" / "TOWN0001.BIN").read_bytes()
    staff = {}
    for index in range(35):
        raw = town[17 + 24000 + 54 * index:17 + 24000 + 54 * (index + 1)]
        v = list(raw[21:37])
        name = names[150 + raw[2]]
        staff[by_name[name]] = {
            "display_name": name, "age_years": raw[3], "salary_yen_per_day_24h": (raw[9] | raw[10] << 8) * 24,
            "stamina": v[0], "education": v[2], "agility": v[3], "sociability": v[4], "academic_background": v[5],
            "register_skill": v[6], "replenishment_skill": v[7], "service_skill": v[8], "cleaning_skill": v[9],
            "security_skill": v[10], "register_skill_growth_ceiling": v[11],
            "replenishment_skill_growth_ceiling": v[12], "service_skill_growth_ceiling": v[13],
            "cleaning_skill_growth_ceiling": v[14], "security_skill_growth_ceiling": v[15],
        }

    block = {
        "evidence_note": (
            "Task #130, CONFIRMED_BINARY (PS program SLPS_007.82, docs/research/ps1-executable-formulas-"
            "2026-09-26.md): the 144 visit rows (0x800A09D0), the customer mixes each town square carries "
            "(0x8009FF1C: visit row and head count), each building type's five candidate mixes (0x8009DA10), "
            "which visit rows may come at each hour on a weekday and on a holiday (0x800A1BF4, [hour][row "
            "start hour]), the holidays (0x80099D84, month x day of 4), the weather thresholds (0x800994B0, "
            "the same as weather.monthly_percentages), how far each arrival reaches (0x80099570), the most "
            "customer groups inside by store size (0x80099DB8) and the summer/winter goods (0x8009CE0C+0x38). "
            "REMAKE_BALANCED_DEFAULT: the program's squares each carry one of their building type's five "
            "candidate mixes (drawn when the map is made); this project's town (drawn from the guide's map) "
            "picks it from the square's position; ベビーカーの女性 rows count as 子供連れのおばさん; a "
            "rival store takes its hours, 人気 and サービス from its guide_data (CONFIRMED_OFFICIAL) or, "
            "for one opened during the game, the guide's rival figures below, sells at the list price, has "
            "every category it may sell (tobacco, alcohol and medicine only with the permit) and no parking; "
            "a group of n takes n units of an item only when the shelf still holds n; mix 136's pair for row 144 "
            "(past the table's end) is left out. Task #133, CONFIRMED_BINARY: the staff candidates' figures (DAT/TOWN0001.BIN) "
            "including 教育 (the staff screen's, not on the guide's cards), and staff growth (0x8003AA58): a "
            "task raises a skill by 1 with a chance of the manager's 学歴 out of 100, never past the staff "
            "member's own 教育/社交性/機敏さ, and past the skill's growth ceiling only 1 time in 16."
        ),
        "visit_rows": rows,
        "customer_mixes": mixes,
        "building_types": types,
        "visit_hours": {"weekday": hour_table(0), "holiday": hour_table(1)},
        "holidays": holidays,
        "weather_thresholds": thresholds,
        "weather_value_bands": [[0, 0], [1, 19], [20, 39], [40, 59], [60, 79]],
        "arrival_reach_squares": dict(zip(ARRIVALS, reach)),
        "closeness_squares": [0, 110],
        "product_seasons": seasons,
        "max_customer_groups": {"small": max_customers[0], "medium": max_customers[2], "large": max_customers[4]},
        "spawn_every_game_minutes": 2,
        "spawn_chance_one_in": 4,
        "max_group_size": 5,
        "popularity_bonus": 20,
        "weather_importance_bonus": 20,
        "rival_store": {"price_percent": 100, "service": 30, "popularity": 20, "parking": 0, "hours": "AM7:00〜PM11:00"},
        "staff_candidates": staff,
        "staff_growth": {"skill_caps": {
            "register_skill": "education", "service_skill": "sociability", "replenishment_skill": "agility",
            "cleaning_skill": "sociability", "security_skill": "education",
        }, "over_ceiling_chance_one_in": 16, "cleaning_while_restocking_below": 100,
            "anger_decline_chance_one_in": 3, "anger_rating_chance_one_in": 10},
    }
    assert thresholds == [
        [sum(month[:k + 1]) for k in range(4)] for month in config["weather"]["monthly_percentages"]
    ], "the program's weather thresholds must match weather.monthly_percentages"
    return block


def main():
    text = CONFIG.read_text(encoding="utf-8")
    block = build_block(json.loads(text))
    rows = block["visit_rows"]
    start = text.find('\n  "ps1_program_tables": ')
    if start >= 0:
        # Cut out only this block: up to the next top-level key, or the
        # closing brace when it is the last one.
        following = re.search(r'\n  "[^"]+": ', text[start + 1:])
        if following is None:
            text = text[:start].rstrip().rstrip(",") + "\n}\n"
        else:
            text = text[:start] + text[start + 1 + following.start():]
    body = json.dumps(block, ensure_ascii=False, indent=2)
    # Lists of plain numbers on one line.
    body = re.sub(r"\[[\s\d,.-]*\]", lambda m: "[" + ", ".join(m.group(0)[1:-1].split()).replace(",,", ",") + "]", body)
    body = "\n".join("  " + line for line in body.splitlines()).lstrip()
    head = text.rstrip()
    assert head.endswith("}")
    text = head[:-1].rstrip() + ',\n  "ps1_program_tables": ' + body + "\n}\n"
    assert json.loads(text)["ps1_program_tables"] == json.loads(json.dumps(block))
    CONFIG.write_text(text, encoding="utf-8")
    print("visit rows %d, mixes %d, building types %d" % (
        len(rows), len(block["customer_mixes"]), len(block["building_types"])))


if __name__ == "__main__":
    main()
