from __future__ import annotations

from typing import Optional

from .baseline_data import SCENARIOS
from .models import ScenarioDefinition
from .rival import RivalChainRuntime, RivalStoreRole

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# `ScenarioDefinition.initial_rival_store_roles`/`initial_rival_branch_exists`
# (baseline_data.SCENARIOS) are CONFIRMED_COMMUNITY: docs/research/scenario-
# initial-rival-topology-2026-09-06.md's PS long-play records state, for
# intermediate and advanced, the exact initial rival role composition
# (headquarters/branch count and order). This module turns that confirmed
# composition into a populated `RivalChainRuntime` so a caller does not have
# to re-derive the `open_store()` call sequence itself.
#
# What is NOT confirmed, and is therefore this module's own
# REMAKE_BALANCED_DEFAULT choice: the `location_id` string each seeded store
# is given. `RivalChainRuntime.open_store()` requires one, but no source
# states where these initial rival stores actually sit -- the research doc
# explicitly lists exact coordinates as UNKNOWN (section 1: "3店舗の正確な
# 座標", section 2: "上級開始時ライバル本店の正確な座標"). The placeholder
# ids below (`f"{scenario_id}_seed_{n}"`) are opaque bookkeeping keys, not a
# claim about where on the town map the store sits -- `rival.py`'s own
# `location_id: str` field was already designed as an opaque key rather than
# a spatial position (see `remake_town_spatial.py` for the actual
# position-based module, which this does not touch).
#
# Beginner is deliberately NOT seeded here: the research doc confirms only
# that a rival branch exists, not the total store count or role order
# (section 4), so there is nothing to build the count from without guessing.


def _scenario(scenario_id: str) -> ScenarioDefinition:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"unknown scenario_id: {scenario_id}")


def seed_rival_chain_for_scenario(scenario_id: str) -> Optional[RivalChainRuntime]:
    """Build a `RivalChainRuntime` pre-populated with `scenario_id`'s
    CONFIRMED_COMMUNITY initial rival role composition (see module
    docstring). Returns None when the scenario has no confirmed role-order
    topology to build from (currently: "beginner")."""

    scenario = _scenario(scenario_id)
    roles_field = scenario.initial_rival_store_roles
    if roles_field is None:
        return None

    runtime = RivalChainRuntime(f"{scenario_id}_rival_chain")
    for index, role_name in enumerate(roles_field.value, start=1):
        role = RivalStoreRole(role_name)
        runtime.open_store(
            f"{scenario_id}_rival_{index}",
            role=role,
            location_id=f"{scenario_id}_seed_{index}",
            source=roles_field.source,
        )
    return runtime
