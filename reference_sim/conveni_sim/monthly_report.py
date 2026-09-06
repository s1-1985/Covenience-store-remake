from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MonthlyReportValues:
    """Values displayed by the first-title monthly report.

    Each field is independently optional because the composition of profit/loss
    and other expenses is still unresolved.  Callers may therefore preserve a
    partially observed report without inventing hidden settlement arithmetic.
    """

    profit_loss_yen: Optional[int] = None
    other_expenses_yen: Optional[int] = None
    town_population: Optional[int] = None

    def __post_init__(self) -> None:
        if self.other_expenses_yen is not None and self.other_expenses_yen < 0:
            raise ValueError("other_expenses_yen must be >= 0 or None")
        if self.town_population is not None and self.town_population < 0:
            raise ValueError("town_population must be >= 0 or None")


@dataclass(frozen=True)
class MonthlyReportDelta:
    profit_loss_yen: Optional[int]
    other_expenses_yen: Optional[int]
    town_population: Optional[int]


@dataclass(frozen=True)
class MonthlyReportSnapshot:
    year: int
    month: int
    values: MonthlyReportValues
    previous_values: Optional[MonthlyReportValues]
    delta: MonthlyReportDelta

    def __post_init__(self) -> None:
        if self.year <= 0:
            raise ValueError("year must be > 0")
        if not 1 <= self.month <= 12:
            raise ValueError("month must be within 1..12")


@dataclass(frozen=True)
class MonthlySalesThresholdNotification:
    """One explicitly observed branch-month threshold notification.

    Threshold tiering is unresolved, so this record never infers additional
    notifications.  `previous_month_sales_yen` may remain unknown.  When it is
    known, the first-title wording '越えました' is enforced as strictly greater
    than the observed threshold.
    """

    store_id: str
    report_year: int
    report_month: int
    threshold_yen: int
    previous_month_sales_yen: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.store_id:
            raise ValueError("store_id must not be empty")
        if self.report_year <= 0:
            raise ValueError("report_year must be > 0")
        if not 1 <= self.report_month <= 12:
            raise ValueError("report_month must be within 1..12")
        if self.threshold_yen < 0:
            raise ValueError("threshold_yen must be >= 0")
        if self.previous_month_sales_yen is not None:
            if self.previous_month_sales_yen < 0:
                raise ValueError("previous_month_sales_yen must be >= 0 or None")
            if self.previous_month_sales_yen <= self.threshold_yen:
                raise ValueError("known sales must be strictly greater than threshold")


def _delta(current: Optional[int], previous: Optional[int]) -> Optional[int]:
    if current is None or previous is None:
        return None
    return current - previous


class MonthlyReportRuntime:
    """Store observed monthly report state without inventing month formulas."""

    def __init__(self) -> None:
        self._reports: list[MonthlyReportSnapshot] = []
        self._sales_notifications: list[MonthlySalesThresholdNotification] = []

    @property
    def reports(self) -> tuple[MonthlyReportSnapshot, ...]:
        return tuple(self._reports)

    @property
    def sales_notifications(self) -> tuple[MonthlySalesThresholdNotification, ...]:
        return tuple(self._sales_notifications)

    def record_report(
        self,
        *,
        year: int,
        month: int,
        values: MonthlyReportValues,
        previous_values: Optional[MonthlyReportValues] = None,
    ) -> MonthlyReportSnapshot:
        """Record a displayed report and only arithmetic deltas that are known.

        The caller supplies the displayed values.  The runtime deliberately does
        not derive them from representative-day samples or cash-ledger events,
        because the original monthly aggregation/settlement formula is not yet
        recovered.
        """

        delta = MonthlyReportDelta(
            profit_loss_yen=_delta(
                values.profit_loss_yen,
                previous_values.profit_loss_yen if previous_values else None,
            ),
            other_expenses_yen=_delta(
                values.other_expenses_yen,
                previous_values.other_expenses_yen if previous_values else None,
            ),
            town_population=_delta(
                values.town_population,
                previous_values.town_population if previous_values else None,
            ),
        )
        snapshot = MonthlyReportSnapshot(
            year=year,
            month=month,
            values=values,
            previous_values=previous_values,
            delta=delta,
        )
        self._reports.append(snapshot)
        return snapshot

    def record_sales_threshold_notification(
        self,
        notification: MonthlySalesThresholdNotification,
    ) -> MonthlySalesThresholdNotification:
        """Record one explicit notification without inferring other tiers."""

        self._sales_notifications.append(notification)
        return notification
