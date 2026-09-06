"""ランダム操作列に対する不変条件テスト。

決まったシードでランダムな操作列を生成し、**どの操作の後でも**壊れてはいけない
性質だけを検証する。個別の機能テストと違い、「想定していなかった操作の組み合わせ」で
状態が壊れることを捕まえるのが目的。

シードは固定なので結果は再現可能。失敗時はメッセージに seed と step が出るので、
その値で `fuzz` ヘルパーを単体で回せば同じ状況を再現できる。

初回作成時(コミット 65ca28c)は、round1 400シード/round3 150シード/round4 400シードの
広い探索でも違反ゼロだった。ここに残しているのは今後の変更に対する回帰検出のため。
"""

import random
import unittest
from collections import Counter

from conveni_sim.clock import RepresentativeDayType, SimulationClock
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.economy import BankruptcyPolicy, CashDirection, FinancialEventKind
from conveni_sim.month_cycle import RepresentativeMonthRecorder
from conveni_sim.operating_time import OperatingHours
from conveni_sim.staff import StaffCondition, StaffSkill, StaffTask, StoreStaffRoster
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness

TERMINAL_STATES = (CustomerState.EXITED, CustomerState.EJECTED)


class StoreRuntimeInvariantTests(unittest.TestCase):
    """ランダムな店舗操作の後でも常に成り立つべき性質。"""

    SEEDS = range(40)
    STEPS = 120

    def build_store(self, rng):
        grid = StoreGrid(rng.randint(5, 7), rng.randint(5, 7))
        width, height = grid.width_subcells, grid.height_subcells
        shelves = []
        for index in range(rng.randint(1, 2)):
            for _ in range(15):
                try:
                    grid.place_fixture(
                        instance_id=f"shelf{index}",
                        fixture_id="synthetic_shelf",
                        origin_subcell=GridPoint(
                            rng.randrange(2, width - 2), rng.randrange(2, height - 2)
                        ),
                        footprint_tiles=(1, 1),
                        interaction_side=rng.choice(list(Direction)),
                    )
                    shelves.append(f"shelf{index}")
                    break
                except Exception:
                    continue
        for _ in range(15):
            try:
                grid.place_fixture(
                    instance_id="checkout",
                    fixture_id="synthetic_checkout",
                    origin_subcell=GridPoint(
                        rng.randrange(2, width - 2), rng.randrange(2, height - 2)
                    ),
                    footprint_tiles=(1, 1),
                    interaction_side=rng.choice(list(Direction)),
                )
                break
            except Exception:
                continue
        return grid, shelves

    def assert_invariants(self, runtime, seen_states, settled_baskets, *, seed, step):
        where = f"seed={seed} step={step}"

        positions = Counter(agent.position for agent in runtime.traffic.agents)
        collisions = [point for point, count in positions.items() if count > 1]
        self.assertEqual(collisions, [], f"two agents share a cell ({where})")

        for slot in runtime.inventory.slots:
            self.assertGreaterEqual(slot.units, 0, f"{slot.id} negative stock ({where})")
            self.assertLessEqual(
                slot.units, slot.capacity_units, f"{slot.id} over capacity ({where})"
            )

        balance = runtime.cash.initial_cash_yen
        for event in runtime.cash.events:
            if event.amount_yen is None:
                continue
            if event.direction is CashDirection.CREDIT:
                balance += event.amount_yen
            else:
                balance -= event.amount_yen
        self.assertEqual(
            balance, runtime.cash.known_cash_yen, f"ledger drifted from its events ({where})"
        )

        for session in runtime.customers.customers:
            planned = len(session.planned_merchandise_fixture_ids)
            self.assertLessEqual(
                session.next_merchandise_index, planned, f"{session.id} route overrun ({where})"
            )
            self.assertLessEqual(
                len(session.interacted_fixture_ids),
                planned,
                f"{session.id} interacted with more fixtures than planned ({where})",
            )

        served_anywhere = []
        for fixture_id in runtime.checkout_fixture_ids:
            checkout = runtime.checkout(fixture_id)
            active = checkout.active_services
            self.assertLessEqual(
                len(active),
                checkout.simultaneous_staff_capacity,
                f"{fixture_id} exceeded its service capacity ({where})",
            )
            served = [record.customer_id for record in active]
            self.assertEqual(
                len(served), len(set(served)), f"{fixture_id} serves a customer twice ({where})"
            )
            served_anywhere.extend(served)
        self.assertEqual(
            len(served_anywhere),
            len(set(served_anywhere)),
            f"a customer is served at two checkouts ({where})",
        )

        for customer_id, previous in seen_states.items():
            current = runtime.customers.customer(customer_id).state
            if previous in TERMINAL_STATES:
                self.assertIn(
                    current,
                    TERMINAL_STATES,
                    f"{customer_id} left a terminal state ({where})",
                )

        for customer_id, line_count in settled_baskets.items():
            basket = runtime.purchases.basket(customer_id)
            self.assertEqual(
                len(basket.lines),
                line_count,
                f"settled basket {customer_id} changed ({where})",
            )

    def test_random_operations_preserve_runtime_invariants(self):
        for seed in self.SEEDS:
            rng = random.Random(seed)
            grid, shelves = self.build_store(rng)
            placed = {placement.instance_id for placement in grid.placements}
            if not shelves or "checkout" not in placed:
                continue

            runtime = StoreRuntimeHarness(
                grid,
                initial_cash_yen=1_000_000,
                operating_hours=OperatingHours.twenty_four_hours(),
            )
            runtime.add_checkout("checkout", simultaneous_staff_capacity=rng.randint(1, 2))
            slot_ids = []
            for index, shelf in enumerate(shelves):
                slot_id = f"slot{index}"
                runtime.inventory.add_slot(
                    slot_id,
                    fixture_id=shelf,
                    product_id=f"product{index}",
                    capacity_units=8,
                    initial_units=rng.randint(0, 5),
                    unit_procurement_cost_yen=rng.choice([None, 60]),
                )
                slot_ids.append(slot_id)
            for index in range(rng.randint(1, 3)):
                runtime.staff.add_staff(f"s{index}", stamina_max=rng.choice([None, 20]))

            walkable = [
                GridPoint(x, y)
                for x in range(grid.width_subcells)
                for y in range(grid.height_subcells)
                if grid.is_walkable(GridPoint(x, y))
            ]
            if len(walkable) < 4:
                continue

            checkout = runtime.checkout("checkout")
            seen_states = {}
            settled_baskets = {}
            next_customer = 0

            for step in range(self.STEPS):
                roll = rng.random()
                try:
                    if roll < 0.2 and next_customer < 7:
                        free = [
                            point
                            for point in walkable
                            if all(agent.position != point for agent in runtime.traffic.agents)
                        ]
                        if len(free) >= 2:
                            entry, exit_point = rng.sample(free, 2)
                            customer_id = f"c{next_customer}"
                            next_customer += 1
                            runtime.add_customer(
                                customer_id,
                                entry_point=entry,
                                exit_point=exit_point,
                                merchandise_fixture_ids=tuple(shelves),
                                checkout_fixture_id=rng.choice([None, "checkout"]),
                            )
                    elif roll < 0.52:
                        runtime.customers.tick()
                        runtime.advance_game_minutes(rng.randint(0, 5))
                    elif roll < 0.68:
                        ready = [
                            session
                            for session in runtime.customers.customers
                            if session.state is CustomerState.AT_MERCHANDISE
                        ]
                        if ready:
                            session = rng.choice(ready)
                            options = [
                                slot
                                for slot in runtime.inventory.slots
                                if slot.fixture_id == session.current_merchandise_fixture_id
                                and slot.units > 0
                            ]
                            if options and rng.random() < 0.8:
                                slot = rng.choice(options)
                                flow = (
                                    PurchaseFlow.CHECKOUT_REQUIRED
                                    if session.checkout_fixture_id
                                    else PurchaseFlow.SELF_SERVICE_CANDIDATE
                                )
                                runtime.customer_pick_and_continue(
                                    session.id,
                                    slot.id,
                                    quantity=1,
                                    unit_sale_price_yen=rng.choice([None, 120]),
                                    flow=flow,
                                )
                            else:
                                runtime.customer_skip_and_continue(session.id)
                    elif roll < 0.78:
                        waiting = checkout.refresh_waiting()
                        idle = [
                            state.id
                            for state in runtime.staff.staff
                            if state.condition is StaffCondition.AVAILABLE
                            and checkout.customer_being_served_by(state.id) is None
                            and state.task in (StaffTask.IDLE, StaffTask.CHECKOUT)
                        ]
                        if waiting and idle:
                            runtime.begin_checkout_service(
                                "checkout",
                                staff_id=rng.choice(idle),
                                customer_id=rng.choice(waiting),
                            )
                    elif roll < 0.88:
                        busy = [
                            state.id
                            for state in runtime.staff.staff
                            if checkout.customer_being_served_by(state.id)
                        ]
                        if busy:
                            staff_id = rng.choice(busy)
                            customer_id = checkout.customer_being_served_by(staff_id)
                            runtime.finish_checkout_sale("checkout", staff_id=staff_id)
                            settled_baskets[customer_id] = len(
                                runtime.purchases.basket(customer_id).lines
                            )
                    elif roll < 0.94:
                        candidates = [
                            session
                            for session in runtime.customers.customers
                            if not session.requires_checkout
                            and runtime.purchases.basket(session.id).lines
                            and not runtime.purchases.basket(session.id).settled
                        ]
                        if candidates:
                            chosen = rng.choice(candidates)
                            runtime.settle_self_service(chosen.id)
                            settled_baskets[chosen.id] = len(
                                runtime.purchases.basket(chosen.id).lines
                            )
                    else:
                        slot = runtime.inventory.slot(rng.choice(slot_ids))
                        if slot.free_capacity > 0:
                            runtime.replenish_and_charge(
                                slot.id, rng.randint(1, slot.free_capacity)
                            )
                except (ValueError, KeyError, RuntimeError):
                    # 拒否された操作自体は正常。不変条件は壊れていてはいけない。
                    pass

                for session in runtime.customers.customers:
                    seen_states[session.id] = session.state
                self.assert_invariants(
                    runtime, seen_states, settled_baskets, seed=seed, step=step
                )


