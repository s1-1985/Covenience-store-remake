import unittest

from conveni_sim.staff import StaffCondition, StaffTask, StoreStaffRoster
from conveni_sim.staff_task_policy import (
    ScriptedStaffTaskPolicy,
    StaffTaskCandidate,
    StaffTaskDecision,
    StaffTaskPolicyCoordinator,
)


class StaffTaskPolicyCoordinatorTests(unittest.TestCase):
    def test_scripted_policy_applies_only_supplied_candidate(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        coordinator = StaffTaskPolicyCoordinator(roster)
        policy = ScriptedStaffTaskPolicy(
            {"s1": StaffTaskDecision(StaffTask.REPLENISH, "shelf-a")}
        )

        result = coordinator.apply_policy(
            policy,
            {
                "s1": (
                    StaffTaskCandidate(StaffTask.CHECKOUT, "register-a"),
                    StaffTaskCandidate(StaffTask.REPLENISH, "shelf-a"),
                )
            },
        )

        self.assertEqual(len(result.applied), 1)
        self.assertEqual(roster.staff_member("s1").task, StaffTask.REPLENISH)
        self.assertEqual(roster.staff_member("s1").target_id, "shelf-a")

    def test_policy_may_choose_no_task_even_when_checkout_is_candidate(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        coordinator = StaffTaskPolicyCoordinator(roster)
        policy = ScriptedStaffTaskPolicy({})

        result = coordinator.apply_policy(
            policy,
            {"s1": (StaffTaskCandidate(StaffTask.CHECKOUT, "register-a"),)},
        )

        self.assertEqual(result.applied, ())
        self.assertEqual(result.no_decision_staff_ids, ("s1",))
        self.assertEqual(roster.staff_member("s1").task, StaffTask.IDLE)

    def test_two_staff_can_independently_choose_same_checkout_target(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        roster.add_staff("s2")
        coordinator = StaffTaskPolicyCoordinator(roster)
        decision = StaffTaskDecision(StaffTask.CHECKOUT, "register-a")
        policy = ScriptedStaffTaskPolicy({"s1": decision, "s2": decision})
        candidates = (StaffTaskCandidate(StaffTask.CHECKOUT, "register-a"),)

        result = coordinator.apply_policy(
            policy,
            {"s1": candidates, "s2": candidates},
        )

        self.assertEqual(tuple(item.staff_id for item in result.applied), ("s1", "s2"))
        self.assertEqual(roster.staff_member("s1").target_id, "register-a")
        self.assertEqual(roster.staff_member("s2").target_id, "register-a")

    def test_resting_staff_is_not_asked_to_take_work(self):
        roster = StoreStaffRoster()
        staff = roster.add_staff("s1", stamina_max=1)
        roster.consume_stamina("s1", 1, break_room_target_id="break")
        roster.arrive_at_break_room("s1")
        self.assertEqual(staff.condition, StaffCondition.RESTING)
        coordinator = StaffTaskPolicyCoordinator(roster)
        policy = ScriptedStaffTaskPolicy(
            {"s1": StaffTaskDecision(StaffTask.CHECKOUT, "register-a")}
        )

        result = coordinator.apply_policy(
            policy,
            {"s1": (StaffTaskCandidate(StaffTask.CHECKOUT, "register-a"),)},
        )

        self.assertEqual(result.unavailable_staff_ids, ("s1",))
        self.assertEqual(staff.task, StaffTask.REST)

    def test_policy_cannot_select_unsupplied_candidate(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        coordinator = StaffTaskPolicyCoordinator(roster)
        policy = ScriptedStaffTaskPolicy(
            {"s1": StaffTaskDecision(StaffTask.CLEAN, "floor-a")}
        )

        with self.assertRaises(ValueError):
            coordinator.apply_policy(
                policy,
                {"s1": (StaffTaskCandidate(StaffTask.CHECKOUT, "register-a"),)},
            )

    def test_candidate_layer_does_not_accept_rest_as_policy_work(self):
        with self.assertRaises(ValueError):
            StaffTaskCandidate(StaffTask.REST, "break")
        with self.assertRaises(ValueError):
            StaffTaskDecision(StaffTask.REST, "break")


if __name__ == "__main__":
    unittest.main()
