import unittest

from conveni_sim.staff import StaffCondition
from conveni_sim.staff_rest_recovery import (
    CONFIRMED_REST_BASE_RECOVERY,
    CONFIRMED_REST_BONUS_RECOVERY,
    EvidenceBackedIntervalRestPolicy,
    EvidenceBackedRestRecoveryResolver,
)
from conveni_sim.staff_rest_timing import StaffRestTimingContext, StaffRestTimingCoordinator
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class FixedBonusPolicy:
    def __init__(self, value):
        self.value = value
        self.contexts = []

    def bonus_applies(self, context):
        self.contexts.append(context)
        return self.value


def resting_context(*, current=10, started=0):
    return StaffRestTimingContext(
        staff_id="s1",
        condition=StaffCondition.RESTING,
        started_at_absolute_minute=started,
        current_absolute_minute=current,
        elapsed_game_minutes=current - started,
        break_room_target_id="break-room",
        stamina_current=1,
        stamina_max=10,
    )


class StaffRestRecoveryTests(unittest.TestCase):
    def test_recovered_amount_is_one_without_bonus_and_two_with_bonus(self):
        resolver = EvidenceBackedRestRecoveryResolver()

        without_bonus = resolver.resolve(resting_context(), FixedBonusPolicy(False))
        with_bonus = resolver.resolve(resting_context(), FixedBonusPolicy(True))

        self.assertEqual(CONFIRMED_REST_BASE_RECOVERY, 1)
        self.assertEqual(CONFIRMED_REST_BONUS_RECOVERY, 1)
        self.assertEqual(without_bonus.exact_recovery_amount, 1)
        self.assertEqual(with_bonus.exact_recovery_amount, 2)

    def test_unknown_bonus_decision_keeps_exact_amount_unresolved(self):
        result = EvidenceBackedRestRecoveryResolver().resolve(
            resting_context(),
            FixedBonusPolicy(None),
        )

        self.assertEqual(result.base_amount, 1)
        self.assertIsNone(result.bonus_applies)
        self.assertIsNone(result.exact_recovery_amount)

    def test_interval_and_return_timing_remain_explicit_inputs(self):
        policy = EvidenceBackedIntervalRestPolicy(
            return_game_minutes=3,
            recovery_interval_game_minutes=5,
            bonus_policy=FixedBonusPolicy(False),
        )
        returning = StaffRestTimingContext(
            staff_id="s1",
            condition=StaffCondition.RETURNING_TO_BREAK_ROOM,
            started_at_absolute_minute=10,
            current_absolute_minute=12,
            elapsed_game_minutes=2,
            break_room_target_id="break-room",
            stamina_current=0,
            stamina_max=10,
        )

        self.assertIsNone(policy.transition(returning))

        arrived = StaffRestTimingContext(
            staff_id="s1",
            condition=StaffCondition.RETURNING_TO_BREAK_ROOM,
            started_at_absolute_minute=10,
            current_absolute_minute=13,
            elapsed_game_minutes=3,
            break_room_target_id="break-room",
            stamina_current=0,
            stamina_max=10,
        )
        self.assertTrue(policy.transition(arrived).arrive_at_break_room)

        self.assertIsNone(policy.transition(resting_context(current=17, started=13)))
        recovery = policy.transition(resting_context(current=18, started=13))
        self.assertEqual(recovery.recovery_amount, 1)

    def test_unresolved_bonus_does_not_consume_an_eligible_recovery_tick(self):
        bonus = FixedBonusPolicy(None)
        policy = EvidenceBackedIntervalRestPolicy(
            return_game_minutes=0,
            recovery_interval_game_minutes=5,
            bonus_policy=bonus,
        )

        self.assertIsNone(policy.transition(resting_context(current=5, started=0)))
        bonus.value = True
        decision = policy.transition(resting_context(current=6, started=0))

        self.assertEqual(decision.recovery_amount, 2)

    def test_policy_drives_existing_roster_rest_state_machine_without_extra_constants(self):
        runtime = StoreRuntimeHarness(StoreGrid(2, 2), initial_cash_yen=1_000)
        runtime.staff.add_staff("s1", stamina_max=2)
        runtime.staff.consume_stamina("s1", 2, break_room_target_id="break-room")
        timing = StaffRestTimingCoordinator(runtime)
        policy = EvidenceBackedIntervalRestPolicy(
            return_game_minutes=0,
            recovery_interval_game_minutes=1,
            bonus_policy=FixedBonusPolicy(False),
        )

        timing.sync_from_roster()
        arrival = timing.evaluate_all(policy)[0]
        self.assertEqual(arrival.stamina_after, 0)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RESTING)

        runtime.advance_game_minutes(1)
        first = timing.evaluate_all(policy)[0]
        self.assertEqual(first.stamina_after, 1)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RESTING)

        runtime.advance_game_minutes(1)
        second = timing.evaluate_all(policy)[0]
        self.assertEqual(second.stamina_after, 2)
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.AVAILABLE)


if __name__ == "__main__":
    unittest.main()
