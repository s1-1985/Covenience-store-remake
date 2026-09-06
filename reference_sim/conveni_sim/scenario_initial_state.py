from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .rival import RivalChainRuntime, RivalStoreRole


class FirstTitlePlatform(str, Enum):
    PLAYSTATION = "playstation"
    SEGA_SATURN = "sega_saturn"


class FirstTitleScenario(str, Enum):
    BEGINNER = "beginner"
    MIDDLE = "middle"
    ADVANCED = "advanced"


@dataclass(frozen=True)
class RivalTopologyEvidence:
    """Evidence-safe constraints for a scenario's initial rival topology.

    exact_roles is None when the total store count or complete role set is not
    recovered. required_roles contains only roles that direct evidence says must
    be present. Unknown platform/scenario combinations deliberately impose no
    topology constraint.
    """

    platform: FirstTitlePlatform
    scenario: FirstTitleScenario
    exact_roles: Optional[tuple[RivalStoreRole, ...]] = None
    required_roles: tuple[RivalStoreRole, ...] = ()
    revision: Optional[str] = None

    @property
    def exact_store_count(self) -> Optional[int]:
        return None if self.exact_roles is None else len(self.exact_roles)


@dataclass(frozen=True)
class RivalStoreSeed:
    """Caller-supplied concrete rival store needed to build runtime state."""

    store_id: str
    role: RivalStoreRole
    location_id: str

    def __post_init__(self) -> None:
        if not self.store_id:
            raise ValueError("store_id must be non-empty")
        if not self.location_id:
            raise ValueError("location_id must be non-empty")


_PS_TOPOLOGY: dict[FirstTitleScenario, RivalTopologyEvidence] = {
    FirstTitleScenario.BEGINNER: RivalTopologyEvidence(
        platform=FirstTitlePlatform.PLAYSTATION,
        scenario=FirstTitleScenario.BEGINNER,
        exact_roles=None,
        required_roles=(RivalStoreRole.BRANCH,),
        revision=None,
    ),
    FirstTitleScenario.MIDDLE: RivalTopologyEvidence(
        platform=FirstTitlePlatform.PLAYSTATION,
        scenario=FirstTitleScenario.MIDDLE,
        exact_roles=(
            RivalStoreRole.HEADQUARTERS,
            RivalStoreRole.BRANCH,
            RivalStoreRole.BRANCH,
        ),
        revision=None,
    ),
    FirstTitleScenario.ADVANCED: RivalTopologyEvidence(
        platform=FirstTitlePlatform.PLAYSTATION,
        scenario=FirstTitleScenario.ADVANCED,
        exact_roles=(RivalStoreRole.HEADQUARTERS,),
        revision=None,
    ),
}


def rival_topology_evidence(
    platform: FirstTitlePlatform,
    scenario: FirstTitleScenario,
) -> RivalTopologyEvidence:
    """Return recovered topology constraints without promoting PS evidence to SS."""

    if platform is FirstTitlePlatform.PLAYSTATION:
        return _PS_TOPOLOGY[scenario]
    return RivalTopologyEvidence(platform=platform, scenario=scenario)


def _role_counts(roles: tuple[RivalStoreRole, ...]) -> Counter[RivalStoreRole]:
    return Counter(roles)


def validate_rival_seeds(
    evidence: RivalTopologyEvidence,
    seeds: tuple[RivalStoreSeed, ...],
) -> None:
    """Validate only topology facts recovered for the selected platform/scenario."""

    roles = tuple(seed.role for seed in seeds)
    if evidence.exact_roles is not None and _role_counts(roles) != _role_counts(evidence.exact_roles):
        raise ValueError(
            "initial rival topology does not match recovered exact role counts"
        )

    available = _role_counts(roles)
    required = _role_counts(evidence.required_roles)
    for role, count in required.items():
        if available[role] < count:
            raise ValueError(
                f"initial rival topology is missing required role {role.value!r}"
            )


def build_rival_chain_from_scenario_seeds(
    rival_id: str,
    *,
    evidence: RivalTopologyEvidence,
    seeds: tuple[RivalStoreSeed, ...],
    source: str = "scenario initial state",
) -> RivalChainRuntime:
    """Create concrete runtime state only from caller-supplied IDs and locations.

    Research currently recovers role/count topology for some PS scenarios but
    not exact coordinates or store IDs. Those unknowns remain caller/data input;
    this helper never manufactures placeholder locations that could leak into
    later simulation logic.
    """

    validate_rival_seeds(evidence, seeds)
    chain = RivalChainRuntime(rival_id)
    for seed in seeds:
        chain.open_store(
            seed.store_id,
            role=seed.role,
            location_id=seed.location_id,
            source=source,
        )
    return chain
