from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_service_timing import CheckoutServiceTimingCoordinator
from .clock import SimulationClock
from .customer import PurchaseFlow
from .customer_demand import CustomerDemandCoordinator
from .customer_purchase_policy import CustomerPurchaseCoordinator, MerchandiseOffer
from .operating_time import OperatingHours, SubdayClock
from .representative_day_runner import RepresentativeDayRunResult, RepresentativeDayRunner
from .scenario_policies import (
    FirstWaitingScenarioCheckoutPolicy,
    FixedScenarioCheckoutDurationPolicy,
    FixedScenarioCheckoutEffectsPolicy,
    FixedScenarioStaffWorkPolicy,
    IntervalScenarioRestPolicy,
    OrderedScenarioStaffTaskPolicy,
    PreferredOfferScenarioPurchasePolicy,
    ScheduledScenarioCustomer,
    ScheduledScenarioDemandPolicy,
)
from .staff import StaffSkill, StaffTask
from .staff_growth_resolution import EvidenceBackedStaffGrowthResolver
from .staff_rest_timing import StaffRestTimingCoordinator
from .staff_work_timing import StaffWorkTimingCoordinator
from .store_grid import Direction, GridPoint, StoreGrid
from .store_runtime import StoreRuntimeHarness
from .store_step import StoreStepOrchestrator


SCENARIO_SHELF_ID = "scenario-shelf"
SCENARIO_CHECKOUT_ID = "scenario-checkout"
SCENARIO_SLOT_ID = "scenario-slot"
SCENARIO_STAFF_ID = "scenario-staff"


@dataclass(frozen=True)
class MinimalScenarioLayout:
    width_tiles: int
    height_tiles: int
    shelf_origin_subcell: GridPoint
    shelf_footprint_tiles: tuple[int, int]
    shelf_interaction_side: Direction
    checkout_origin_subcell: GridPoint
    checkout_footprint_tiles: tuple[int, int]
    checkout_interaction_side: Direction
    entry_point: GridPoint
    exit_point: GridPoint


@dataclass(frozen=True)
class MinimalScenarioProduct:
    product_id: str
    capacity_units: int
    initial_units: int
    unit_procurement_cost_yen: Optional[int]
    unit_sale_price_yen: Optional[int]
    purchase_quantity: int

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("product_id must not be empty")
        if self.purchase_quantity <= 0:
            raise ValueError("purchase_quantity must be > 0")


@dataclass(frozen=True)
class MinimalScenarioStaff:
    stamina_max: Optional[int]
    register_skill: Optional[int]
    task_order: tuple[StaffTask, ...]
    replenishment_skill: Optional[int] = None
    replenishment_cap: Optional[int] = None
    cleaning_skill: Optional[int] = None
    cleaning_cap: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.task_order:
            raise ValueError("task_order must not be empty")


@dataclass(frozen=True)
class MinimalScenarioTiming:
    step_game_minutes: int
    checkout_game_minutes: int
    checkout_stamina_cost: Optional[int]
    replenish_game_minutes: int
    clean_game_minutes: int
    replenish_up_to_quantity: int
    replenish_stamina_cost: Optional[int]
    clean_stamina_cost: Optional[int]
    break_room_target_id: Optional[str]
    return_to_break_room_game_minutes: int
    recovery_interval_game_minutes: int
    recovery_amount: int

    def __post_init__(self) -> None:
        if self.step_game_minutes <= 0:
            raise ValueError("step_game_minutes must be > 0")


@dataclass(frozen=True)
class MinimalRepresentativeDayScenarioConfig:
    layout: MinimalScenarioLayout
    product: MinimalScenarioProduct
    staff: MinimalScenarioStaff
    timing: MinimalScenarioTiming
    arrivals: tuple[ScheduledScenarioCustomer, ...]
    initial_cash_yen: int
    operating_hours: OperatingHours
    start_hour: int
    start_minute: int
    year: int
    month: int
    day: int
    checkout_staff_capacity: int

    def __post_init__(self) -> None:
        start_minute_of_day = self.start_hour * 60 + self.start_minute
        for arrival in self.arrivals:
            if arrival.minute_of_day < start_minute_of_day:
                raise ValueError("scenario arrival cannot precede the configured start time")


@dataclass
class MinimalRepresentativeDayScenario:
    config: MinimalRepresentativeDayScenarioConfig
    runtime: StoreRuntimeHarness
    calendar: SimulationClock
    orchestrator: StoreStepOrchestrator
    runner: RepresentativeDayRunner

    def run(self) -> RepresentativeDayRunResult:
        return self.runner.run(step_game_minutes=self.config.timing.step_game_minutes)


