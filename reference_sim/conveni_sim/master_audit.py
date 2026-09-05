from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from .models import (
    CustomerArchetypeDefinition,
    EvidenceValue,
    FixtureDefinition,
    ProductDefinition,
    StaffDefinition,
)


FIXTURE_IMPLEMENTATION_FIELDS = (
    "footprint",
    "purchase_price_yen",
    "maintenance_yen_per_day",
    "capacity",
    "compatible_product_categories",
    "interaction_sides",
)

PRODUCT_IMPLEMENTATION_FIELDS = (
    "category",
    "procurement_cost_yen",
    "standard_retail_price_yen",
    "compatible_fixture_ids",
)

CUSTOMER_ARCHETYPE_RESEARCH_FIELDS = (
    "origin_building_affinities",
    "spending_power_profile",
    "preferred_primary_products",
    "preferred_add_on_products",
    "patience_profile",
)

STAFF_IMPLEMENTATION_FIELDS = (
    "salary_yen_per_day_24h",
    "stamina",
    "academic_background",
    "agility",
    "sociability",
    "education",
    "register_skill",
    "replenishment_skill",
    "security_skill",
    "cleaning_skill",
    "service_skill",
)


@dataclass(frozen=True)
class MasterAuditResult:
    record_id: str
    required_fields: tuple[str, ...]
    known_fields: tuple[str, ...]
    unknown_fields: tuple[str, ...]

    @property
    def completion_ratio(self) -> float:
        if not self.required_fields:
            return 1.0
        return len(self.known_fields) / len(self.required_fields)

    @property
    def complete(self) -> bool:
        return not self.unknown_fields


def audit_record(record: Any, required_fields: Sequence[str]) -> MasterAuditResult:
    known: list[str] = []
    unknown: list[str] = []

    for field_name in required_fields:
        if not hasattr(record, field_name):
            raise AttributeError(f"{type(record).__name__} has no field {field_name!r}")
        value = getattr(record, field_name)
        if value is None:
            unknown.append(field_name)
            continue
        if not isinstance(value, EvidenceValue):
            raise TypeError(
                f"{type(record).__name__}.{field_name} must be EvidenceValue or None, "
                f"got {type(value).__name__}"
            )
        known.append(field_name)

    return MasterAuditResult(
        record_id=record.id,
        required_fields=tuple(required_fields),
        known_fields=tuple(known),
        unknown_fields=tuple(unknown),
    )


def audit_fixture(record: FixtureDefinition) -> MasterAuditResult:
    return audit_record(record, FIXTURE_IMPLEMENTATION_FIELDS)


def audit_product(record: ProductDefinition) -> MasterAuditResult:
    return audit_record(record, PRODUCT_IMPLEMENTATION_FIELDS)


def audit_customer_archetype(record: CustomerArchetypeDefinition) -> MasterAuditResult:
    return audit_record(record, CUSTOMER_ARCHETYPE_RESEARCH_FIELDS)


def audit_staff(record: StaffDefinition) -> MasterAuditResult:
    return audit_record(record, STAFF_IMPLEMENTATION_FIELDS)


def aggregate_completion(results: Iterable[MasterAuditResult]) -> float:
    results = tuple(results)
    total_fields = sum(len(result.required_fields) for result in results)
    if total_fields == 0:
        return 1.0
    known_fields = sum(len(result.known_fields) for result in results)
    return known_fields / total_fields
