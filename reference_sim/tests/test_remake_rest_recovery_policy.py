import random
import unittest

from conveni_sim.remake_rest_recovery_policy import RemakeBalancedRestRecoveryBonusPolicy
from conveni_sim.staff import StaffCondition
from conveni_sim.staff_rest_timing import StaffRestTimingContext


def make_context(staff_id="s1"):
    return StaffRestTimingContext(
        staff_id=staff_id,
        condition=StaffCondition.RESTING,
        started_at_absolute_minute=0,
        current_absolute_minute=10,
        elapsed_game_minutes=10,
        break_room_target_id="break-room",
        stamina_current=1,
        stamina_max=5,
    )


class RemakeRestRecoveryBonusPolicyTests(unittest.TestCase):
    def test_none_when_agility_is_unknown(self):
        policy = RemakeBalancedRestRecoveryBonusPolicy(agility_by_staff_id={})
        self.assertIsNone(policy.bonus_applies(make_context("unknown-staff")))

    def test_agility_100_always_applies(self):
        policy = RemakeBalancedRestRecoveryBonusPolicy(
            agility_by_staff_id={"s1": 100}, rng=random.Random(0)
        )
        for _ in range(20):
            self.assertTrue(policy.bonus_applies(make_context()))

    def test_agility_0_never_applies(self):
        policy = RemakeBalancedRestRecoveryBonusPolicy(
            agility_by_staff_id={"s1": 0}, rng=random.Random(0)
        )
        for _ in range(20):
            self.assertFalse(policy.bonus_applies(make_context()))

    def test_higher_agility_applies_more_often_over_many_rolls(self):
        low = RemakeBalancedRestRecoveryBonusPolicy(agility_by_staff_id={"s1": 10}, rng=random.Random(1))
        high = RemakeBalancedRestRecoveryBonusPolicy(agility_by_staff_id={"s1": 90}, rng=random.Random(1))

        low_count = sum(1 for _ in range(500) if low.bonus_applies(make_context()))
        high_count = sum(1 for _ in range(500) if high.bonus_applies(make_context()))

        self.assertLess(low_count, high_count)


if __name__ == "__main__":
    unittest.main()