def build_minimal_representative_day_scenario(
    config: MinimalRepresentativeDayScenarioConfig,
) -> MinimalRepresentativeDayScenario:
    """Compose one parameter-driven shelf/checkout/staff representative day.

    This is a compatibility/integration harness, not an assertion that the
    original game used these concrete fixture sizes, priorities or timing values.
    Every unresolved gameplay-sensitive numeric value is supplied by the caller.
    Replenishment/cleaning +1 growth is applied only when current values and
    normal caps are explicitly supplied because that increment is now supported
    by first-title dedicated research.
    """

    grid = StoreGrid(config.layout.width_tiles, config.layout.height_tiles)
    grid.place_fixture(
        instance_id=SCENARIO_SHELF_ID,
        fixture_id="scenario_shelf_type",
        origin_subcell=config.layout.shelf_origin_subcell,
        footprint_tiles=config.layout.shelf_footprint_tiles,
        interaction_side=config.layout.shelf_interaction_side,
    )
    grid.place_fixture(
        instance_id=SCENARIO_CHECKOUT_ID,
        fixture_id="scenario_checkout_type",
        origin_subcell=config.layout.checkout_origin_subcell,
        footprint_tiles=config.layout.checkout_footprint_tiles,
        interaction_side=config.layout.checkout_interaction_side,
    )

    runtime = StoreRuntimeHarness(
        grid,
        initial_cash_yen=config.initial_cash_yen,
        operating_hours=config.operating_hours,
        subday_clock=SubdayClock(config.start_hour, config.start_minute),
    )
    runtime.add_checkout(
        SCENARIO_CHECKOUT_ID,
        simultaneous_staff_capacity=config.checkout_staff_capacity,
    )

    runtime_skills: dict[StaffSkill, int] = {}
    base_skill_caps: dict[StaffSkill, int] = {}
    if config.staff.register_skill is not None:
        runtime_skills[StaffSkill.REGISTER] = config.staff.register_skill
    if config.staff.replenishment_skill is not None:
        runtime_skills[StaffSkill.REPLENISHMENT] = config.staff.replenishment_skill
    if config.staff.cleaning_skill is not None:
        runtime_skills[StaffSkill.CLEANING] = config.staff.cleaning_skill
    if config.staff.replenishment_cap is not None:
        base_skill_caps[StaffSkill.REPLENISHMENT] = config.staff.replenishment_cap
    if config.staff.cleaning_cap is not None:
        base_skill_caps[StaffSkill.CLEANING] = config.staff.cleaning_cap

    runtime.staff.add_staff(
        SCENARIO_STAFF_ID,
        stamina_max=config.staff.stamina_max,
        runtime_skills=runtime_skills or None,
        base_skill_caps=base_skill_caps or None,
    )
    runtime.inventory.add_slot(
        SCENARIO_SLOT_ID,
        fixture_id=SCENARIO_SHELF_ID,
        product_id=config.product.product_id,
        capacity_units=config.product.capacity_units,
        initial_units=config.product.initial_units,
        unit_procurement_cost_yen=config.product.unit_procurement_cost_yen,
    )

    demand_policy = ScheduledScenarioDemandPolicy(
        config.arrivals,
        entry_point=config.layout.entry_point,
        exit_point=config.layout.exit_point,
        merchandise_fixture_ids=(SCENARIO_SHELF_ID,),
        checkout_fixture_id=SCENARIO_CHECKOUT_ID,
    )
    demand = CustomerDemandCoordinator(runtime, demand_policy)

    purchases = CustomerPurchaseCoordinator(
        runtime,
        (
            MerchandiseOffer(
                SCENARIO_SLOT_ID,
                unit_sale_price_yen=config.product.unit_sale_price_yen,
                flow=PurchaseFlow.CHECKOUT_REQUIRED,
            ),
        ),
    )
    purchase_policy = PreferredOfferScenarioPurchasePolicy(
        (SCENARIO_SLOT_ID,),
        quantity=config.product.purchase_quantity,
    )

    checkout_timing = CheckoutServiceTimingCoordinator(runtime)
    staff_work_timing = StaffWorkTimingCoordinator(runtime)
    staff_rest_timing = StaffRestTimingCoordinator(runtime)
    staff_growth = EvidenceBackedStaffGrowthResolver(runtime.staff)

    orchestrator = StoreStepOrchestrator(
        runtime,
        demand=demand,
        purchases=purchases,
        purchase_policy=purchase_policy,
        staff_policy=OrderedScenarioStaffTaskPolicy(config.staff.task_order),
        checkout_policy=FirstWaitingScenarioCheckoutPolicy(),
        checkout_timing=checkout_timing,
        checkout_duration_policy=FixedScenarioCheckoutDurationPolicy(
            config.timing.checkout_game_minutes
        ),
        checkout_completion_effects_policy=FixedScenarioCheckoutEffectsPolicy(
            stamina_cost=config.timing.checkout_stamina_cost,
            break_room_target_id=config.timing.break_room_target_id,
        ),
        staff_work_timing=staff_work_timing,
        staff_work_completion_policy=FixedScenarioStaffWorkPolicy(
            replenish_game_minutes=config.timing.replenish_game_minutes,
            clean_game_minutes=config.timing.clean_game_minutes,
            replenish_up_to_quantity=config.timing.replenish_up_to_quantity,
            replenish_stamina_cost=config.timing.replenish_stamina_cost,
            clean_stamina_cost=config.timing.clean_stamina_cost,
            break_room_target_id=config.timing.break_room_target_id,
        ),
        staff_growth_resolver=staff_growth,
        staff_rest_timing=staff_rest_timing,
        staff_rest_transition_policy=IntervalScenarioRestPolicy(
            return_game_minutes=config.timing.return_to_break_room_game_minutes,
            recovery_interval_game_minutes=config.timing.recovery_interval_game_minutes,
            recovery_amount=config.timing.recovery_amount,
        ),
    )

    calendar = SimulationClock(config.year, config.month, config.day)
    runner = RepresentativeDayRunner(orchestrator, calendar)
    return MinimalRepresentativeDayScenario(
        config=config,
        runtime=runtime,
        calendar=calendar,
        orchestrator=orchestrator,
        runner=runner,
    )
