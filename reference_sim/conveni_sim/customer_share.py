from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional


class ShareRecalculationReason(str, Enum):
    """Observed or caller-supplied reasons to refresh customer share."""

    DATE_CHANGE = "date_change"
    WEATHER_CHANGE = "weather_change"
    EXPLICIT = "explicit"


@dataclass(frozen=True)
class CustomerShareInputs:
    """Known customer-share inputs without an invented formula.

    The first-title Wiki reports these factors as relevant to customer share,
    but does not provide a complete equation. Every field is therefore an
    explicit observation/input; None means unknown rather than neutral/zero.
    """

    popularity: Optional[int] = None
    cleaning: Optional[int] = None
    service: Optional[int] = None
    nearby_population: Optional[int] = None
    assortment_product_ids: Optional[tuple[str, ...]] = None
    product_prices_yen: Optional[tuple[tuple[str, int], ...]] = None
    opening_minutes_per_day: Optional[int] = None
    weather: Optional[str] = None
    competing_store_ids: Optional[tuple[str, ...]] = None
    is_main_store: Optional[bool] = None
    security: Optional[int] = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.popularity, "popularity"),
            (self.cleaning, "cleaning"),
            (self.service, "service"),
            (self.security, "security"),
        ):
            if value is not None and not 0 <= value <= 100:
                raise ValueError(f"{name} must be 0..100 or None")
        if self.nearby_population is not None and self.nearby_population < 0:
            raise ValueError("nearby_population must be >= 0 or None")
        if self.opening_minutes_per_day is not None and not 0 <= self.opening_minutes_per_day <= 1440:
            raise ValueError("opening_minutes_per_day must be 0..1440 or None")
        if self.product_prices_yen is not None:
            for product_id, price_yen in self.product_prices_yen:
                if not product_id:
                    raise ValueError("product id must be non-empty")
                if price_yen < 0:
                    raise ValueError("product price must be >= 0")


@dataclass(frozen=True)
class CustomerShareSnapshot:
    share_percent: int
    inputs: CustomerShareInputs
    reasons: tuple[ShareRecalculationReason, ...]
    source: str


class CustomerShareRuntime:
    """Evidence-safe share state and recalculation trigger ledger.

    The original share equation is unresolved. This class never computes share.
    It only records known inputs, tracks observed recalculation triggers, and
    accepts a caller/observation supplied result.
    """

    def __init__(self, inputs: CustomerShareInputs = CustomerShareInputs()) -> None:
        self.inputs = inputs
        self.current_share_percent: Optional[int] = None
        self._pending_reasons: list[ShareRecalculationReason] = []
        self._history: list[CustomerShareSnapshot] = []

    @property
    def pending_reasons(self) -> tuple[ShareRecalculationReason, ...]:
        return tuple(self._pending_reasons)

    @property
    def history(self) -> tuple[CustomerShareSnapshot, ...]:
        return tuple(self._history)

    @property
    def recalculation_pending(self) -> bool:
        return bool(self._pending_reasons)

    def set_inputs(self, inputs: CustomerShareInputs) -> None:
        """Replace inputs without guessing when non-weather changes take effect."""
        self.inputs = inputs

    def request_recalculation(
        self,
        reason: ShareRecalculationReason,
        *,
        occurrences: int = 1,
    ) -> None:
        if occurrences <= 0:
            raise ValueError("occurrences must be positive")
        self._pending_reasons.extend([reason] * occurrences)

    def on_date_change(self, *, days_crossed: int = 1) -> None:
        self.request_recalculation(
            ShareRecalculationReason.DATE_CHANGE,
            occurrences=days_crossed,
        )

    def observe_weather(self, weather: str) -> None:
        """Update weather and request refresh only for a real known->known change."""
        if not weather:
            raise ValueError("weather must be non-empty")
        previous = self.inputs.weather
        self.inputs = replace(self.inputs, weather=weather)
        if previous is not None and previous != weather:
            self.request_recalculation(ShareRecalculationReason.WEATHER_CHANGE)

    def apply_share(self, share_percent: int, *, source: str) -> CustomerShareSnapshot:
        """Accept an externally observed/calculated share and clear pending triggers."""
        if not 0 <= share_percent <= 100:
            raise ValueError("share_percent must be 0..100")
        if not source:
            raise ValueError("source must be non-empty")
        snapshot = CustomerShareSnapshot(
            share_percent=share_percent,
            inputs=self.inputs,
            reasons=self.pending_reasons,
            source=source,
        )
        self.current_share_percent = share_percent
        self._history.append(snapshot)
        self._pending_reasons.clear()
        return snapshot
