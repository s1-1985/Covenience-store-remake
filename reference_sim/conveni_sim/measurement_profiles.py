from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median
from typing import Optional

from .observations import GameTimestamp, GameplayObservationTimeline


@dataclass(frozen=True)
class NumericSummary:
    sample_count: int
    minimum: float
    mean: float
    median: float
    maximum: float


@dataclass(frozen=True)
class CheckoutTimingProfile:
    staff_id: Optional[str]
    fixture_id: Optional[str]
    game_minutes: NumericSummary
    video_seconds: Optional[NumericSummary]


@dataclass(frozen=True)
class ArrivalWindowSample:
    start: GameTimestamp
    end: GameTimestamp
    window_game_minutes: int
    arrival_count: int
    arrivals_per_game_hour: float
    share_percent: Optional[float] = None
    popularity: Optional[float] = None
    weather: Optional[str] = None
    store_open: Optional[bool] = None
    note: str = ""


def summarize_numeric(values: tuple[float, ...]) -> NumericSummary:
    if not values:
        raise ValueError("at least one value is required")
    return NumericSummary(
        sample_count=len(values),
        minimum=min(values),
        mean=mean(values),
        median=median(values),
        maximum=max(values),
    )


def checkout_timing_profiles(timeline: GameplayObservationTimeline) -> tuple[CheckoutTimingProfile, ...]:
    groups: dict[tuple[Optional[str], Optional[str]], list] = {}
    for measurement in timeline.checkout_service_durations():
        key = (measurement.start.staff_id, measurement.start.fixture_id)
        groups.setdefault(key, []).append(measurement)

    profiles: list[CheckoutTimingProfile] = []
    for (staff_id, fixture_id), measurements in groups.items():
        game_values = tuple(float(m.game_minutes) for m in measurements)
        video_values = tuple(float(m.video_seconds) for m in measurements if m.video_seconds is not None)
        profiles.append(
            CheckoutTimingProfile(
                staff_id=staff_id,
                fixture_id=fixture_id,
                game_minutes=summarize_numeric(game_values),
                video_seconds=summarize_numeric(video_values) if video_values else None,
            )
        )
    profiles.sort(key=lambda p: ((p.staff_id or ""), (p.fixture_id or "")))
    return tuple(profiles)


def make_arrival_window_sample(
    timeline: GameplayObservationTimeline,
    start: GameTimestamp,
    end: GameTimestamp,
    *,
    share_percent: Optional[float] = None,
    popularity: Optional[float] = None,
    weather: Optional[str] = None,
    store_open: Optional[bool] = None,
    note: str = "",
) -> ArrivalWindowSample:
    window_minutes = start.minutes_until(end)
    if window_minutes <= 0:
        raise ValueError("arrival window must have positive duration")
    if share_percent is not None and not 0 <= share_percent <= 100:
        raise ValueError("share_percent must be 0..100 or None")
    if popularity is not None and not 0 <= popularity <= 100:
        raise ValueError("popularity must be 0..100 or None")
    count = timeline.count_arrivals(start, end)
    return ArrivalWindowSample(
        start=start,
        end=end,
        window_game_minutes=window_minutes,
        arrival_count=count,
        arrivals_per_game_hour=count * 60.0 / window_minutes,
        share_percent=share_percent,
        popularity=popularity,
        weather=weather,
        store_open=store_open,
        note=note,
    )
