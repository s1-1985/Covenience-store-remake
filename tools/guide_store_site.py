"""Task #95: the store-site rules of the guide town map (no numpy/Pillow, so
the contract test can import it). build_guide_town_map.py writes
store_site_rules() into guide_town_map.store_site; site_quote() is the Python
mirror of game/scripts/domain/store_site.gd, and the contract test checks
both give the same numbers.
"""

# Task #95: where the player may open a store and what the land costs.
# CONFIRMED_OFFICIAL / CONFIRMED_COMMUNITY anchors:
# - a convenience store takes 2x2 map squares (DATA4 コンビニ(自) 2×2, guide
#   p.92-95);
# - a new store's land cost = 地価(4エリア分) + 建物評価額÷2 (guide third book
#   p.79; p.7 "買収費~建物評価額の50%");
# - no store within 5 squares of another store (guide p.7 ring diagram,
#   店建設可能 5; TownSpatial.STORE_CONSTRUCTION_MIN_DISTANCE_TILES);
# - start-of-game vacant lots cost 20,000,000 (rail side, map centre),
#   25,000,000 (near a school, facing a main road), 26,000,000 and 30,000,000
#   yen (guide p.6-8 screenshots; 20,000,000 is also the wiki's minimum).
# REMAKE_BALANCED_DEFAULT: the shape that turns a site into a price -- the
# 20,000,000 floor, +5,000,000 when the site touches a road (the guide's
# 大通り example minus the floor), up to +5,000,000 more for how built-up the
# surrounding 16x16 squares are (so a vacant lot tops out at the guide's
# highest vacant example, 30,000,000), rounded to the million like every
# guide example -- and the customer catchment below are this project's own.
STORE_SITE_FOOTPRINT = (2, 2)
STORE_SITE_LAND_AREA_COUNT = 4
STORE_SITE_MIN_STORE_DISTANCE = 5
STORE_SITE_FLOOR_PRICE_YEN = 20_000_000
STORE_SITE_ROAD_BONUS_YEN = 5_000_000
STORE_SITE_DENSITY_BONUS_YEN = 5_000_000
STORE_SITE_PRICE_STEP_YEN = 1_000_000
# The guide's 16x16-square zone around a store (security facilities, PDF3
# p.10): 7 squares out from the 2x2 store on every side. Used here, by
# analogy, as the area whose buildings send customers to the store.
STORE_SITE_CATCHMENT_TILES = 7
STORE_SITE_UNBUILDABLE = ("R", "T")
# DATA4 prints building prices as bare numbers (住宅(小A) 1000). PROVISIONAL:
# read as 万円, the only unit under which the guide's own example of a lot
# with a house (34,000,000) comes out next to its vacant ones (26-30,000,000).
BUILDING_PRICE_UNIT_YEN = 10_000


def building_tiles(buildings):
    """Map square -> index of the building standing on it."""
    tiles = {}
    for index, building in enumerate(buildings):
        x0, y0 = building["tile"]
        w, h = building["size"]
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                tiles[(x, y)] = index
    return tiles


def site_footprint(origin):
    return [
        (origin[0] + dx, origin[1] + dy)
        for dy in range(STORE_SITE_FOOTPRINT[1])
        for dx in range(STORE_SITE_FOOTPRINT[0])
    ]


def site_is_buildable(rows, origin):
    height, width = len(rows), len(rows[0])
    for x, y in site_footprint(origin):
        if not (0 <= x < width and 0 <= y < height) or rows[y][x] in STORE_SITE_UNBUILDABLE:
            return False
    return True


def site_faces_road(rows, origin):
    height, width = len(rows), len(rows[0])
    for x, y in site_footprint(origin):
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and rows[ny][nx] == "R":
                return True
    return False


def catchment_building_tiles(tiles, origin, removed=()):
    """Building squares within STORE_SITE_CATCHMENT_TILES of the 2x2 site;
    squares off the map count as empty (the guide: a store at the map edge
    gets no customers from beyond it)."""
    r = STORE_SITE_CATCHMENT_TILES
    count = 0
    for y in range(origin[1] - r, origin[1] + STORE_SITE_FOOTPRINT[1] + r):
        for x in range(origin[0] - r, origin[0] + STORE_SITE_FOOTPRINT[0] + r):
            index = tiles.get((x, y))
            if index is not None and index not in removed:
                count += 1
    return count