class CalendarInvariantTests(unittest.TestCase):
    """4日represent月を長期間回したときのカレンダー/台帳の整合性。"""

    def test_long_calendar_loop_stays_consistent(self):
        for seed in range(12):
            rng = random.Random(seed)
            grid = StoreGrid(5, 5)
            grid.place_fixture(
                instance_id="checkout",
                fixture_id="synthetic_checkout",
                origin_subcell=GridPoint(6, 4),
                footprint_tiles=(1, 1),
                interaction_side=Direction.NORTH,
            )
            runtime = StoreRuntimeHarness(
                grid,
                initial_cash_yen=200_000_000,
                operating_hours=OperatingHours.twenty_four_hours(),
                bankruptcy_policy=BankruptcyPolicy(check_negative_cash_at_end_of_day=True),
            )
            recorder = RepresentativeMonthRecorder(SimulationClock())
            months = 14
            samples = []

            for _ in range(months):
                for _day in range(4):
                    day = recorder.clock.day
                    expected_type = (
                        RepresentativeDayType.HOLIDAY
                        if day == 4
                        else RepresentativeDayType.WEEKDAY
                    )
                    self.assertIs(
                        recorder.clock.representative_day_type,
                        expected_type,
                        f"day {day} has the wrong representative type (seed={seed})",
                    )
                    runtime.advance_game_minutes(60 * rng.choice([4, 6, 8]))
                    runtime.cash.record_sale(rng.randint(0, 50_000), source_id="daily")
                    runtime.cash.record_cost(
                        FinancialEventKind.LABOR, rng.randint(0, 30_000)
                    )
                    sample = recorder.close_representative_day(runtime.close_day())
                    if sample is not None:
                        samples.append(sample)

            self.assertEqual(len(samples), months, f"month sample count (seed={seed})")
            for sample in samples:
                self.assertEqual(
                    sample.representative_days, (1, 2, 3, 4), f"month days (seed={seed})"
                )
                self.assertTrue(sample.complete_four_day_sample)
                self.assertEqual(len(sample.weekday_records), 3)
                self.assertEqual(len(sample.holiday_records), 1)

            keys = [(sample.year, sample.month) for sample in samples]
            self.assertEqual(len(keys), len(set(keys)), f"duplicate month (seed={seed})")
            for previous, following in zip(keys, keys[1:]):
                year, month = previous
                expected = (year + 1, 1) if month == 12 else (year, month + 1)
                self.assertEqual(
                    following, expected, f"month did not advance (seed={seed})"
                )

            balance = runtime.cash.initial_cash_yen
            for event in runtime.cash.events:
                if event.amount_yen is None:
                    continue
                if event.direction is CashDirection.CREDIT:
                    balance += event.amount_yen
                else:
                    balance -= event.amount_yen
            self.assertEqual(
                balance, runtime.cash.known_cash_yen, f"ledger drift (seed={seed})"
            )


