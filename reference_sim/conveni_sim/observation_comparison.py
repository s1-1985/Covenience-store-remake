from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Optional

from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind


@dataclass(frozen=True)
class ObservationIdentityMapping:
    """Explicit observed-id -> simulated-id correspondences.

    Identical literal ids still match without a mapping. Different ids never get
    guessed into correspondence: callers must supply that relationship here.
    Each mapping is one-to-one so two observed entities cannot silently collapse
    onto one simulated entity.
    """

    customer_ids: tuple[tuple[str, str], ...] = ()
    staff_ids: tuple[tuple[str, str], ...] = ()
    fixture_ids: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for label, pairs in (
            ("customer", self.customer_ids),
            ("staff", self.staff_ids),
            ("fixture", self.fixture_ids),
        ):
            observed = [item[0] for item in pairs]
            simulated = [item[1] for item in pairs]
            if any(not value for value in (*observed, *simulated)):
                raise ValueError(f"{label} identity mappings require non-empty ids")
            if len(observed) != len(set(observed)):
                raise ValueError(f"duplicate observed {label} id in identity mapping")
            if len(simulated) != len(set(simulated)):
                raise ValueError(f"duplicate simulated {label} id in identity mapping")

    @staticmethod
    def _translate(value: Optional[str], pairs: tuple[tuple[str, str], ...]) -> Optional[str]:
        if value is None:
            return None
        for observed, simulated in pairs:
            if observed == value:
                return simulated
        return value

    def customer(self, value: Optional[str]) -> Optional[str]:
        return self._translate(value, self.customer_ids)

    def staff(self, value: Optional[str]) -> Optional[str]:
        return self._translate(value, self.staff_ids)

    def fixture(self, value: Optional[str]) -> Optional[str]:
        return self._translate(value, self.fixture_ids)


@dataclass(frozen=True)
class ObservationEventSignature:
    kind: ObservationKind
    customer_id: Optional[str]
    staff_id: Optional[str]
    fixture_id: Optional[str]


@dataclass(frozen=True)
class ObservationKindCountDelta:
    kind: ObservationKind
    observed_count: int
    simulated_count: int
    delta: int


@dataclass(frozen=True)
class MatchedObservationEvent:
    signature: ObservationEventSignature
    observed: GameplayObservation
    simulated: GameplayObservation
    game_minute_delta: int
    numeric_delta: Optional[float]

    @property
    def exact_time_match(self) -> bool:
        return self.game_minute_delta == 0

    @property
    def exact_numeric_match(self) -> Optional[bool]:
        if self.observed.numeric_value is None or self.simulated.numeric_value is None:
            return None
        return self.numeric_delta == 0


@dataclass(frozen=True)
class ObservationTimelineComparison:
    observed_source_id: str
    simulated_source_id: str
    coverage: ObservationDayCoverage
    identity_mapping: ObservationIdentityMapping
    kind_counts: tuple[ObservationKindCountDelta, ...]
    matched: tuple[MatchedObservationEvent, ...]
    unmatched_observed: tuple[GameplayObservation, ...]
    unmatched_simulated: tuple[GameplayObservation, ...]

    @property
    def exact_event_match(self) -> bool:
        if self.unmatched_observed or self.unmatched_simulated:
            return False
        return all(
            item.game_minute_delta == 0
            and (item.numeric_delta is None or item.numeric_delta == 0)
            for item in self.matched
        )


