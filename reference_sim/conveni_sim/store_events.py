from __future__ import annotations

from dataclasses import dataclass

from .store_value import SecurityFacilityCoverage

DONATION_CASH_THRESHOLD_YEN = 1_500_000_000
"""Source: strategy guide event-trigger table ("寄付: 手持ち資金が15億円以上で月が変わる")."""

DONATION_MINIMUM_DEDUCTION_YEN = 1_000_000_000
"""Source: same table ("10億円以上の資金が強制的に寄付金として差し引かれる").

Only a floor is given, not an exact formula for how much above 10億円 is
taken; this module therefore exposes the trigger condition and the known
floor, not a computed deduction amount.
"""

TOWN_POPULATION_THRESHOLD = 10_000
STORE_COUNT_THRESHOLD = 5
CONTEST_PRIZE_YEN_PER_STORE = 10_000_000
"""Source: strategy guide event-trigger table for 業界誌掲載/コンビニコンテスト
("人口1万人以上 かつ マップ内に5店舗以上"; contest prize = "店舗数(ライバル店を
含む)×1000万円"). Only the eligibility gate is confirmed as deterministic;
whether the event actually fires once eligible is described as "選ばれる
こともある" (may or may not be picked), so this module does not roll that
draw.
"""

METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD = 20_000
"""Source: strategy guide quick reference book, マップ攻略 section (book
pages 80-83), body text for the 初級(beginner) scenario's own clear
condition: "20000人の人口を集めれば、役所用地に都庁が建設される" (once town
population reaches 20,000, the metropolitan government building is built
automatically on the designated 役場用地 land). CONFIRMED_OFFICIAL -- this
upgrades what `baseline_data.SCENARIOS`'s `beginner.objective` field and an
earlier wiki-only research note had recorded as a PROVISIONAL/CONFIRMED_
COMMUNITY "population threshold" into a directly-quoted guide body-text
statement, and gives the exact number for the first time. Not wired into
`game/`: no scenario-selection mechanic exists there to attach a beginner-
specific clear condition to (same boundary as decision 0131's rival
topology work)."""


def metropolitan_government_is_induced(town_population: int) -> bool:
    """初級シナリオのクリア条件: 町人口が20000人に達すると都庁が自動建設される。

    This is a population threshold, not a player action -- the guide's own
    text frames it as "誘致というより、マップ内の人口をいかにして増やすかが課題だ"
    (less "inducing" it than growing the town's population). See
    METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD for the source citation.
    """
    if town_population < 0:
        raise ValueError("town_population must be >= 0")
    return town_population >= METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD


GAME_OVER_YEAR_LIMIT = 100
"""Source: strategy guide ("ゲームオーバー: 破産、またはクリア条件未達成の
まま100年経過"). "100年経過" is read as year > 100 (100 full years have
elapsed since the scenario's year 1 start), not year >= 100; this is an
interpretation of the printed Japanese, not a separately-confirmed exact
boundary.
"""


def donation_event_is_eligible(cash_yen: int) -> bool:
    """寄付イベントの発生し得る条件(月が変わる、というカレンダー条件は呼び出し側の責務)。"""
    if cash_yen < 0:
        raise ValueError("cash_yen must be >= 0")
    return cash_yen >= DONATION_CASH_THRESHOLD_YEN


def magazine_or_contest_event_is_eligible(
    town_population: int,
    store_count_including_rivals: int,
) -> bool:
    """業界誌掲載/コンビニコンテストが発生し得る条件(実際に選ばれるかは別途)。"""
    if town_population < 0:
        raise ValueError("town_population must be >= 0")
    if store_count_including_rivals < 0:
        raise ValueError("store_count_including_rivals must be >= 0")
    return (
        town_population >= TOWN_POPULATION_THRESHOLD
        and store_count_including_rivals >= STORE_COUNT_THRESHOLD
    )


def compute_contest_prize_yen(store_count_including_rivals: int) -> int:
    """コンビニコンテストの賞金 = 店舗数(ライバル店を含む) × 1000万円."""
    if store_count_including_rivals < 0:
        raise ValueError("store_count_including_rivals must be >= 0")
    return store_count_including_rivals * CONTEST_PRIZE_YEN_PER_STORE


def shoplifting_is_possible(customer_manner_value: int, store_security_value: float) -> bool:
    """万引きが発生し得る条件: 顧客のマナー値が店舗のセキュリティ値を上回る。

    Source: strategy guide event-trigger table ("万引き: 顧客のマナー値 >
    店舗の警備値"). The guide does not name a per-customer "manner value"
    field this codebase currently tracks (the deep-read customer-visit
    schedule kept the guide's 9-column tuning stats as an unlabeled raw
    tuple rather than a confidently-named "manner" field, per
    docs/decisions/0078); a caller must supply that value explicitly rather
    than this module inventing where it comes from.
    """
    return customer_manner_value > store_security_value


@dataclass(frozen=True)
class FireOrRobberyRisk:
    """Whether a store currently has any guide-confirmed fire/robbery protection.

    Source: strategy guide event-trigger table ("火災/強盗: 店舗周囲16×16
    エリアにセキュリティ施設(交番/消防署)が無い場合"; "警備値より人気が高い
    と発生しやすい"). This class exposes the deterministic protection
    boundary (is any facility in range at all) and the confirmed
    comparative hint (popularity > security makes it more likely); it does
    not compute an actual fire/robbery probability, which the guide never
    gives as an exact number.
    """

    security_coverage: SecurityFacilityCoverage
    store_popularity: int
    store_security_value: float

    def __post_init__(self) -> None:
        if not 0 <= self.store_popularity <= 100:
            raise ValueError("store_popularity must be 0..100")

    @property
    def is_unprotected(self) -> bool:
        return not self.security_coverage.has_any_protection

    @property
    def popularity_exceeds_security(self) -> bool:
        """Guide hint: more likely when popularity outstrips the security value."""
        return self.store_popularity > self.store_security_value

    @property
    def risk_factors_present(self) -> bool:
        return self.is_unprotected or self.popularity_exceeds_security


def scenario_time_limit_exceeded(current_year: int, clear_condition_met: bool) -> bool:
    """ゲームオーバー判定(破産以外の経路): クリア条件未達成のまま100年経過。

    Bankruptcy itself is already handled elsewhere (economy.py's
    BankruptcyPolicy / month_boundary.py's MonthBoundaryTerminalGate); this
    covers only the guide's second, time-limit game-over path.
    """
    if current_year < 1:
        raise ValueError("current_year must be >= 1")
    return current_year > GAME_OVER_YEAR_LIMIT and not clear_condition_met