def store_site_rules(rows, buildings):
    tiles = building_tiles(buildings)
    counts = [
        catchment_building_tiles(tiles, (x, y))
        for y in range(len(rows))
        for x in range(len(rows[0]))
        if site_is_buildable(rows, (x, y))
    ]
    return {
        "evidence_note": (
            "Task #95. CONFIRMED_OFFICIAL: a store takes 2x2 map squares (DATA4 コンビニ(自)); "
            "land cost = 地価(4エリア分) + 建物評価額÷2 (guide third book p.79, p.7); no store "
            "within 5 squares of another (guide p.7 ring diagram). CONFIRMED_OFFICIAL/"
            "CONFIRMED_COMMUNITY price anchors: start-of-game vacant lots 20,000,000 (rail side, "
            "map centre; the wiki minimum), 25,000,000 (near a school, facing a main road), "
            "26,000,000 and 30,000,000 (guide p.6-8). REMAKE_BALANCED_DEFAULT: the price shape "
            "(floor 20,000,000, +5,000,000 when the site touches a road, up to +5,000,000 by the "
            "share of built-up squares in the surrounding 16x16 area relative to the busiest "
            "site, rounded to 1,000,000), the later growth by LandValuePolicy's yearly rate, "
            "and the customer catchment: the site's nearby population = demand.nearby_population "
            "x (building squares in that 16x16 area / the mean over every buildable site). "
            "The 16x16 area itself is the guide's zone around a store for security facilities "
            "(PDF3 p.10), used by analogy. PROVISIONAL: DATA4's bare building prices read as "
            "万円 (building_price_unit_yen)."
        ),
        "footprint_tiles": list(STORE_SITE_FOOTPRINT),
        "land_area_count": STORE_SITE_LAND_AREA_COUNT,
        "min_store_distance_tiles": STORE_SITE_MIN_STORE_DISTANCE,
        "unbuildable_tiles": list(STORE_SITE_UNBUILDABLE),
        "floor_land_price_yen": STORE_SITE_FLOOR_PRICE_YEN,
        "road_bonus_yen": STORE_SITE_ROAD_BONUS_YEN,
        "density_bonus_yen": STORE_SITE_DENSITY_BONUS_YEN,
        "price_step_yen": STORE_SITE_PRICE_STEP_YEN,
        "catchment_tiles": STORE_SITE_CATCHMENT_TILES,
        "max_catchment_building_tiles": max(counts),
        "mean_catchment_building_tiles": round(sum(counts) / len(counts), 3),
        "building_price_unit_yen": BUILDING_PRICE_UNIT_YEN,
    }