class ObservationTimelineComparator:
    """Compare explicit observation events without fitting a tolerance or rule.

    Events are first restricted to the same caller-supplied representative-day
    coverage. Matching then uses kind + normalized customer/staff/fixture ids.
    Repeated events with the same signature are paired chronologically by ordinal
    occurrence. This reports factual count, missing-event and signed game-minute
    differences only; it does not decide whether any difference is acceptable.
    """

    @staticmethod
    def _in_coverage(event: GameplayObservation, coverage: ObservationDayCoverage) -> bool:
        return (
            event.game_time.year == coverage.year
            and event.game_time.month == coverage.month
            and event.game_time.day == coverage.day
            and coverage.start_minute_inclusive
            <= event.game_time.minute_of_day
            < coverage.end_minute_exclusive
        )

    @staticmethod
    def _observed_signature(
        event: GameplayObservation,
        mapping: ObservationIdentityMapping,
    ) -> ObservationEventSignature:
        return ObservationEventSignature(
            kind=event.kind,
            customer_id=mapping.customer(event.customer_id),
            staff_id=mapping.staff(event.staff_id),
            fixture_id=mapping.fixture(event.fixture_id),
        )

    @staticmethod
    def _simulated_signature(event: GameplayObservation) -> ObservationEventSignature:
        return ObservationEventSignature(
            kind=event.kind,
            customer_id=event.customer_id,
            staff_id=event.staff_id,
            fixture_id=event.fixture_id,
        )

    @staticmethod
    def _signature_sort_key(
        signature: ObservationEventSignature,
    ) -> tuple[str, str, str, str]:
        return (
            signature.kind.value,
            signature.customer_id or "",
            signature.staff_id or "",
            signature.fixture_id or "",
        )

    @staticmethod
    def _sort_events(events: list[GameplayObservation]) -> None:
        events.sort(key=lambda item: (item.game_time.representative_ordinal_minute, item.sequence))

    def compare(
        self,
        observed: GameplayObservationTimeline,
        simulated: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationTimelineComparison:
        observed_events = [
            event for event in observed.events if self._in_coverage(event, coverage)
        ]
        simulated_events = [
            event for event in simulated.events if self._in_coverage(event, coverage)
        ]

        observed_counts = Counter(event.kind for event in observed_events)
        simulated_counts = Counter(event.kind for event in simulated_events)
        kind_counts = tuple(
            ObservationKindCountDelta(
                kind=kind,
                observed_count=observed_counts[kind],
                simulated_count=simulated_counts[kind],
                delta=simulated_counts[kind] - observed_counts[kind],
            )
            for kind in sorted(
                set(observed_counts) | set(simulated_counts),
                key=lambda value: value.value,
            )
        )

        observed_buckets: dict[
            ObservationEventSignature, list[GameplayObservation]
        ] = defaultdict(list)
        simulated_buckets: dict[
            ObservationEventSignature, list[GameplayObservation]
        ] = defaultdict(list)

        for event in observed_events:
            observed_buckets[self._observed_signature(event, identity_mapping)].append(event)
        for event in simulated_events:
            simulated_buckets[self._simulated_signature(event)].append(event)

        matched: list[MatchedObservationEvent] = []
        unmatched_observed: list[GameplayObservation] = []
        unmatched_simulated: list[GameplayObservation] = []

        signatures = sorted(
            set(observed_buckets) | set(simulated_buckets),
            key=self._signature_sort_key,
        )
        for signature in signatures:
            observed_bucket = observed_buckets.get(signature, [])
            simulated_bucket = simulated_buckets.get(signature, [])
            self._sort_events(observed_bucket)
            self._sort_events(simulated_bucket)
            pair_count = min(len(observed_bucket), len(simulated_bucket))

            for index in range(pair_count):
                observed_event = observed_bucket[index]
                simulated_event = simulated_bucket[index]
                if (
                    observed_event.numeric_value is not None
                    and simulated_event.numeric_value is not None
                ):
                    numeric_delta = simulated_event.numeric_value - observed_event.numeric_value
                else:
                    numeric_delta = None
                matched.append(
                    MatchedObservationEvent(
                        signature=signature,
                        observed=observed_event,
                        simulated=simulated_event,
                        game_minute_delta=(
                            simulated_event.game_time.representative_ordinal_minute
                            - observed_event.game_time.representative_ordinal_minute
                        ),
                        numeric_delta=numeric_delta,
                    )
                )

            unmatched_observed.extend(observed_bucket[pair_count:])
            unmatched_simulated.extend(simulated_bucket[pair_count:])

        matched.sort(
            key=lambda item: (
                item.observed.game_time.representative_ordinal_minute,
                item.observed.sequence,
                item.signature.kind.value,
            )
        )
        unmatched_observed.sort(
            key=lambda item: (item.game_time.representative_ordinal_minute, item.sequence)
        )
        unmatched_simulated.sort(
            key=lambda item: (item.game_time.representative_ordinal_minute, item.sequence)
        )

        return ObservationTimelineComparison(
            observed_source_id=observed.source_id,
            simulated_source_id=simulated.source_id,
            coverage=coverage,
            identity_mapping=identity_mapping,
            kind_counts=kind_counts,
            matched=tuple(matched),
            unmatched_observed=tuple(unmatched_observed),
            unmatched_simulated=tuple(unmatched_simulated),
        )