class StaffStateMachineInvariantTests(unittest.TestCase):
    """スタミナ/成長機会の状態機械が、ランダムな順序でも破綻しないこと。"""

    def test_stamina_and_growth_state_machine_holds(self):
        for seed in range(60):
            rng = random.Random(seed)
            roster = StoreStaffRoster()
            stamina_max = rng.randint(1, 40)
            roster.add_staff(
                "s1",
                stamina_max=stamina_max,
                runtime_skills={StaffSkill.REGISTER: rng.randint(0, 5)},
                base_skill_caps={StaffSkill.REGISTER: rng.randint(5, 20)},
            )
            roster.add_staff(
                "mgr", manager=True, runtime_skills={StaffSkill.EDUCATION: rng.randint(0, 100)}
            )
            state = roster.staff_member("s1")

            for step in range(120):
                roll = rng.random()
                where = f"seed={seed} step={step}"
                if roll < 0.34 and state.condition is StaffCondition.AVAILABLE:
                    roster.record_completed_work(
                        "s1",
                        rng.choice(
                            [StaffTask.CHECKOUT, StaffTask.REPLENISH, StaffTask.CLEAN]
                        ),
                        stamina_cost=rng.choice([None, rng.randint(0, stamina_max)]),
                        break_room_target_id="break-room",
                    )
                elif roll < 0.5 and state.condition is StaffCondition.RETURNING_TO_BREAK_ROOM:
                    roster.arrive_at_break_room("s1", break_room_target_id="break-room")
                elif roll < 0.7 and state.condition is StaffCondition.RESTING:
                    roster.recover_stamina("s1", rng.randint(1, stamina_max))
                elif roll < 0.85:
                    unresolved = roster.unresolved_growth_opportunities
                    if unresolved:
                        opportunity = rng.choice(unresolved)
                        low = opportunity.before_value or 0
                        high = opportunity.base_cap if opportunity.base_cap is not None else low + 5
                        if low <= high:
                            roster.resolve_growth_opportunity(
                                opportunity.sequence, after_value=rng.randint(low, high)
                            )

                self.assertGreaterEqual(state.stamina_current, 0, f"stamina < 0 ({where})")
                self.assertLessEqual(
                    state.stamina_current, stamina_max, f"stamina > max ({where})"
                )
                if state.condition is StaffCondition.RESTING:
                    self.assertIs(state.task, StaffTask.REST, f"resting task ({where})")
                if state.stamina_current == 0:
                    self.assertIsNot(
                        state.condition,
                        StaffCondition.AVAILABLE,
                        f"exhausted staff still available ({where})",
                    )
                for opportunity in roster.growth_opportunities:
                    if not opportunity.resolved:
                        continue
                    if opportunity.before_value is not None:
                        self.assertGreaterEqual(
                            opportunity.resolved_after,
                            opportunity.before_value,
                            f"growth reduced a skill ({where})",
                        )
                    if opportunity.base_cap is not None:
                        self.assertLessEqual(
                            opportunity.resolved_after,
                            opportunity.base_cap,
                            f"growth exceeded the cap ({where})",
                        )


if __name__ == "__main__":
    unittest.main()