def site_quote(block, origin, removed=()):
    """Start-of-game quote for a 2x2 site, mirrored by game/scripts/domain/
    store_site.gd (the contract test checks both give the same numbers)."""
    rows, buildings, rules = block["tile_rows"], block["buildings"], block["store_site"]
    if not site_is_buildable(rows, origin):
        return None
    tiles = building_tiles(buildings)
    density = catchment_building_tiles(tiles, origin) / rules["max_catchment_building_tiles"]
    price = rules["floor_land_price_yen"] + rules["density_bonus_yen"] * min(1.0, density)
    if site_faces_road(rows, origin):
        price += rules["road_bonus_yen"]
    step = rules["price_step_yen"]
    land = int((price + step / 2) // step * step)
    bought = sorted({tiles[t] for t in site_footprint(origin) if t in tiles})
    building_value = sum(
        block["building_catalog"][buildings[i]["sprite"]]["price"] * rules["building_price_unit_yen"]
        for i in bought
    )
    return {
        "land_yen": land,
        "building_yen": building_value // 2,
        "total_yen": land + building_value // 2,
        "bought_buildings": bought,
        "catchment_building_tiles": catchment_building_tiles(tiles, origin, set(bought)),
    }


# Task #98: rival stores. CONFIRMED_OFFICIAL: the beginner map starts with
# the rival's 本店 and 2号店 (quick reference guide オールテクニックガイド, book
# pages 66-83, the beginner map's DATA block:
# 本店 AM7:00-PM11:00 人気20 警備89 清掃30 サービス30; 2号店 AM7:00-PM11:00
# 人気20 警備58 清掃30 サービス31, 買収46,721,490円), drawn on the town map as
# the red 本 and 02 marks (gameplay video, map_red_hq / map_red_02). Where they
# stand is not recorded anywhere. REMAKE_BALANCED_DEFAULT: each is placed, in
# turn, on the vacant 2x2 site whose customers (split with the stores
# already placed) are the most, at least STORE_SITE_MIN_STORE_DISTANCE from
# them; ties go to the top-left-most site. A building square inside several
# stores' catchments sends each of them an equal share of its customers.
RIVAL_STORES = (
    {
        "id": "rival-hq", "role": "head", "name": "ライバル本店", "sprite": "map_red_hq",
        "guide_data": {"hours": "AM7:00〜PM11:00", "popularity": 20, "security": 89, "cleaning": 30, "service": 30},
    },
    {
        "id": "rival-02", "role": "branch", "name": "ライバル2号店", "sprite": "map_red_02",
        "guide_data": {"hours": "AM7:00〜PM11:00", "popularity": 20, "security": 58, "cleaning": 30, "service": 31, "buyout_yen": 46_721_490},
    },
)


# Task #101: investigating and buying out a rival.
# CONFIRMED_OFFICIAL: the rival menu offers 「調査する 費用 / 買収する 費用 / 何もしない」
# (guide p.53, p.65, p.72-73 screenshots); a buyout takes the rival's store,
# land and staff over as the player's own (p.53 「相手の店や社員ごと自分のものに」,
# p.72 「土地も店舗も一度にプレーヤーのものに」); the 2号店 costs 46,721,490 at the
# start (the DATA block). CONFIRMED_COMMUNITY: only branches can be bought, not
# the 本店 (first-title wiki; the DATA block likewise prints a buyout price for
# the 2号店 only). PROVISIONAL: the investigation fee -- 600,000 in the two
# screenshots that show the DATA block's 46,721,490, 500,000 in the p.53 one.
RIVAL_ACTIONS = {
    "investigation_cost_yen": 600_000,
    "evidence_note": (
        "Task #101. CONFIRMED_OFFICIAL: 調査する / 買収する / 何もしない (guide p.53, p.65, p.72-73); "
        "a buyout takes over the store, land and staff; the 2号店 costs 46,721,490 at the start "
        "(DATA block). CONFIRMED_COMMUNITY: 本店 cannot be bought (first-title wiki). "
        "PROVISIONAL: investigation 600,000 (two screenshots; 500,000 in a third). "
        "CONFIRMED that the price grows with the years and the store's sales (wiki: about 45,000,000 "
        "at the start, over 200,000,000 some years later), formula unknown; "
        "REMAKE_BALANCED_DEFAULT: the start price grows with the land price's yearly rate, a bought "
        "branch is counted as one of the player's stores and drawn as the blue 02 mark, and its own "
        "sales are not simulated (like the chain-expansion action)."
    ),
}


# Task #106: rivals losing money, withdrawing and opening again elsewhere.
# CONFIRMED_OFFICIAL: cutting the new store's 商品利益率 15-20% near a rival
# branch makes it post losses several months in a row, and it withdraws
# (guide p.53 flowchart); "赤字が半年も続けば、ライバルは撤退するはずだ" (two
# map strategy pages); a map holds at most 10 stores, rivals included (quick
# reference, 中級). CONFIRMED_COMMUNITY (PS/SS long-play records, B+): after a
# branch closes the rival soon opens a branch somewhere else; 5% off did not
# topple a strong branch, 15% did; a price cut far from the branch had no
# effect. PROVISIONAL (a player's inference): the 本店 does not withdraw while
# the rival still has a branch.
# REMAKE_BALANCED_DEFAULT: the shape -- a rival loses the month when
# (share of its catchment's building squares also in a player store's
# catchment) x min(1, price cut / 20%) >= 0.5; it withdraws after 6 losing
# months in a row; a withdrawn branch reopens at the next month end on the
# vacant site place_rivals() would pick, at least 5 squares from where it was
# (the records say it opens somewhere else); a withdrawn 本店 never reopens.
RIVAL_AI = {
    "full_effect_price_cut_pct": 20,
    "deficit_pressure_threshold": 0.5,
    "withdraw_after_deficit_months": 6,
    "town_store_limit": 10,
    "reopen_after_month_ends": 1,
    "evidence_note": (
        "Task #106. CONFIRMED_OFFICIAL: cutting the store's 商品利益率 15-20% near a rival branch makes it "
        "post losses several months in a row and withdraw (guide p.53); 赤字が半年も続けば、ライバルは撤退する "
        "(two map strategy pages); at most 10 stores on a map, rivals included (quick reference, 中級). "
        "CONFIRMED_COMMUNITY (PS/SS long-play records): a closed branch soon reopens elsewhere; 5% off did not "
        "topple a strong branch while 15% did; a cut far from the branch had no effect. PROVISIONAL: the 本店 "
        "does not withdraw while the rival has a branch. Reading the game's price policy (% from list price) "
        "as the guide's 商品利益率 cut is an inference. REMAKE_BALANCED_DEFAULT: a rival loses the month when "
        "(share of its catchment's building squares also in a player store's catchment) x min(1, price cut / "
        "20%) >= 0.5; it withdraws after 6 losing months in a row; a withdrawn branch reopens at the next "
        "month end on the vacant site with the most customers left to it, at least 5 squares from where it was "
        "(the records say it opens somewhere else); a withdrawn 本店 never reopens."
    ),
}


# Task #111: 販促 → 誘致, asking for a facility to be built where the player
# chooses. CONFIRMED_OFFICIAL (guide PDF1 p.45 「誘致できる施設リスト」): the 18
# facilities with their size, time to build (1ヶ月+0〜3日) and 援助額; only
# one facility can be under 誘致 at a time; it may take in the buildings on
# its squares ("誘致は、その空間すべての建築物を巻き込んでしまう", p.88).
# CONFIRMED_OFFICIAL (PDF3 p.10, PDF4 p.74): 店舗のセキュリティ値 = 社員のセキュ
# リティ値合計×店舗規模別基準値 + セキュリティ施設の効果; a 交番 adds 10 for each
# of its squares inside the 16x16 area around the store (at most 40), a 消防署
# 5 for each (at most 30). CONFIRMED_VISUAL (videos V01/V03,
# docs/research/video-v01-opening-parameters-2026-09-08.md): the 援助額 is
# paid when the place is chosen and a place price (場所代) that depends on
# the place is paid on top (交番 2,000,000-4,000,000 at the start of a game,
# a 3x2 プール 3,800,000). The building's squares, customers and wanted items
# are its DATA4 entry (TOWN_BUILDINGS); where the table's size is the same
# area turned round, DATA4's orientation is used (its sprite is drawn that
# way). CONFLICT: 体育館 is 2x3 in the 誘致 table but 3x3 in DATA4 -- DATA4 is
# used (PROVISIONAL); マンション has no DATA4 entry and is drawn as 住宅(大C)
# (PROVISIONAL). REMAKE_BALANCED_DEFAULT: the place price is a tenth of the
# store land price for the same number of squares at that place (anchored to
# the two video quotes above), rounded to 100,000; the extra 0-3 days are
# drawn at random.
INDUCEMENT_FACILITIES = (
    # (id, name, DATA4 sprite, 誘致 table size, 援助額, (security per square, most))
    ("police_box", "交番", "police_box_building", (2, 2), 400_000, (10, 40)),
    ("fire_station", "消防署", "fire_station_building", (2, 3), 600_000, (5, 30)),
    ("apartment", "マンション", "house_large_c", (2, 3), 4_200_000, (0, 0)),
    ("company", "会社", "company_large_a", (3, 3), 5_400_000, (0, 0)),
    ("gym", "体育館", "gym_building", (2, 3), 4_200_000, (0, 0)),
    ("pool", "プール", "pool_building", (2, 3), 1_800_000, (0, 0)),
    ("athletic_field", "運動場", "athletic_field_building", (4, 5), 2_000_000, (0, 0)),
    ("event_hall", "イベント会場", "event_hall_building", (2, 2), 6_000_000, (0, 0)),
    ("kindergarten", "幼稚園", "kindergarten_building", (2, 3), 1_200_000, (0, 0)),
    ("elementary_school", "小学校", "elementary_school_building", (4, 4), 3_200_000, (0, 0)),
    ("middle_school", "中学校", "middle_school_building", (5, 5), 5_000_000, (0, 0)),
    ("high_school", "高校", "high_school_building", (6, 6), 7_200_000, (0, 0)),
    ("university", "大学", "university_building", (7, 7), 9_800_000, (0, 0)),
    ("vocational_school", "専門学校", "vocational_school_building", (3, 4), 4_800_000, (0, 0)),
    ("park", "公園", "large_park_building", (2, 2), 2_000_000, (0, 0)),
    ("aquarium", "水族館", "aquarium_building", (3, 3), 2_700_000, (0, 0)),
    ("zoo", "動物園", "zoo_building", (6, 6), 7_200_000, (0, 0)),
    ("amusement_park", "遊園地", "amusement_park_building", (7, 7), 9_800_000, (0, 0)),
)
INDUCEMENT_RULES = {
    "build_days": 4,
    "build_extra_days_max": 3,
    "place_price_share_of_land": 0.1,
    "place_price_step_yen": 100_000,
    "evidence_note": (
        "Task #111. CONFIRMED_OFFICIAL (guide PDF1 p.45): the 18 facilities, their size, 1ヶ月(+0〜3日) to build "
        "and 援助額; one facility under 誘致 at a time; it takes in the buildings on its squares (p.88); a 交番 adds "
        "10 セキュリティ per square inside the 16x16 area around the store (at most 40), a 消防署 5 (at most 30) "
        "(PDF3 p.10, PDF4 p.74). A month is 4 representative days "
        "(1月=4日間×8). CONFIRMED_VISUAL (videos V01/V03): the 援助額 is paid when the place is chosen, and a "
        "place price that depends on the place is paid on top (交番 2,000,000-4,000,000 at the start, a 3x2 "
        "プール 3,800,000). The building's squares, customers and wanted items are its DATA4 entry, in DATA4's "
        "orientation. CONFLICT/PROVISIONAL: 体育館 2x3 (誘致 table) vs 3x3 (DATA4), DATA4 used; マンション has no "
        "DATA4 entry and is drawn as 住宅(大C). REMAKE_BALANCED_DEFAULT: the place price is a tenth of the store "
        "land price for as many squares at that place (anchored to the video quotes), rounded to 100,000; the "
        "0-3 extra days are random."
    ),
}


# Task #112: the facility ids reference_sim's TOWN_FACILITIES uses where
# they differ from this table's.
TOWN_FACILITY_IDS = {"apartment": "mansion"}


def inducement_block():
    from conveni_sim.baseline_data import TOWN_BUILDINGS, TOWN_FACILITIES

    footprints = {profile.id: profile.footprint.value for profile in TOWN_BUILDINGS}
    shoppers = {
        anchor.id: anchor.shopping_population.value
        for anchor in TOWN_FACILITIES
        if anchor.shopping_population is not None
    }
    facilities = []
    for facility_id, name, sprite, table_size, aid, (per_square, most) in INDUCEMENT_FACILITIES:
        facilities.append({
            "id": facility_id,
            "name": name,
            "sprite": sprite,
            "size": list(footprints[sprite]),
            "table_size": list(table_size),
            "aid_yen": aid,
            "security_per_square": per_square,
            "security_max": most,
            # Task #112: 買い物人口 where reference_sim records it
            # (CONFIRMED_OFFICIAL guide table), else null.
            "shopping_population": shoppers.get(TOWN_FACILITY_IDS.get(facility_id, facility_id)),
        })
    return dict(INDUCEMENT_RULES, facilities=facilities)


def inducement_place_price(block, facility, origin, removed=()):
    """REMAKE_BALANCED_DEFAULT place price (see INDUCEMENT_FACILITIES)."""
    rules = block["inducement"]
    quote = site_quote(block, origin, removed)
    if quote is None:
        return None
    squares = facility["size"][0] * facility["size"][1]
    price = quote["land_yen"] * squares / 4 * rules["place_price_share_of_land"]
    step = rules["place_price_step_yen"]
    return int((price + step / 2) // step * step)


# Task #114: the town grows, and at set populations the town builds its
# own 市役所, 駅, 区役所 and 都庁 (the beginner map is cleared when the 都庁
# stands). CONFIRMED_OFFICIAL: the beginner map starts with 2,179 住人 and
# is cleared by 「都庁を誘致する」, which "人口を増やせば都庁は自然と建設される"
# (guide PDF2 p.86, p.11); 人口5000人以上=市役所, 8000人以上=区役所,
# 20000人以上=都庁, and 人口が5000人を超えると駅ができる (線路沿い) (PDF3 p.10);
# "8年ほどの経営で都庁誘致できるはずだ" (PDF2 p.86). CONFIRMED_VISUAL (video
# V03 monthly reports): 町人口 2,106 → 2,262 → 2,338 → ... → 2,401, i.e.
# +63 to +156 a month. PROVISIONAL: which DATA4 building stands for each
# (市役所 = 役場(村役場) 2x2, 区役所 = 役所(県庁) 5x5, 都庁 7x7, 駅 = 駅(小)
# 2x1). Analogy: the monthly growth rate is the one that takes 2,179 to
# 20,000 in the guide's 8 years (96 months). REMAKE_BALANCED_DEFAULT: that
# the rate is the same every month, that the store's customers grow with
# the town's population, and where each building goes (the buildable spot
# taking in the fewest buildings, nearest the middle of the map; the 駅
# beside the railway).
TOWN_GROWTH = {
    "start_population": 2_179,
    "monthly_growth_rate": round((20_000 / 2_179) ** (1 / 96) - 1, 6),
    "milestones": [
        {"id": "city_office", "name": "市役所", "population": 5_000, "sprite": "village_office", "size": [2, 2], "near_railway": False},
        {"id": "station", "name": "駅", "population": 5_000, "sprite": "station_small", "size": [2, 1], "near_railway": True},
        {"id": "ward_office", "name": "区役所", "population": 8_000, "sprite": "prefectural_office", "size": [5, 5], "near_railway": False},
        {"id": "metropolitan_office", "name": "都庁", "population": 20_000, "sprite": "metropolitan_government_office", "size": [7, 7], "near_railway": False},
    ],
    "clear_milestone": "metropolitan_office",
    "evidence_note": (
        "Task #114. CONFIRMED_OFFICIAL: the beginner map starts with 2,179 住人 and is cleared by 都庁を誘致する, the "
        "都庁 being built once the population is large enough (PDF2 p.86, p.11); 5,000 → 市役所 and 駅 (along the "
        "railway), 8,000 → 区役所, 20,000 → 都庁 (PDF3 p.10); about 8 years to reach it (PDF2 p.86). "
        "CONFIRMED_VISUAL (V03 monthly reports): 町人口 +63 to +156 a month early on. PROVISIONAL: 市役所 drawn as "
        "役場(村役場) 2x2, 区役所 as 役所(県庁) 5x5, 駅 as 駅(小) 2x1. Analogy: monthly growth rate = the rate taking "
        "2,179 to 20,000 in 96 months. REMAKE_BALANCED_DEFAULT: the same rate every month, the store's customers "
        "growing with the population, and where each building is put (fewest buildings taken in, then nearest "
        "the map's middle; the 駅 beside the railway)."
    ),
}


def best_town_building_site(rows, buildings, size, stores, removed=(), near_railway=False):
    """Where the town puts a 役所 or 駅 (REMAKE_BALANCED_DEFAULT, see TOWN_GROWTH)."""
    tiles = building_tiles(buildings)
    height, width = len(rows), len(rows[0])
    middle = ((width - size[0]) / 2, (height - size[1]) / 2)
    best = None
    for y in range(height - size[1] + 1):
        for x in range(width - size[0] + 1):
            cells = [(x + dx, y + dy) for dy in range(size[1]) for dx in range(size[0])]
            if any(rows[cy][cx] in STORE_SITE_UNBUILDABLE for cx, cy in cells):
                continue
            if any(
                sx < x + size[0] and x < sx + 2 and sy < y + size[1] and y < sy + 2 for sx, sy in stores
            ):
                continue
            if near_railway and not any(
                0 <= cy + d < height and rows[cy + d][cx] == "T" for cx, cy in cells for d in (-1, 1)
            ):
                continue
            taken = len({tiles[c] for c in cells if c in tiles and tiles[c] not in removed})
            key = (taken, (x - middle[0]) ** 2 + (y - middle[1]) ** 2, y, x)
            if best is None or key < best[0]:
                best = (key, (x, y))
    return None if best is None else best[1]


def place_town_buildings(block, stores):
    """Every town building in turn on a map that has grown to 20,000 people,
    each counting the ones put up before it (as the game does)."""
    buildings = list(block["buildings"])
    removed = set()
    placed = {}
    for milestone in block["town_growth"]["milestones"]:
        site = best_town_building_site(
            block["tile_rows"], buildings, milestone["size"], stores, removed, milestone["near_railway"]
        )
        tiles = building_tiles(buildings)
        for dy in range(milestone["size"][1]):
            for dx in range(milestone["size"][0]):
                cell = (site[0] + dx, site[1] + dy)
                if cell in tiles:
                    removed.add(tiles[cell])
        buildings.append({"sprite": milestone["sprite"], "tile": list(site), "size": milestone["size"]})
        placed[milestone["id"]] = site
    return placed


def rival_pressure(tiles, rival_origin, player_origins, price_change_pct, removed=()):
    """How hard the player's stores press a rival this month (REMAKE shape)."""
    mine = [t for t, index in tiles.items() if index not in removed and in_catchment(rival_origin, t)]
    if not mine:
        return 0.0
    shared = sum(1 for t in mine if any(in_catchment(o, t) for o in player_origins))
    cut = min(1.0, max(0, -price_change_pct) / RIVAL_AI["full_effect_price_cut_pct"])
    return shared / len(mine) * cut


def best_open_site(rows, buildings, stores, removed=(), avoid=()):
    """The vacant 2x2 site a rival opens on: most customers left to it,
    at least STORE_SITE_MIN_STORE_DISTANCE from every store and from the
    `avoid` sites (where it just withdrew from: it opens somewhere else);
    ties go to the top-left-most site (same rule as place_rivals)."""
    tiles = building_tiles(buildings)
    best = None
    for y in range(len(rows)):
        for x in range(len(rows[0])):
            origin = (x, y)
            if not site_is_buildable(rows, origin):
                continue
            if any(t in tiles and tiles[t] not in removed for t in site_footprint(origin)):
                continue
            if any(
                max(abs(x - o[0]), abs(y - o[1])) < STORE_SITE_MIN_STORE_DISTANCE
                for o in list(stores) + list(avoid)
            ):
                continue
            score = shared_catchment(tiles, origin, stores, removed)
            if best is None or score > best[0] + 1e-9:
                best = (score, origin)
    return None if best is None else best[1]


def in_catchment(store_origin, tile):
    r = STORE_SITE_CATCHMENT_TILES
    return (
        store_origin[0] - r <= tile[0] < store_origin[0] + STORE_SITE_FOOTPRINT[0] + r
        and store_origin[1] - r <= tile[1] < store_origin[1] + STORE_SITE_FOOTPRINT[1] + r
    )


def shared_catchment(tiles, origin, others, removed=()):
    """Building squares in the site's catchment, each counted as 1/n when n
    stores (this one included) have it in their catchment."""
    total = 0.0
    for tile, index in tiles.items():
        if index in removed or not in_catchment(origin, tile):
            continue
        total += 1.0 / (1 + sum(1 for other in others if in_catchment(other, tile)))
    return total


def place_rivals(rows, buildings):
    tiles = building_tiles(buildings)
    placed = []
    for rival in RIVAL_STORES:
        best = None
        for y in range(len(rows)):
            for x in range(len(rows[0])):
                origin = (x, y)
                if not site_is_buildable(rows, origin):
                    continue
                if any(t in tiles for t in site_footprint(origin)):
                    continue
                if any(max(abs(x - o[0]), abs(y - o[1])) < STORE_SITE_MIN_STORE_DISTANCE for o in placed):
                    continue
                score = shared_catchment(tiles, origin, placed)
                if best is None or score > best[0] + 1e-9:
                    best = (score, origin)
        placed.append(best[1])
    return [
        dict(rival, position=list(origin), permits_held=[], buyable="buyout_yen" in rival["guide_data"])
        for rival, origin in zip(RIVAL_STORES, placed)
    ]
